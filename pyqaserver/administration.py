import sys
import os
import sqlite3 as sql
import json
import shutil
import datetime

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    import general_functions
    import RestToolbox_modified as RestToolbox
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
else:
    from . import config
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    
CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

# Here starts the bottle server
admin_app = Bottle()

@admin_app.route('/administration', method="POST")
def administration():
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    displayname = request.forms.hidden_displayname
    if not username:
        redirect("/login")
    
    elif not general_functions.check_is_admin(username):
        return template("error_template", {"error_message": "Insufficient rights."})
    else:
        variables = {
            "displayname": displayname
            }
        response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
        return template("administration", variables)

@admin_app.route('/edit_users', method="POST")
def edit_users():
    return template("edit_users")

@admin_app.route('/get_user_data', method="POST")
def get_user_data():
    json_string = []
    users = general_functions.get_users()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Name": users[a][1], "Admin": users[a][2], "Displayname": users[a][3]})
    return json.dumps(json_string)

@admin_app.route('/add_user', method="POST")
def add_user():
    username = request.forms.username
    displayname = request.forms.displayname
    password = request.forms.password
    is_admin = "Yes" if request.forms.is_admin=="true" else "No"
    try:
        general_functions.add_one_user(username, password, is_admin, displayname)
        return "Done!"
    except sql.IntegrityError:
        return "User already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_user', method="POST")
def remove_user():
    user_id = request.forms.user_id
    if not general_functions.can_delete(int(user_id)):
        return "Cannot delete the only admin user."
    if int(user_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_one_user(int(user_id))
        return "Done!"
    except:
        return "Failed!"
    
    
################################ ORTHANC ####################################
@admin_app.route('/edit_orthanc', method="POST")
def edit_orthanc():
    return template("edit_orthanc")

@admin_app.route('/get_orthanc_settings', method="POST")
def get_orthanc_settings():
    json_string = []
    users = general_functions.get_orthanc_settings()
    json_string.append({"Setting": "IP", "Value": users[0]})
    json_string.append({"Setting": "Port", "Value": users[1]})
    json_string.append({"Setting": "User", "Value": users[2]})
    json_string.append({"Setting": "Password", "Value": users[3]})
    return json.dumps(json_string)

@admin_app.route('/update_orthanc_settings', method="POST")
def update_orthanc_settings():
    IP = request.forms.IP
    Port = request.forms.Port
    User = request.forms.User
    Password = request.forms.Password
    try:
        general_functions.update_orthanc_settings(IP, Port, User, Password)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    

################################ INSTITUTION ####################################
@admin_app.route('/edit_institution', method="POST")
def edit_institution():
    return template("edit_institution")

@admin_app.route('/get_institution_settings', method="POST")
def get_institution_settings():
    json_string = []
    users = general_functions.get_institution_settings()
    json_string.append({"Setting": "Name", "Value": users[0]})
    return json.dumps(json_string)

@admin_app.route('/update_institution_settings', method="POST")
def update_institution_settings():
    Name = request.forms.Name
    try:
        general_functions.update_institution_settings(Name)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

################################ WINSTON LUTZ ################################
@admin_app.route('/edit_settings_winstonlutz', method="POST")
def edit_settings_winstonlutz():
    return template("edit_settings_winstonlutz")

@admin_app.route('/get_treatmentunits_wl', method="POST")
def get_treatmentunits_wl():
    json_string = []
    users = general_functions.get_treatmentunits_wl()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Machine": users[a][1], "Beam": users[a][2]})
    return json.dumps(json_string)

@admin_app.route('/add_treatmentunit_wl', method="POST")
def add_treatmentunit_wl():
    machine = request.forms.Machine
    beam = request.forms.Beam
    try:
        general_functions.add_treatmentunit_wl(machine, beam)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_treatmentunit_wl', method="POST")
def remove_treatmentunit_wl():
    unit_id = request.forms.unit_id
    if int(unit_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_treatmentunit_wl(int(unit_id))
        return "Done!"
    except:
        return "Failed!"
    
@admin_app.route('/get_settings_wl', method="POST")
def get_settings_wl():
    json_string = []
    users = general_functions.get_settings_wl()
    json_string.append({"Setting": "PASS_RATE", "Value": users[0]})
    json_string.append({"Setting": "ACTION_RATE", "Value": users[1]})
    json_string.append({"Setting": "APPLY_TOLERANCE_TO_COLL_ASYM", "Value": users[2]})
    json_string.append({"Setting": "COLL_ASYM_TOL", "Value": users[3]})
    json_string.append({"Setting": "BEAM_DEV_TOL", "Value": users[4]})
    json_string.append({"Setting": "COUCH_DIST_TOL", "Value": users[5]})
    return json.dumps(json_string)

@admin_app.route('/get_tolerance_wl', method="POST")
def get_tolerance_wl():
    json_string = []
    users = general_functions.get_tolerance_wl()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "PASS_RATE": i[2], "ACTION_RATE": i[3], "APPLY_TOLERANCE_TO_COLL_ASYM": i[4],
                            "COLL_ASYM_TOL": i[5], "BEAM_DEV_TOL": i[6], "COUCH_DIST_TOL": i[7]})
    return json.dumps(json_string)

