import sys
import os
import json
import datetime
import numpy as np
import base64

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    import RestToolbox_modified as RestToolbox
    from python_packages.bottlepy.bottle import Bottle, static_file
else:
    from . import config
    from . import RestToolbox_modified as RestToolbox
    from .python_packages.bottlepy.bottle import Bottle, static_file

app_general = Bottle()

CUR_DIR = os.path.realpath(os.path.dirname(__file__))
CUR_DIR_STATIC = os.path.join(CUR_DIR, "static")
CUR_DIR_STATIC_DOCS = os.path.join(CUR_DIR_STATIC, "docs")

PLWEB_FOLDER = config.PLWEB_FOLDER

@app_general.get('/<filename:re:.*\.(css)>')
def stylesheets(filename):
    # Serve css files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.get('/<filename:re:.*\.(map)>')
def stylesheets_map(filename):
    # Serve css files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.get('/<filename:re:.*\.(ttf)>')
def font_bootstrap(filename):
    # Serve font files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.get('/<filename:re:.*\.(woff)>')
def font_bootstrap_woff(filename):
    # Serve font files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.get('/<filename:re:.*\.(woff2)>')
def font_bootstrap_woff2(filename):
    # Serve font files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.get('/<filename:re:.*\.(js)>')
def javascript(filename):
    # Serve js files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.get('/<filename:re:.*\.(html)>')
def html(filename):
    # Serve html files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.get('/docs/<filepath:path>')
def server_sphinx(filepath):
    # Serve sphinx
    return static_file(filepath, root=CUR_DIR_STATIC_DOCS)

@app_general.get('/<filename:re:.*\.(png)>')
def png(filename):
    # Serve png files
    return static_file(filename, root=CUR_DIR_STATIC)

@app_general.route(PLWEB_FOLDER + '/searchStudies/<s>', method="POST")
def livesearch_study(s):
    if s != "FirstLineEmptyLineFromJavascriptPatient":
        # Function to get studies and return them to the interface
        data = RestToolbox.GetPatientData(config.ORTHANC_URL, [s])
        studies = data[0]["Studies"]
        data_s = RestToolbox.GetStudies(config.ORTHANC_URL, studies)
        study_names = []
    
        for p in data_s:
            try:
                name_id = p["MainDicomTags"]["StudyID"]
            except:
                name_id = ""
            try:
                name_desc = " (" + p["MainDicomTags"]["StudyDescription"] + ")"
            except:
                name_desc = ""
            if name_desc == "" and name_id == "":
                name_id = "Undefined"
            try:
                study_date = " - " + datetime.datetime.strptime(p["MainDicomTags"]["StudyDate"], "%Y%m%d").strftime("%Y-%m-%d")
            except:
                study_date = ""
            study_names.append(name_id + name_desc + study_date)
        return json.dumps((["FirstLineEmptyLineFromJavascriptStudy"]+studies, ["-----------"]+study_names))
    else:
        return json.dumps((["FirstLineEmptyLineFromJavascriptStudy"], ["-----------"]))


@app_general.route(PLWEB_FOLDER + '/searchSeries/<s>', method="POST")
def livesearch_series(s):
    # Function to get series and return to the interface
    if s != "FirstLineEmptyLineFromJavascriptStudy":
        data = RestToolbox.GetStudies(config.ORTHANC_URL, [s])
        series = data[0]["Series"]
        data_s = RestToolbox.GetSeries(config.ORTHANC_URL, series)
        series_names = []
     
        for p in data_s:
            try:
                ser_num = " (" + p["MainDicomTags"]["SeriesNumber"] + ")"
            except:
                ser_num = ""
            try:
                ser_desc = p["MainDicomTags"]["SeriesDescription"]
            except:
                ser_desc = ""
            if ser_num == "" and ser_desc == "":
                ser_num = "Undefined"
    
            ser_datetime = RestToolbox.GetInstances(config.ORTHANC_URL, [p["Instances"][0]])
    
            date_var = RestToolbox.get_datetime(ser_datetime[0])
    
            if date_var[0] == "Unknown":
                date_str = "Unknown date"
            else:
                date_str = datetime.datetime.strptime(date_var[0], "%Y%m%d").strftime("%Y-%m-%d")  # To string
            series_names.append(ser_desc + ser_num + " - " + date_str)
        return json.dumps((["FirstLineEmptyLineFromJavascriptSeries"] + series, ["-----------"] + series_names))
    else:
        return json.dumps((["FirstLineEmptyLineFromJavascriptSeries"], ["-----------"]))


