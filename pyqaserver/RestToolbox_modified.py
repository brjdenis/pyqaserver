# The original code
#  was modified in order to further extend its usabilty.
# Changes include: modification of the authentication procedure,
# modification of functions that are used to get data from the
# orthanc server, addition of new functions.
# The original RestToolbox code is contained in the same directory for reference.
# Denis Brojan, Ljubljana, 2017
############################################################################
#############################################################################

# Orthanc - A Lightweight, RESTful DICOM Store
# Copyright (C) 2012-2016 Sebastien Jodogne, Medical Physics
# Department, University Hospital of Liege, Belgium
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import httplib2
import json
import base64
import tempfile
import datetime
from shutil import copyfile
import os, sys
from multiprocessing.pool import ThreadPool
from urllib.parse import urlencode

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    import config
else:
    from . import config

_credentials = None
_auth = ""

def _DecodeJson(s):
    try:
        #if (sys.version_info >= (3, 0)):
        #    return json.loads(s.decode())
        #else:
        #    return json.loads(s)
        return json.loads(s.decode())
    except:
        return s

def get_datetime(instance):
    # Function to get date and time of an instance.
    # CAREFUL, datetime orders the instances for analysis
    date_var = ""
    time_var = ""
    try:
        date_var = instance["ContentDate"]
        time_var = instance["ContentTime"]
    except:
        try:
            date_var = instance["AcquisitionDate"]
            time_var = instance["AcquisitionTime"]
        except:
            try:
                date_var = instance["StudyDate"]
                time_var = instance["StudyTime"]
            except:
                date_var = "Unknown"  # Do not change, or else you will break the code!
                time_var = "Unknown"
    if date_var == "":
        date_var = "Unknown"
    if time_var == "":
        time_var = "Unknown"

    return date_var, time_var


def order_instance_datetime(instance_list):
    # This function gets instances with time stamp for further ordering

    instance_datetime = []
    instance_datetime_order = []
    epoch = datetime.datetime.utcfromtimestamp(0)
    instance_num = []
    for ii in instance_list:
        try:
            date_var, time_var = get_datetime(ii)  # Get raw from REST (Dicom)
            date_str = datetime.datetime.strptime(date_var, "%Y%m%d").strftime("%Y-%m-%d")  # To string
            try:
                time_str = datetime.datetime.strptime(time_var, "%H%M%S").strftime("%H:%M:%S")
            except:
                time_str = datetime.datetime.strptime(time_var, "%H%M%S.%f").strftime("%H:%M:%S.%f")
                time_str = time_str.split('.')[0]
            inst_datetime_temp = date_str + " " + time_str
            instance_datetime.append(inst_datetime_temp)
            #try:
            #    instance_datetime_order.append(int((datetime.datetime.strptime(inst_datetime_temp,  "%Y/%m/%d | %H:%M:%S.%f") - epoch).total_seconds()*1000))
            #except:
            instance_datetime_order.append(int((datetime.datetime.strptime(inst_datetime_temp,  "%Y-%m-%d %H:%M:%S") - epoch).total_seconds()*1000))
        except:
            instance_datetime.append("Unknown")
            instance_datetime_order.append(int((epoch - epoch).total_seconds()*1000))

        try:
            manufact = ii["Manufacturer"]
        except:
            manufact = "Undefined"

        if manufact in ["Varian Medical Systems"]:
            show_instance_label = "RTImageLabel"
        else:
            show_instance_label = "InstanceNumber"

        try:
            pp = ii[show_instance_label]
            instance_num.append(pp)
        except:
            instance_num.append("Undefined")
    return instance_datetime, instance_datetime_order, instance_num


def SetCredentials(username, password):
    global _credentials, _auth
    _credentials = (username, password)
    _auth = base64.encodebytes( (_credentials[0] + ':' + _credentials[1] ).encode())

def _SetupCredentials(h):
    global _credentials, _auth
    if _credentials != None:
        h.add_credentials(_credentials[0], _credentials[1])

def DoGet(uri, data = {}, interpretAsJson = True):
    d = ''
    if len(data.keys()) > 0:
        d = '?' + urlencode(data)

    h = httplib2.Http()
    _SetupCredentials(h)

    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization' : 'Basic ' + _auth.decode()}
    resp, content = h.request(uri + d, 'GET', headers=headers)
    h.close()
    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    elif not interpretAsJson:
        return content.decode()
    else:
        return _DecodeJson(content)