@admin_app.route('/update_settings_wl', method="POST")
def update_settings_wl():
    passrate = request.forms.passrate
    actionrate = request.forms.actionrate
    collasym = "True" if request.forms.collasym=="true" else "False"
    coll_asym_tol = request.forms.collasym_tol_gen
    beam_dev_tol = request.forms.beam_dev_tol_gen
    couch_distance_tol = request.forms.couch_distance_gen
    try:
        general_functions.update_settings_wl(passrate, actionrate, collasym, coll_asym_tol, beam_dev_tol, couch_distance_tol)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/add_tolerance_wl', method="POST")
def add_tolerance_wl():
    machine = request.forms.machine_tol
    passrate = request.forms.passrate_tol
    actionrate = request.forms.actionrate_tol
    collasym = "True" if request.forms.collasym_tol=="true" else "False"
    coll_asym_tol = request.forms.collasym_tol_m
    beam_dev_tol = request.forms.beam_dev_tol_m
    couch_distance_tol = request.forms.couch_distance_m
    try:
        general_functions.add_tolerance_wl(machine, passrate, actionrate, collasym, coll_asym_tol, beam_dev_tol, couch_distance_tol)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_wl', method="POST")
def remove_tolerance_wl():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_wl(int(tol_id))
        return "Done!"
    except:
        return "Failed!"

@admin_app.route('/get_phantoms_wl', method="POST")
def get_phantoms_wl():
    json_string = []
    users = general_functions.get_phantoms_wl()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Phantom": users[a][1]})
    return json.dumps(json_string)

@admin_app.route('/add_phantom_wl', method="POST")
def add_phantom_wl():
    phantom = request.forms.Phantom
    try:
        general_functions.add_phantom_wl(phantom)
        return "Done!"
    except sql.IntegrityError:
        return "Phantom already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_phantom_wl', method="POST")
def remove_phantom_wl():
    phantom_id = request.forms.phantom_id
    if int(phantom_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_phantom_wl(int(phantom_id))
        return "Done!"
    except:
        return "Failed!"

################################ STARSHOT ################################
@admin_app.route('/edit_settings_starshot', method="POST")
def edit_settings_starshot():
    return template("edit_settings_starshot")

@admin_app.route('/get_treatmentunits_starshot', method="POST")
def get_treatmentunits_starshot():
    json_string = []
    users = general_functions.get_treatmentunits_starshot()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Machine": users[a][1], "Beam": users[a][2]})
    return json.dumps(json_string)

@admin_app.route('/add_treatmentunit_starshot', method="POST")
def add_treatmentunit_starshot():
    machine = request.forms.Machine
    beam = request.forms.Beam
    try:
        general_functions.add_treatmentunit_starshot(machine, beam)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_treatmentunit_starshot', method="POST")
def remove_treatmentunit_starshot():
    unit_id = request.forms.unit_id
    if int(unit_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_treatmentunit_starshot(int(unit_id))
        return "Done!"
    except:
        return "Failed!"
    
@admin_app.route('/get_settings_starshot', method="POST")
def get_settings_starshot():
    json_string = []
    users = general_functions.get_settings_starshot()
    json_string.append({"Setting": "TOLERANCE", "Value": users[0]})
    json_string.append({"Setting": "GENERATE_PDF_REPORT", "Value": users[1]})
    return json.dumps(json_string)


@admin_app.route('/update_settings_starshot', method="POST")
def update_settings_starshot():
    passrate = request.forms.passrate
    generate_pdf = "True" if request.forms.generate_pdf=="true" else "False"

    try:
        general_functions.update_settings_starshot(passrate, generate_pdf)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/get_tolerance_starshot', method="POST")
def get_tolerance_starshot():
    json_string = []
    users = general_functions.get_tolerance_starshot()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "TOLERANCE": i[2], "GENERATE_PDF_REPORT": i[3]})
    return json.dumps(json_string)

@admin_app.route('/add_tolerance_starshot', method="POST")
def add_tolerance_starshot():
    machine = request.forms.machine_tol
    passrate = request.forms.passrate_tol
    generate_pdf_tol = "True" if request.forms.generate_pdf_tol=="true" else "False"
    try:
        general_functions.add_tolerance_starshot(machine, passrate, generate_pdf_tol)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_starshot', method="POST")
def remove_tolerance_starshot():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_starshot(int(tol_id))
        return "Done!"
    except:
        return "Failed!"


################################ PICKETFENCE ################################
@admin_app.route('/edit_settings_picketfence', method="POST")
def edit_settings_picketfence():
    return template("edit_settings_picketfence")