@app_general.route(PLWEB_FOLDER + '/searchInstances/<s:re:.+>', method="POST")
def livesearch_instances(s):

    if "FirstLineEmptyLineFromJavascriptSeries" not in s:
        # Function to get single dicom files in order of time stamp
        series = s.split("/")
        instances_final_num = []
        num_instances_final = []
        instance_datetime_final = []
        instances_final = []

        inst_temp = []
        # First collect all instances, then order them!
        for ss in series:
            p = RestToolbox.GetSeries(config.ORTHANC_URL, [ss])[0]
            instances = p["Instances"]
            num_instances_final.append(len(instances))
            # GEt all instances for ss series:
            instances_final.append(instances)
            inst_temp.append(RestToolbox.GetInstances(config.ORTHANC_URL, instances))

        inst_temp = [val for sublist in inst_temp for val in sublist]
        instances_final = [val for sublist in instances_final for val in sublist]
        
        # Order all instances by date time
        instance_datetime, instance_datetime_order, instance_num = RestToolbox.order_instance_datetime(inst_temp)
        order = np.argsort(instance_datetime_order)
        
        instances_final_num = (np.asarray(instance_num)[order]).tolist()
        instance_datetime_final = (np.asarray(instance_datetime)[order]).tolist()
        instances_final = (np.asarray(instances_final)[order]).tolist()

        # Take stationname from last element of series
        try:
            station_name = p["MainDicomTags"]["StationName"]
        except:
            station_name = "Unknown"
        if station_name==None:
            station_name = "Unknown"
    
        # Take image description tag from last element of instances (MUST DO THIS BETTER!)
        try:
            img_description = inst_temp[-1]["RTImageDescription"]
        except:
            img_description = "Not available"

        if img_description==None:
            try:
                img_description = RestToolbox.GetImageDescription(config.ORTHANC_URL, instances[-1], interpretAsJson = False)
            except:
                img_description = "Not available"
            if img_description==None:
                img_description = "Not available"

        return json.dumps({"1": instances_final_num, "2": num_instances_final,
                           "3": instance_datetime_final, "4": instances_final,
                           "5": station_name, "6": img_description})
    else:
        return json.dumps({"1": [], "2": [],
                           "3": [], "4": [],
                           "5": "", "6": ""})

@app_general.route(PLWEB_FOLDER + '/searchSeriesTags/<s>', method="POST")
def livesearch_series_tags(s):
    '''Used to find some data for a large series with multiple instances'''
    if s!= "FirstLineEmptyLineFromJavascriptSeries":
        p = RestToolbox.GetSeries(config.ORTHANC_URL, [s])[0]
        instances = p["Instances"]
        num_instances = len(instances)
        tags = p["MainDicomTags"]

        try:
            ser_datetime = RestToolbox.GetInstances(config.ORTHANC_URL, [p["Instances"][0]])
            datetime_var = RestToolbox.get_datetime(ser_datetime[0])
            tt = datetime_var[0]+datetime_var[1]
            #try:
            #    milisec = "."+tt[15:17]
            #except:
            #    milisec = ".00"
            series_datetime = datetime.datetime.strptime(tt[0:14], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S") #+milisec
        except:
            series_datetime = "Unknown"
    
        try:
            manufact = tags["Manufacturer"]
        except:
            manufact = "Unknown"
        try:
            modality = tags["Modality"]
        except:
            modality = "Unknown"
        try:
            protocol = tags["ProtocolName"]
        except:
            protocol = "Unknown"
        try:
            station = tags["StationName"]
        except:
            station = "Unknown"
    
        return json.dumps({"1": series_datetime, "2": num_instances, "3": manufact, "4": modality, "5": protocol,
                           "6": station})
    else:
        return json.dumps({"1": "", "2": "", "3": "", "4": "", "5": "",
                           "6": ""})

@app_general.route(PLWEB_FOLDER + '/getInstanceImage/<s>', method="POST")
def getinstanceimage(s):
    # Function to get png image from the instance and return it to user
    image = RestToolbox.DoGet_image(config.ORTHANC_URL + "/instances/" + s + "/preview")
    return base64.b64encode(image)

@app_general.route(PLWEB_FOLDER + '/getInstanceImageDescription/<s>', method="POST")
def getinstanceimagedescription(s):
    # Function to get image description. Used only for some modules (StarShot etc)
    try:
        img_description = RestToolbox.GetImageDescription(config.ORTHANC_URL, s, interpretAsJson = False)
    except:
        img_description = "Not available"
    if img_description==None:
        img_description = "Not available"
    return img_description