def _DoPutOrPost(uri, method, data, contentType):
    h = httplib2.Http()
    _SetupCredentials(h)

    if isinstance(data, str):
        body = data
        if len(contentType) != 0:
            headers = { 'content-type' : contentType,
                        'Authorization' : 'Basic ' + _auth.decode() }
        else:
            headers = { 'content-type' : 'text/plain',
                        'Authorization' : 'Basic ' + _auth.decode()}
    else:
        body = json.dumps(data)
        headers = { 'content-type' : 'application/json',
                    'Authorization' : 'Basic ' + _auth.decode()}

    resp, content = h.request(
        uri, method,
        body = body,
        headers = headers)

    if not (resp.status in [ 200, 302 ]):
        raise Exception(resp.status)
    else:
        return _DecodeJson(content)


def DoDelete(uri):
    h = httplib2.Http()
    _SetupCredentials(h)
    headers = { 'Authorization' : 'Basic ' + _auth.decode() }

    resp, content = h.request(uri, 'DELETE', headers=headers)

    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    else:
        return _DecodeJson(content)


def DoPut(uri, data = {}, contentType = ''):
    return _DoPutOrPost(uri, 'PUT', data, contentType)


def DoPost(uri, data = {}, contentType = ''):
    return _DoPutOrPost(uri, 'POST', data, contentType)


def GetPatientIds(uri, interpretAsJson = True):

    h = httplib2.Http()
    _SetupCredentials(h)
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization' : 'Basic ' + _auth.decode()}

    resp, content = h.request(uri + "/patients", 'GET', headers=headers)

    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    elif not interpretAsJson:
        return content.decode()
    else:
        return _DecodeJson(content)

def GetPatientData(uri, patient_id, interpretAsJson = True):

    patient_properties = []
    h = httplib2.Http()
    _SetupCredentials(h)
    headers = {'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization' : 'Basic ' + _auth.decode(),
                'Connection': 'keep-alive'}
    for p in patient_id:
        resp, content = h.request(uri + "/patients/"+p, 'GET', headers=headers)
        #h.close()
        if not (resp.status in [ 200 ]):
            raise Exception(resp.status)
        elif not interpretAsJson:
            patient_properties.append(content.decode())
        else:
            patient_properties.append(_DecodeJson(content))
    h.close()
    return patient_properties


def GetStudies(uri, studies, interpretAsJson = True):
    study_data = []
    h = httplib2.Http()
    _SetupCredentials(h)
    for p in studies:
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Authorization' : 'Basic ' + _auth.decode(),
                   'Connection': 'keep-alive'}

        resp, content = h.request(uri + "/studies/"+p, 'GET', headers=headers)
        if not (resp.status in [ 200 ]):
            raise Exception(resp.status)
        elif not interpretAsJson:
            study_data.append(content.decode())
        else:
            study_data.append(_DecodeJson(content))
    h.close()
    return study_data

def GetSeries(uri, series, interpretAsJson = True):
    series_data = []
    h = httplib2.Http()
    _SetupCredentials(h)
    for p in series:
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Authorization' : 'Basic ' + _auth.decode(),
                   'Connection': 'keep-alive'}

        resp, content = h.request(uri + "/series/"+p, 'GET', headers=headers)

        if not (resp.status in [ 200 ]):
            raise Exception(resp.status)
        elif not interpretAsJson:
            series_data.append(content.decode())
        else:
            series_data.append(_DecodeJson(content))
    h.close()
    return series_data

def GetInstances(uri, instances, interpretAsJson = True):
    instance_data = []
    h = httplib2.Http()
    _SetupCredentials(h)
    for p in instances:
        
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Authorization' : 'Basic ' + _auth.decode(),
                   'Connection': 'keep-alive'}

        resp, content = h.request(uri + "/instances/"+p+"/simplified-tags", 'GET', headers=headers)

        if not (resp.status in [ 200 ]):
            raise Exception(resp.status)
        elif not interpretAsJson:
            instance_data.append(content.decode())
        else:
            instance_data.append(_DecodeJson(content))
    h.close()
    return instance_data

def GetImageDescription(uri, instance, interpretAsJson = True):
    # Function that is used to get RTimagedescription when it is too long
    h = httplib2.Http()
    _SetupCredentials(h)
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization' : 'Basic ' + _auth.decode(),
               'Connection': 'Close'}

    resp, content = h.request(uri + "/instances/"+instance+"/content/3002-0004", 'GET', headers=headers)
    h.close()
    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    elif not interpretAsJson:
        instance_data = content.decode()
    else:
        instance_data = _DecodeJson(content)
    return instance_data