@admin_app.route('/get_treatmentunits_picketfence', method="POST")
def get_treatmentunits_picketfence():
    json_string = []
    users = general_functions.get_treatmentunits_picketfence()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Machine": users[a][1], "Beam": users[a][2]})
    return json.dumps(json_string)

@admin_app.route('/add_treatmentunit_picketfence', method="POST")
def add_treatmentunit_picketfence():
    machine = request.forms.Machine
    beam = request.forms.Beam
    try:
        general_functions.add_treatmentunit_picketfence(machine, beam)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_treatmentunit_picketfence', method="POST")
def remove_treatmentunit_picketfence():
    unit_id = request.forms.unit_id
    if int(unit_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_treatmentunit_picketfence(int(unit_id))
        return "Done!"
    except:
        return "Failed!"
    
@admin_app.route('/get_settings_picketfence', method="POST")
def get_settings_picketfence():
    json_string = []
    users = general_functions.get_settings_picketfence()
    json_string.append({"Setting": "ACTION_TOLERANCE", "Value": users[0]})
    json_string.append({"Setting": "TOLERANCE", "Value": users[1]})
    json_string.append({"Setting": "GENERATE_PDF_REPORT", "Value": users[2]})
    return json.dumps(json_string)

@admin_app.route('/get_tolerance_picketfence', method="POST")
def get_tolerance_picketfence():
    json_string = []
    users = general_functions.get_tolerance_picketfence()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "ACTION_TOLERANCE": i[2], "TOLERANCE": i[3], "GENERATE_PDF_REPORT": i[4]})
    return json.dumps(json_string)

@admin_app.route('/update_settings_picketfence', method="POST")
def update_settings_picketfence():
    action_tolerance = request.forms.action_tolerance
    tolerance = request.forms.tolerance
    generate_pdf = "True" if request.forms.generate_pdf=="true" else "False"
    try:
        general_functions.update_settings_picketfence(action_tolerance, tolerance, generate_pdf)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/add_tolerance_picketfence', method="POST")
def add_tolerance_picketfence():
    machine = request.forms.machine_tol
    action_tolerance = request.forms.action_tolerance_tol
    tolerance = request.forms.tolerance_tol
    generate_pdf = "True" if request.forms.generate_pdf_tol=="true" else "False"

    try:
        general_functions.add_tolerance_picketfence(machine, action_tolerance, tolerance, generate_pdf)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_picketfence', method="POST")
def remove_tolerance_picketfence():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_picketfence(int(tol_id))
        return "Done!"
    except:
        return "Failed!"


################################ PLANAR IMAGING ################################
@admin_app.route('/edit_settings_planarimaging', method="POST")
def edit_settings_planarimaging():
    variables = {
        "phantoms": config.PLANARIMAGING_PHANTOMS
        }
    return template("edit_settings_planarimaging", variables)


@admin_app.route('/get_tolerance_planarimaging', method="POST")
def get_tolerance_planarimaging():
    json_string = []
    users = general_functions.get_tolerance_planarimaging()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "Beam": i[2], "Phantom": i[3], "LOW_THRESHOLD": i[4],
                            "HIGH_THRESHOLD": i[5], "GENERATE_PDF_REPORT": i[6]})
    return json.dumps(json_string)

@admin_app.route('/add_tolerance_planarimaging', method="POST")
def add_tolerance_planarimaging():
    machine = request.forms.machine_tol
    beam = request.forms.beam_tol
    phantom = request.forms.phantom_tol
    low_threshold = request.forms.low_threshold_tol
    high_threshold = request.forms.high_threshold_tol
    generate_pdf = "True" if request.forms.generate_pdf_tol=="true" else "False"
    try:
        general_functions.add_tolerance_planarimaging(machine, beam, phantom, low_threshold, high_threshold, generate_pdf)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_planarimaging', method="POST")
def remove_tolerance_planarimaging():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_planarimaging(int(tol_id))
        return "Done!"
    except:
        return "Failed!"

@admin_app.route('/get_referenceimages_planarimaging', method="POST")
def get_referenceimages_planarimaging():
    json_string = []
    users = general_functions.get_referenceimages_planarimaging()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "Beam": i[2], "Phantom": i[3], "Path": i[4]})
    return json.dumps(json_string)


@admin_app.route('/add_referenceimage_planarimaging', method="POST")
def add_referenceimage_planarimaging():
    machine = request.forms.Machine
    beam = request.forms.Beam
    phantom = request.forms.Phantom
    orthanc_instance = request.forms.Instance
    
    new_name = os.path.join(phantom, machine, beam)
    new_path = os.path.join(config.WORKING_DIRECTORY, config.REFERENCE_IMAGES_FOLDER, new_name)
    
    # If the sql database already references machine/beam/phantom, then do nothing.
    if general_functions.has_referenceimages_planarimaging(machine, beam, phantom)[0]==1:
        return "Reference already exists. Remove the reference and retry."
    
    # Get the dicom image to a temp folder, then copy it to database folder
    try:
        temp_folder, file_path = RestToolbox.GetSingleDcm(config.ORTHANC_URL, orthanc_instance)
    except Exception as e:
        return "Could not download file. Check Orthanc settings. "+str(e)
    
    # Now copy the file to reference_images folder
    # First create new directory for this image

    try:
        if not os.path.isdir(new_path):
            os.makedirs(new_path)
    except Exception as e:
        general_functions.delete_files_in_subfolders([temp_folder])
        return "Could not create room for the image in the repository. "+str(e)

    try:
        new_file_name_string = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+".dcm"
        shutil.copyfile(file_path, os.path.join(new_path, new_file_name_string))
    except Exception as e:
        general_functions.delete_files_in_subfolders([temp_folder])
        return "Could not copy downloaded file to repository. "+str(e)
    
    general_functions.delete_files_in_subfolders([temp_folder])
    # Now save the path to database
    try:
        general_functions.add_referenceimage_planarimaging(machine, beam, phantom,
                                                           os.path.join(new_name, new_file_name_string))
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_referenceimage_planarimaging', method="POST")
def remove_referenceimage_planarimaging():
    ref_id = request.forms.ref_id
    if int(ref_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_referenceimage_planarimaging(int(ref_id))
        return "Done!"
    except:
        return "Failed!"


################################ CATPHAN ################################
@admin_app.route('/edit_settings_catphan', method="POST")
def edit_settings_catphan():
    variables = {
        "phantoms": config.CATPHAN_PHANTOMS
        }
    return template("edit_settings_catphan", variables)


@admin_app.route('/get_tolerance_catphan', method="POST")
def get_tolerance_catphan():
    json_string = []
    users = general_functions.get_tolerance_catphan()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "Beam": i[2], "Phantom": i[3], "HU": i[4],
                            "LCV": i[5], "SCALING": i[6], "THICKNESS": i[7],
                            "LOWCONTRAST": i[8], "CNR": i[9], "MTF": i[10],
                            "UNIFORMITYIDX": i[11], "GENERATE_PDF_REPORT": i[12]})
    return json.dumps(json_string)

@admin_app.route('/add_tolerance_catphan', method="POST")
def add_tolerance_catphan():
    machine = request.forms.machine_tol
    beam = request.forms.beam_tol
    phantom = request.forms.phantom_tol
    hu = request.forms.hu_tol
    lcv = request.forms.lcv_tol
    scaling = request.forms.scaling_tol
    thickness = request.forms.thickness_tol
    lowcontrast = request.forms.lowcontrast_tol
    cnr = request.forms.cnr_tol
    mtf = request.forms.mtf_tol
    uniformityidx = request.forms.uniformityidx_tol
    generate_pdf = "True" if request.forms.generate_pdf_tol=="true" else "False"

    try:
        general_functions.add_tolerance_catphan(machine, beam, phantom,
                                                hu, lcv, scaling, thickness,
                                                lowcontrast, cnr, mtf,
                                                uniformityidx, generate_pdf)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_catphan', method="POST")
def remove_tolerance_catphan():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_catphan(int(tol_id))
        return "Done!"
    except:
        return "Failed!"

@admin_app.route('/get_referenceimages_catphan', method="POST")
def get_referenceimages_catphan():
    json_string = []
    users = general_functions.get_referenceimages_catphan()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "Beam": i[2], "Phantom": i[3], "Path": i[4]})
    return json.dumps(json_string)