def GetSeries2Subfolders_helperf(args):
    i = args[0]  # instance
    uri = args[1]
    if i != None:
        temp_folder = tempfile.mkdtemp(prefix=i+"_", dir=config.TEMP_DCM_FOLDER)
        temp_file1 = tempfile.NamedTemporaryFile(delete=False, prefix=i+"_", suffix=".DCM", dir=temp_folder)
        temp_file2 = tempfile.NamedTemporaryFile(delete=False, prefix=i+"_second_", suffix=".DCM", dir=temp_folder)
        file = DoGet(uri + "/instances/" + i + "/file")

        with open(temp_file1.name, 'wb') as dst:
            dst.write(file)
        copyfile(temp_file1.name, temp_file2.name)
        temp_file1.close()
        temp_file2.close()
        return temp_folder
    else:
        return "None"


def GetSeries2Subfolders(uri, list_instances, pickinstances, interpretAsJson = True):
    # Get filepaths, ordered in sequence of datetime! Ordering is important for analysis (Winston Lutz etc.)

    # If image was not chose put None into instance list:
    for p in range(0, len(list_instances)):
        if not pickinstances[p]:
            list_instances[p] = None
    
    # Now save each file twice in a subfolder
    arguments = []
    for i in range(len(list_instances)):
        arguments.append([list_instances[i], uri])

    p = ThreadPool(4)
    file_paths = p.map(GetSeries2Subfolders_helperf, arguments)
    p.close()
    p.join()
    
    return file_paths

def GetSeries2Folder(uri, instances, pickinstances, interpretAsJson = True):
    # Get filepaths, ordered in sequence of datetime! But this time save in one folder
    # and use numeric image names!
    # series is a list of series, for only one series  = ["..."]
    # For winston lutz "pylinac" method
    file_paths_final = []
    file_paths_full = []
    temp_folder = tempfile.mkdtemp(prefix=instances[0]+"_", dir=config.TEMP_DCM_FOLDER)

    # If image was not chose put None into instance list:
    for p in range(0, len(instances)):
        if not pickinstances[p]:
            instances[p] = None

    # Now save each file
    for i in range(0, len(instances), 1):
        if instances[i] != None:
            temp_file = os.path.join(temp_folder, "img"+str(i+1)+".dcm")
            file = DoGet(uri + "/instances/" + instances[i] + "/file")
            with open(temp_file, 'wb') as dst:
                dst.write(file)
            dst.close()
            file_paths_final.append(temp_file)
            file_paths_full.append(temp_file)
        else:
            file_paths_full.append("None")
    return temp_folder, file_paths_final, file_paths_full

def GetSeries2Folder2_helperf(args):
    instance = args[0]
    temp_folder = args[1]
    uri = args[2]

    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix=instance+"_", suffix=".DCM", dir=temp_folder)
    file = DoGet(uri + "/instances/" + instance + "/file")
    with open(temp_file.name, 'wb') as dst:
        dst.write(file)
    dst.close()
    temp_file.close()


def GetSeries2Folder2(uri, series, interpretAsJson = True):
    h = httplib2.Http()
    _SetupCredentials(h)
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization' : 'Basic ' + _auth.decode(),
               'Connection': 'Close'}

    resp, content = h.request(uri + "/series/" + series, 'GET', headers=headers)
    h.close()
    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    elif not interpretAsJson:
        data = content.decode()
    else:
        data = _DecodeJson(content)
    instances = data["Instances"]

    temp_folder = tempfile.mkdtemp(prefix=series+"_", dir=config.TEMP_DCM_FOLDER)
    
    arguments = []
    for i in range(len(instances)):
        arguments.append([instances[i], temp_folder, uri])

    p = ThreadPool(4)
    p.map(GetSeries2Folder2_helperf, arguments)
    p.close()
    p.join()

    return temp_folder

def GetSingleDcm(uri, instance, interpretAsJson = True):
    #Get one single dicom file
    #Used, for example, for the starshot module'''
    temp_folder = tempfile.mkdtemp(prefix=instance+"_", dir=config.TEMP_DCM_FOLDER)
    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix="Dicom_", suffix=".DCM", dir=temp_folder)
    file = DoGet(uri + "/instances/" + instance + "/file")
    with open(temp_file.name, 'wb') as dst:
        dst.write(file)
    dst.close()
    temp_file.close()
    return temp_folder, temp_file.name

def DoGet_image(uri, data = {}, interpretAsJson = True):
    d = ''
    if len(data.keys()) > 0:
        d = '?' + urlencode(data)

    h = httplib2.Http()
    _SetupCredentials(h)

    headers = {'Accept': 'image/png',
               'Content-Type': 'image/png',
               'Authorization' : 'Basic ' + _auth.decode() }
    resp, content = h.request(uri + d, 'GET', headers=headers)
    h.close()
    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    elif not interpretAsJson:
        return content.decode()
    else:
        return _DecodeJson(content)