@admin_app.route('/add_referenceimage_catphan', method="POST")
def add_referenceimage_catphan():
    machine = request.forms.Machine
    beam = request.forms.Beam
    phantom = request.forms.Phantom
    orthanc_series = request.forms.Series
    
    new_name = os.path.join(phantom, machine, beam)
    new_folder_name = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    new_path = os.path.join(config.WORKING_DIRECTORY, config.REFERENCE_IMAGES_FOLDER, new_name, new_folder_name)
    
    # If the sql database already references machine/beam/phantom, then do nothing.
    if general_functions.has_referenceimages_catphan(machine, beam, phantom)[0]==1:
        return "Reference already exists. Remove the reference and retry."
    
    # Get the dicom images to a temp folder, then copy it to database folder
    try:
        temp_folder = RestToolbox.GetSeries2Folder2(config.ORTHANC_URL, orthanc_series)
    except Exception as e:
        return "Could not download files. Check Orthanc settings. "+str(e)
    
    # Now copy the file to reference_images folder
    # First create new directory for this image
    try:
        if not os.path.isdir(new_path):
            os.makedirs(new_path)
    except Exception as e:
        general_functions.delete_files_in_subfolders([temp_folder])
        return "Could not create room for the images in the repository. "+str(e)

    try:
        list_of_files = os.listdir(temp_folder)
        for old_file_name in list_of_files:
            shutil.copyfile(os.path.join(temp_folder, old_file_name), os.path.join(new_path, old_file_name))
    except Exception as e:
        general_functions.delete_files_in_subfolders([temp_folder])
        return "Could not copy downloaded files to repository. "+str(e)
    
    general_functions.delete_files_in_subfolders([temp_folder])
    
    # Now save the path to database
    try:
        general_functions.add_referenceimage_catphan(machine, beam, phantom,
                                                     os.path.join(new_name, new_folder_name))
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_referenceimage_catphan', method="POST")
def remove_referenceimage_catphan():
    ref_id = request.forms.ref_id
    if int(ref_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_referenceimage_catphan(int(ref_id))
        return "Done!"
    except:
        return "Failed!"


################################ FLATSYM ################################
@admin_app.route('/edit_settings_flatsym', method="POST")
def edit_settings_flatsym():
    return template("edit_settings_flatsym")

@admin_app.route('/get_treatmentunits_flatsym', method="POST")
def get_treatmentunits_flatsym():
    json_string = []
    users = general_functions.get_treatmentunits_flatsym()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Machine": users[a][1], "Beam": users[a][2]})
    return json.dumps(json_string)

@admin_app.route('/add_treatmentunit_flatsym', method="POST")
def add_treatmentunit_flatsym():
    machine = request.forms.Machine
    beam = request.forms.Beam
    try:
        general_functions.add_treatmentunit_flatsym(machine, beam)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_treatmentunit_flatsym', method="POST")
def remove_treatmentunit_flatsym():
    unit_id = request.forms.unit_id
    if int(unit_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_treatmentunit_flatsym(int(unit_id))
        return "Done!"
    except:
        return "Failed!"
    
@admin_app.route('/get_settings_flatsym', method="POST")
def get_settings_flatsym():
    json_string = []
    users = general_functions.get_settings_flatsym()
    json_string.append({"Setting": "TOLERANCE_FLAT", "Value": users[0]})
    json_string.append({"Setting": "TOLERANCE_SYM", "Value": users[1]})
    json_string.append({"Setting": "GENERATE_PDF_REPORT", "Value": users[2]})
    return json.dumps(json_string)


@admin_app.route('/update_settings_flatsym', method="POST")
def update_settings_flatsym():
    tolerance_flat = request.forms.tolerance_flat
    tolerance_sym = request.forms.tolerance_sym
    generate_pdf = "True" if request.forms.generate_pdf=="true" else "False"

    try:
        general_functions.update_settings_flatsym(tolerance_flat, tolerance_sym, generate_pdf)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/get_tolerance_flatsym', method="POST")
def get_tolerance_flatsym():
    json_string = []
    users = general_functions.get_tolerance_flatsym()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "TOLERANCE_FLAT": i[2], "TOLERANCE_SYM": i[3], "GENERATE_PDF_REPORT": i[4]})
    return json.dumps(json_string)

@admin_app.route('/add_tolerance_flatsym', method="POST")
def add_tolerance_flatsym():
    machine = request.forms.machine_tol
    tolerance_flat = request.forms.tolerance_flat_tol
    tolerance_sym = request.forms.tolerance_sym_tol
    generate_pdf_tol = "True" if request.forms.generate_pdf_tol=="true" else "False"
    try:
        general_functions.add_tolerance_flatsym(machine, tolerance_flat, tolerance_sym, generate_pdf_tol)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_flatsym', method="POST")
def remove_tolerance_flatsym():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_flatsym(int(tol_id))
        return "Done!"
    except:
        return "Failed!"
    
################################ VMAT ################################
@admin_app.route('/edit_settings_vmat', method="POST")
def edit_settings_vmat():
    return template("edit_settings_vmat")

@admin_app.route('/get_treatmentunits_vmat', method="POST")
def get_treatmentunits_vmat():
    json_string = []
    users = general_functions.get_treatmentunits_vmat()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Machine": users[a][1], "Beam": users[a][2]})
    return json.dumps(json_string)

@admin_app.route('/add_treatmentunit_vmat', method="POST")
def add_treatmentunit_vmat():
    machine = request.forms.Machine
    beam = request.forms.Beam
    try:
        general_functions.add_treatmentunit_vmat(machine, beam)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_treatmentunit_vmat', method="POST")
def remove_treatmentunit_vmat():
    unit_id = request.forms.unit_id
    if int(unit_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_treatmentunit_vmat(int(unit_id))
        return "Done!"
    except:
        return "Failed!"
    
@admin_app.route('/get_settings_vmat', method="POST")
def get_settings_vmat():
    json_string = []
    users = general_functions.get_settings_vmat()
    json_string.append({"Setting": "TOLERANCE", "Value": users[0]})
    json_string.append({"Setting": "GENERATE_PDF_REPORT", "Value": users[1]})
    return json.dumps(json_string)


@admin_app.route('/update_settings_vmat', method="POST")
def update_settings_vmat():
    tolerance = request.forms.tolerance
    generate_pdf = "True" if request.forms.generate_pdf=="true" else "False"

    try:
        general_functions.update_settings_vmat(tolerance, generate_pdf)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/get_tolerance_vmat', method="POST")
def get_tolerance_vmat():
    json_string = []
    users = general_functions.get_tolerance_vmat()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "TOLERANCE": i[2], "GENERATE_PDF_REPORT": i[3]})
    return json.dumps(json_string)

@admin_app.route('/add_tolerance_vmat', method="POST")
def add_tolerance_vmat():
    machine = request.forms.machine_tol
    tolerance = request.forms.tolerance_tol
    generate_pdf_tol = "True" if request.forms.generate_pdf_tol=="true" else "False"
    try:
        general_functions.add_tolerance_vmat(machine, tolerance, generate_pdf_tol)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_vmat', method="POST")
def remove_tolerance_vmat():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_vmat(int(tol_id))
        return "Done!"
    except:
        return "Failed!"


################################ FIELDSIZE ################################
@admin_app.route('/edit_settings_fieldsize', method="POST")
def edit_settings_fieldsize():
    variables = {
        "field_sizes": config.FIELDSIZE_FIELDS
        }
    return template("edit_settings_fieldsize", variables)

@admin_app.route('/get_treatmentunits_fieldsize', method="POST")
def get_treatmentunits_fieldsize():
    json_string = []
    users = general_functions.get_treatmentunits_fieldsize()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Machine": users[a][1], "Beam": users[a][2]})
    return json.dumps(json_string)

@admin_app.route('/add_treatmentunit_fieldsize', method="POST")
def add_treatmentunit_fieldsize():
    machine = request.forms.Machine
    beam = request.forms.Beam
    try:
        general_functions.add_treatmentunit_fieldsize(machine, beam)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_treatmentunit_fieldsize', method="POST")
def remove_treatmentunit_fieldsize():
    unit_id = request.forms.unit_id
    if int(unit_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_treatmentunit_fieldsize(int(unit_id))
        return "Done!"
    except:
        return "Failed!"
    
@admin_app.route('/get_settings_fieldsize', method="POST")
def get_settings_fieldsize():
    json_string = []
    users = general_functions.get_settings_fieldsize()
    json_string.append({"Setting": "SMALL_NOMINAL", "Value": users[0]})
    json_string.append({"Setting": "MEDIUM_NOMINAL", "Value": users[1]})
    json_string.append({"Setting": "LARGE_NOMINAL", "Value": users[2]})
    json_string.append({"Setting": "SMALL_EXP_MLC", "Value": users[3]})
    json_string.append({"Setting": "MEDIUM_EXP_MLC", "Value": users[4]})
    json_string.append({"Setting": "LARGE_EXP_MLC", "Value": users[5]})
    json_string.append({"Setting": "SMALL_EXP_JAW", "Value": users[6]})
    json_string.append({"Setting": "MEDIUM_EXP_JAW", "Value": users[7]})
    json_string.append({"Setting": "LARGE_EXP_JAW", "Value": users[8]})
    json_string.append({"Setting": "TOLERANCE_SMALL_MLC", "Value": users[9]})
    json_string.append({"Setting": "TOLERANCE_MEDIUM_MLC", "Value": users[10]})
    json_string.append({"Setting": "TOLERANCE_LARGE_MLC", "Value": users[11]})
    json_string.append({"Setting": "TOLERANCE_SMALL_JAW", "Value": users[12]})
    json_string.append({"Setting": "TOLERANCE_MEDIUM_JAW", "Value": users[13]})
    json_string.append({"Setting": "TOLERANCE_LARGE_JAW", "Value": users[14]})
    json_string.append({"Setting": "TOLERANCE_ISO", "Value": users[15]})
    return json.dumps(json_string)

@admin_app.route('/get_tolerance_fieldsize', method="POST")
def get_tolerance_fieldsize():
    json_string = []
    users = general_functions.get_tolerance_fieldsize()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1],
                            "SMALL_NOMINAL": i[2],
                            "MEDIUM_NOMINAL": i[3],
                            "LARGE_NOMINAL": i[4],
                            "SMALL_EXP_MLC": i[5],
                            "MEDIUM_EXP_MLC": i[6],
                            "LARGE_EXP_MLC": i[7],
                            "SMALL_EXP_JAW": i[8],
                            "MEDIUM_EXP_JAW": i[9],
                            "LARGE_EXP_JAW": i[10],
                            "TOLERANCE_SMALL_MLC": i[11],
                            "TOLERANCE_MEDIUM_MLC": i[12],
                            "TOLERANCE_LARGE_MLC": i[13],
                            "TOLERANCE_SMALL_JAW": i[14],
                            "TOLERANCE_MEDIUM_JAW": i[15],
                            "TOLERANCE_LARGE_JAW": i[16],
                            "TOLERANCE_ISO": i[17]})
    return json.dumps(json_string)

@admin_app.route('/update_settings_fieldsize', method="POST")
def update_settings_fieldsize():
    small_nominal = request.forms.small_nominal
    medium_nominal = request.forms.medium_nominal
    large_nominal = request.forms.large_nominal
    small_exp_mlc = request.forms.small_exp_mlc
    medium_exp_mlc = request.forms.medium_exp_mlc
    large_exp_mlc = request.forms.large_exp_mlc
    small_exp_jaw = request.forms.small_exp_jaw
    medium_exp_jaw = request.forms.medium_exp_jaw
    large_exp_jaw = request.forms.large_exp_jaw
    tolerance_small_mlc = request.forms.tolerance_small_mlc
    tolerance_medium_mlc = request.forms.tolerance_medium_mlc
    tolerance_large_mlc = request.forms.tolerance_large_mlc
    tolerance_small_jaw = request.forms.tolerance_small_jaw
    tolerance_medium_jaw = request.forms.tolerance_medium_jaw
    tolerance_large_jaw = request.forms.tolerance_large_jaw
    tolerance_iso = request.forms.tolerance_iso

    try:
        general_functions.update_settings_fieldsize(small_nominal, medium_nominal, large_nominal,
                                                    small_exp_mlc, medium_exp_mlc, large_exp_mlc,
                                                    small_exp_jaw, medium_exp_jaw, large_exp_jaw,
                                                    tolerance_small_mlc, tolerance_medium_mlc, tolerance_large_mlc,
                                                    tolerance_small_jaw, tolerance_medium_jaw, tolerance_large_jaw,
                                                    tolerance_iso)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/add_tolerance_fieldsize', method="POST")
def add_tolerance_fieldsize():
    machine_tol = request.forms.machine_tol
    small_nominal_tol = request.forms.small_nominal_tol
    medium_nominal_tol = request.forms.medium_nominal_tol
    large_nominal_tol = request.forms.large_nominal_tol
    small_exp_tol_mlc = request.forms.small_exp_tol_mlc
    medium_exp_tol_mlc = request.forms.medium_exp_tol_mlc
    large_exp_tol_mlc = request.forms.large_exp_tol_mlc
    small_exp_tol_jaw = request.forms.small_exp_tol_jaw
    medium_exp_tol_jaw = request.forms.medium_exp_tol_jaw
    large_exp_tol_jaw = request.forms.large_exp_tol_jaw
    tolerance_small_tol_mlc = request.forms.tolerance_small_tol_mlc
    tolerance_medium_tol_mlc = request.forms.tolerance_medium_tol_mlc
    tolerance_large_tol_mlc = request.forms.tolerance_large_tol_mlc
    tolerance_small_tol_jaw = request.forms.tolerance_small_tol_jaw
    tolerance_medium_tol_jaw = request.forms.tolerance_medium_tol_jaw
    tolerance_large_tol_jaw = request.forms.tolerance_large_tol_jaw
    tolerance_iso_tol = request.forms.tolerance_iso_tol
    try:
        general_functions.add_tolerance_fieldsize(machine_tol, small_nominal_tol, medium_nominal_tol, large_nominal_tol,
                                                  small_exp_tol_mlc, medium_exp_tol_mlc, large_exp_tol_mlc,
                                                  small_exp_tol_jaw, medium_exp_tol_jaw, large_exp_tol_jaw,
                                                  tolerance_small_tol_mlc, tolerance_medium_tol_mlc, tolerance_large_tol_mlc,
                                                  tolerance_small_tol_jaw, tolerance_medium_tol_jaw, tolerance_large_tol_jaw,
                                                  tolerance_iso_tol)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_fieldsize', method="POST")
def remove_tolerance_fieldsize():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_fieldsize(int(tol_id))
        return "Done!"
    except:
        return "Failed!"


################################ FIELD ROTATION ##############################
@admin_app.route('/edit_settings_fieldrotation', method="POST")
def edit_settings_fieldrotation():
    return template("edit_settings_fieldrotation")

@admin_app.route('/get_treatmentunits_fieldrotation', method="POST")
def get_treatmentunits_fieldrotation():
    json_string = []
    users = general_functions.get_treatmentunits_fieldrotation()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "Machine": users[a][1], "Beam": users[a][2]})
    return json.dumps(json_string)

@admin_app.route('/add_treatmentunit_fieldrotation', method="POST")
def add_treatmentunit_fieldrotation():
    machine = request.forms.Machine
    beam = request.forms.Beam
    try:
        general_functions.add_treatmentunit_fieldrotation(machine, beam)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"
    
@admin_app.route('/remove_treatmentunit_fieldrotation', method="POST")
def remove_treatmentunit_fieldrotation():
    unit_id = request.forms.unit_id
    if int(unit_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_treatmentunit_fieldrotation(int(unit_id))
        return "Done!"
    except:
        return "Failed!"
    
@admin_app.route('/get_settings_fieldrotation', method="POST")
def get_settings_fieldrotation():
    json_string = []
    users = general_functions.get_settings_fieldrotation()
    json_string.append({"Setting": "TOLERANCE_COLLABS", "Value": users[0]})
    json_string.append({"Setting": "TOLERANCE_COLLREL", "Value": users[1]})
    json_string.append({"Setting": "TOLERANCE_COUCHREL", "Value": users[2]})
    return json.dumps(json_string)

@admin_app.route('/get_tolerance_fieldrotation', method="POST")
def get_tolerance_fieldrotation():
    json_string = []
    users = general_functions.get_tolerance_fieldrotation()
    for a in range(len(users)):
        i = users[a]
        json_string.append({"Id":i[0], "Machine": i[1], "TOLERANCE_COLLABS": i[2], "TOLERANCE_COLLREL": i[3], "TOLERANCE_COUCHREL": i[4]})
    return json.dumps(json_string)

@admin_app.route('/update_settings_fieldrotation', method="POST")
def update_settings_fieldrotation():
    tolerance_collabs = request.forms.tolerance_collabs
    tolerance_collrel = request.forms.tolerance_collrel
    tolerance_couchrel = request.forms.tolerance_couchrel
    try:
        general_functions.update_settings_fieldrotation(tolerance_collabs, tolerance_collrel, tolerance_couchrel)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/add_tolerance_fieldrotation', method="POST")
def add_tolerance_fieldrotation():
    machine = request.forms.machine_tol
    tolerance_collabs_tol = request.forms.tolerance_collabs_tol
    tolerance_collrel_tol = request.forms.tolerance_collrel_tol
    tolerance_couchrel_tol = request.forms.tolerance_couchrel_tol
    try:
        general_functions.add_tolerance_fieldrotation(machine, tolerance_collabs_tol,
                                                      tolerance_collrel_tol, tolerance_couchrel_tol)
        return "Done!"
    except sql.IntegrityError:
        return "Unit already exists!"
    else:
        return "Failed"

@admin_app.route('/remove_tolerance_fieldrotation', method="POST")
def remove_tolerance_fieldrotation():
    tol_id = request.forms.tol_id
    if int(tol_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_tolerance_fieldrotation(int(tol_id))
        return "Done!"
    except:
        return "Failed!"

############################## MACHINE MAPPING ##############################
@admin_app.route('/edit_machine_mapping', method="POST")
def edit_machine_mapping():
    return template("edit_machine_mapping")

@admin_app.route('/get_mapping', method="POST")
def get_mapping():
    json_string = []
    users = general_functions.get_mapping()
    for a in range(len(users)):
        json_string.append({"id": users[a][0], "DicomName": users[a][1], "DicomEnergy":users[a][2],
                            "UserName": users[a][3],  "UserEnergy": users[a][4]})
    return json.dumps(json_string)

@admin_app.route('/add_mapping', method="POST")
def add_mapping():
    dicomname = request.forms.DicomName
    username = request.forms.UserName
    dicomenergy = request.forms.DicomEnergy
    userenergy = request.forms.UserEnergy
    try:
        general_functions.add_mapping(dicomname, dicomenergy, username, userenergy)
        return "Done!"
    except sql.IntegrityError:
        return "Mapping must be unique!"
    else:
        return "Failed"
    
@admin_app.route('/remove_mapping', method="POST")
def remove_mapping():
    mapping_id = request.forms.mapping_id
    if int(mapping_id) < 1:
        return "Failed!"
    try:
        general_functions.remove_mapping(int(mapping_id))
        return "Done!"
    except:
        return "Failed!"


############################# DYNALOG ###########################################
@admin_app.route('/edit_settings_dynalog', method="POST")
def edit_settings_dynalog():
    return template("edit_settings_dynalog")

@admin_app.route('/dynalog_start_batch_analysis', method=['POST'])
def dynalog_start_batch_analysis():
    
    if __name__ == '__main__' or parent_module.__name__ == '__main__':
        import analyze_dynalogs
    else:
        from . import analyze_dynalogs

    if not config.DYNALOG_ANALYSIS_IN_PROGRESS:
        config.DYNALOG_ANALYSIS_IN_PROGRESS = True
        try:
            analyze_dynalogs.start_the_analysis()
        except:
            config.DYNALOG_CURRENT_FOLDER_ANALYSIS = 0
            config.DYNALOG_CURRENT_PROGRESS = 0
            config.DYNALOG_ANALYSIS_IN_PROGRESS = False
            return "Error"
        config.DYNALOG_ANALYSIS_IN_PROGRESS = False
        config.DYNALOG_CURRENT_FOLDER_ANALYSIS = 0
        config.DYNALOG_CURRENT_PROGRESS = 0
    else:
        return "Analysis already running!"

@admin_app.route('/get_dynalog_analysis_status', method="POST")
def get_dynalog_analysis_status():
    variables = {
                 "in_progress": config.DYNALOG_ANALYSIS_IN_PROGRESS,
                 "current_folder": config.DYNALOG_CURRENT_FOLDER_ANALYSIS,
                 "current_file": config.DYNALOG_CURRENT_PROGRESS
                 }
    return json.dumps(variables)