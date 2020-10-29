import numpy as np
import warnings
import os, sys
import shutil
import sqlite3 as sql
from collections import defaultdict 

from passlib.context import CryptContext

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

from pylinac import Dynalog

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    import config
    import RestToolbox_modified as RestToolbox
else:
    from . import config
    from . import RestToolbox_modified as RestToolbox

def encrypt_password(password):
    return pwd_context.hash(password)

def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)

def get_configuration():
    return [config.QASERVER_VERSION,
            config.INSTITUTION,
            config.SECRET_KEY,
            config.REFERENCE_IMAGES_FOLDER,
            config.REFERENCE_IMAGES_FOLDER_NAME,
            config.WORKING_DIRECTORY,
            config.GENERAL_DATABASE,
            config.TRENDS_DATABASE,
            config.USERNAME_ORTHANC,
            config.PASSWORD_ORTHANC,
            config.ORTHANC_IP,
            config.ORTHANC_PORT,
            config.ORTHANC_URL,
            config.DYNALOG_DATABASE,
            config.DYNALOG_ARCHIVE,
            config.DYNALOG_FOLDER,
            config.DYNALOG_CONFIG,
            config.DYNALOG_FAILED,
            config.DYNALOG_ANALYSIS_IN_PROGRESS,
            config.TEMP_DCM_FOLDER,
            config.TEMP_NONDCM_FOLDER,
            config.PDF_REPORT_FOLDER,
            config.TEMP_DYNALOG_FOLDER,
            config.TEMP_DIRECTORY]

def set_configuration(cfg):
    [config.QASERVER_VERSION,
    config.INSTITUTION,
    config.SECRET_KEY,
    config.REFERENCE_IMAGES_FOLDER,
    config.REFERENCE_IMAGES_FOLDER_NAME,
    config.WORKING_DIRECTORY,
    config.GENERAL_DATABASE,
    config.TRENDS_DATABASE,
    config.USERNAME_ORTHANC,
    config.PASSWORD_ORTHANC,
    config.ORTHANC_IP,
    config.ORTHANC_PORT,
    config.ORTHANC_URL,
    config.DYNALOG_DATABASE,
    config.DYNALOG_ARCHIVE,
    config.DYNALOG_FOLDER,
    config.DYNALOG_CONFIG,
    config.DYNALOG_FAILED,
    config.DYNALOG_ANALYSIS_IN_PROGRESS,
    config.TEMP_DCM_FOLDER,
    config.TEMP_NONDCM_FOLDER,
    config.PDF_REPORT_FOLDER,
    config.TEMP_DYNALOG_FOLDER,
    config.TEMP_DIRECTORY] = cfg
    RestToolbox.SetCredentials(config.USERNAME_ORTHANC, config.PASSWORD_ORTHANC)


def get_users():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Name, Admin, DisplayName FROM Users ORDER BY Name")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def can_delete(user_id):
    # This function finds out if the (name) user exists and is the only admin
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE rowid = ? AND Admin = 'Yes')", (user_id,))
    user_exists = curs.fetchone()
    curs.execute("SELECT rowid FROM Users WHERE Admin = 'Yes'")
    data = curs.fetchall()
    curs.close()
    conn.close()
    if len(data)==1 and user_exists[0]==1:
        return False
    else:
        return True

def get_one_user(username):
    conn = sql.connect(config.GENERAL_DATABASE)
    conn.row_factory = sql.Row
    curs = conn.cursor()
    curs.execute("SELECT Name, Password, Admin, DisplayName FROM Users WHERE Name = ?", (username, ))
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def add_one_user(username, password, is_admin, displayname):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO Users (Name, Password, Admin, DisplayName) VALUES (?, ?, ?, ?)", (username, encrypt_password(password), is_admin, displayname))
    conn.commit()
    curs.close()
    conn.close()

def remove_one_user(user_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM Users WHERE rowid = ?", (user_id,) )
    conn.commit()
    curs.close()
    conn.close()

def check_is_admin(username):
    # This function finds out if the (name) user exists and is admin
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT Admin FROM Users WHERE Name = ?", (username,))
    data = curs.fetchone()
    curs.close()
    conn.close()
    if data[0] == "Yes":
        return True
    else:
        return False

############################# ORTHANC ####################################

def get_orthanc_settings():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT IP, Port, User, Password FROM Orthanc WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_orthanc_settings(IP, Port, User, Password):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE Orthanc SET IP=?, Port=?, User=?, Password=?"
                 "WHERE ROWID=1", (IP, Port, User, Password))
    conn.commit()
    curs.close()
    conn.close()
    config.ORTHANC_IP = IP
    config.ORTHANC_PORT = Port
    config.USERNAME_ORTHANC = User
    config.PASSWORD_ORTHANC = Password
    config.ORTHANC_URL = "http://"+str(IP) + ":" + str(Port)
    RestToolbox.SetCredentials(User, Password)

############################# INSTITUTION ####################################

def get_institution_settings():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT Name FROM Institution WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_institution_settings(Name):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE Institution SET Name=? "
                 "WHERE ROWID=1", (Name,))
    conn.commit()
    curs.close()
    conn.close()
    config.INSTITUTION = Name
    
############################## MACHINE MAPPING ############################

def get_mapping():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, DicomName, DicomEnergy, UserName, UserEnergy FROM MachineMapping ORDER BY DicomName")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_mapping(dicomname, dicomenergy, username, userenergy):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO MachineMapping (DicomName, DicomEnergy, UserName, UserEnergy) VALUES (?, ?, ?, ?)",
                 (dicomname, dicomenergy, username, userenergy))
    conn.commit()
    curs.close()
    conn.close()

def remove_mapping(mapping_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM MachineMapping WHERE rowid = ?", (mapping_id,) )
    conn.commit()
    curs.close()
    conn.close()


############################## WINSTON LUTZ#####################################

def get_treatmentunits_wl():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM WinstonLutzUnits ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_treatmentunit_wl(machine, beam):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO WinstonLutzUnits (Machine, Beam) VALUES (?, ?)", (machine, beam))
    conn.commit()
    curs.close()
    conn.close()

def remove_treatmentunit_wl(unit_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM WinstonLutzUnits WHERE rowid = ?", (unit_id, ) )
    conn.commit()
    curs.close()
    conn.close()
    
def get_settings_wl():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT PASS_RATE, SUCCESS_RATE, APPLY_TOLERANCE_TO_COLL_ASYM, COLL_ASYM_TOL, "
                 "BEAM_DEV_TOL, COUCH_DIST_TOL FROM WinstonLutzSettings WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_settings_wl(passrate, actionrate, collasym, coll_asym_tol, beam_dev_tol, couch_distance_tol):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE WinstonLutzSettings SET PASS_RATE=?, SUCCESS_RATE=?, APPLY_TOLERANCE_TO_COLL_ASYM=?, "
                 "COLL_ASYM_TOL=?, BEAM_DEV_TOL=?, COUCH_DIST_TOL=? WHERE ROWID=1", (passrate, actionrate, collasym, coll_asym_tol, beam_dev_tol, couch_distance_tol))
    conn.commit()
    curs.close()
    conn.close()
   
def get_tolerance_wl():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, PASS_RATE, SUCCESS_RATE, APPLY_TOLERANCE_TO_COLL_ASYM, COLL_ASYM_TOL, "
                 "BEAM_DEV_TOL, COUCH_DIST_TOL FROM WinstonLutzTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_wl(user_machine):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT PASS_RATE, SUCCESS_RATE, APPLY_TOLERANCE_TO_COLL_ASYM, COLL_ASYM_TOL, BEAM_DEV_TOL, "
                 "COUCH_DIST_TOL FROM WinstonLutzTolerance WHERE Machine=?", (user_machine,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_tolerance_wl(machine, passrate, actionrate, collasym, coll_asym_tol, beam_dev_tol, couch_distance_tol):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO WinstonLutzTolerance (Machine, PASS_RATE, SUCCESS_RATE, APPLY_TOLERANCE_TO_COLL_ASYM, "
                 "COLL_ASYM_TOL, BEAM_DEV_TOL, COUCH_DIST_TOL) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (machine, passrate, actionrate, collasym, coll_asym_tol, beam_dev_tol, couch_distance_tol))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_wl(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM WinstonLutzTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()

def get_phantoms_wl():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Phantom FROM WinstonLutzPhantoms")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_phantom_wl(phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO WinstonLutzPhantoms (Phantom) VALUES (?)", (phantom,))
    conn.commit()
    curs.close()
    conn.close()

def remove_phantom_wl(phantom_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM WinstonLutzPhantoms WHERE rowid = ? ", (phantom_id,) )
    conn.commit()
    curs.close()
    conn.close()
    
######################## STARSHOT ###########################################

def get_treatmentunits_starshot():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM StarshotUnits ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_treatmentunit_starshot(machine, beam):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO StarshotUnits (Machine, Beam) VALUES (?, ?)", (machine, beam))
    conn.commit()
    curs.close()
    conn.close()

def remove_treatmentunit_starshot(unit_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM StarshotUnits WHERE rowid = ?", (unit_id, ) )
    conn.commit()
    curs.close()
    conn.close()
    
def get_settings_starshot():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE, GENERATE_PDF_REPORT FROM StarshotSettings WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_settings_starshot(passrate, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE StarshotSettings SET TOLERANCE=?, GENERATE_PDF_REPORT=? WHERE ROWID=1", (passrate, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()
   
def get_tolerance_starshot():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, TOLERANCE, GENERATE_PDF_REPORT FROM StarshotTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_starshot(user_machine):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE, GENERATE_PDF_REPORT FROM StarshotTolerance WHERE Machine=?", (user_machine,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_tolerance_starshot(machine, passrate, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO StarshotTolerance (Machine, TOLERANCE, GENERATE_PDF_REPORT) VALUES (?, ?, ?)",
                 (machine, passrate, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_starshot(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM StarshotTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()

############################## PICKETFENCE #####################################

def get_treatmentunits_picketfence():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM PicketfenceUnits ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_treatmentunit_picketfence(machine, beam):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO PicketfenceUnits (Machine, Beam) VALUES (?, ?)", (machine, beam))
    conn.commit()
    curs.close()
    conn.close()

def remove_treatmentunit_picketfence(unit_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM PicketfenceUnits WHERE rowid = ?", (unit_id, ) )
    conn.commit()
    curs.close()
    conn.close()
    
def get_settings_picketfence():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT ACTION_TOLERANCE, TOLERANCE, GENERATE_PDF_REPORT FROM PicketfenceSettings WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_settings_picketfence(action_tolerance, tolerance, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE PicketfenceSettings SET ACTION_TOLERANCE=?, TOLERANCE=?, GENERATE_PDF_REPORT=? "
                 "WHERE ROWID=1", (action_tolerance, tolerance, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()
   
def get_tolerance_picketfence():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, ACTION_TOLERANCE, TOLERANCE, GENERATE_PDF_REPORT "
                 "FROM PicketfenceTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_picketfence(user_machine):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT ACTION_TOLERANCE, TOLERANCE, GENERATE_PDF_REPORT "
                 "FROM PicketfenceTolerance WHERE Machine=?", (user_machine,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_tolerance_picketfence(machine, action_tolerance, tolerance, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO PicketfenceTolerance (Machine, ACTION_TOLERANCE, TOLERANCE, GENERATE_PDF_REPORT"
                 ") VALUES (?, ?, ?, ?)",
                 (machine, action_tolerance, tolerance, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_picketfence(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM PicketfenceTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()

############################## PLANAR IMAGING#####################################

def get_tolerance_planarimaging():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam, Phantom, LOW_THRESHOLD, HIGH_THRESHOLD, GENERATE_PDF_REPORT "
                 "FROM PlanarImagingTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_treatmentunits_planarimaging(phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM PlanarImagingTolerance WHERE Phantom=? ORDER BY Machine", (phantom,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_planarimaging(machine, beam, phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT LOW_THRESHOLD, HIGH_THRESHOLD, GENERATE_PDF_REPORT "
                 "FROM PlanarImagingTolerance WHERE Machine=? AND Beam=? AND Phantom=?",
                 (machine, beam, phantom))
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def add_tolerance_planarimaging(machine, beam, phantom, low_threshold, high_threshold, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO PlanarImagingTolerance (Machine, Beam, Phantom, LOW_THRESHOLD, "
                 "HIGH_THRESHOLD, GENERATE_PDF_REPORT) VALUES (?, ?, ?, ?, ?, ?)",
                 (machine, beam, phantom, low_threshold, high_threshold, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_planarimaging(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM PlanarImagingTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()

def get_referenceimages_planarimaging():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam, Phantom, Path "
                 "FROM PlanarImagingReferenceImages")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_referenceimagepath_planarimaging(machine, beam, phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT Path FROM PlanarImagingReferenceImages "
                 "WHERE Machine=? AND Beam=? AND Phantom=?",
                 (machine, beam, phantom))
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def has_referenceimages_planarimaging(machine, beam, phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT EXISTS(SELECT 1 FROM PlanarImagingReferenceImages WHERE Machine=? "
                 "AND Beam=? AND Phantom=?)", (machine, beam, phantom))
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def add_referenceimage_planarimaging(machine, beam, phantom, orthanc_instance):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO PlanarImagingReferenceImages (Machine, Beam, Phantom, Path"
                 ") VALUES (?, ?, ?, ?)",
                 (machine, beam, phantom, orthanc_instance))
    conn.commit()
    curs.close()
    conn.close()

def remove_referenceimage_planarimaging(ref_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM PlanarImagingReferenceImages WHERE rowid = ?", (ref_id,) )
    conn.commit()
    curs.close()
    conn.close()


############################## CATPHAN #####################################
def get_tolerance_catphan():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam, Phantom, HU, LCV, SCALING, THICKNESS, "
                 "LOWCONTRAST, CNR, MTF, UNIFORMITYIDX, GENERATE_PDF_REPORT FROM CatphanTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_treatmentunits_catphan(phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM CatphanTolerance WHERE Phantom=? ORDER BY Machine", (phantom,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_catphan(machine, beam, phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT HU, LCV, SCALING, THICKNESS, LOWCONTRAST, CNR, MTF, UNIFORMITYIDX, GENERATE_PDF_REPORT "
                 "FROM CatphanTolerance WHERE Machine=? AND Beam=? AND Phantom=?",
                 (machine, beam, phantom))
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def add_tolerance_catphan(machine, beam, phantom, hu, lcv, scaling, thickness,
                          lowcontrast, cnr, mtf, uniformityidx, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO CatphanTolerance (Machine, Beam, Phantom, HU, LCV, "
                 "SCALING, THICKNESS, LOWCONTRAST, CNR, MTF, UNIFORMITYIDX, GENERATE_PDF_REPORT) VALUES "
                 "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (machine, beam, phantom, hu, lcv, scaling, thickness,
                  lowcontrast, cnr, mtf, uniformityidx, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_catphan(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM CatphanTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()

def get_referenceimages_catphan():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam, Phantom, Path "
                 "FROM CatphanReferenceImages")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_referenceimagepath_catphan(machine, beam, phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT Path FROM CatphanReferenceImages "
                 "WHERE Machine=? AND Beam=? AND Phantom=?",
                 (machine, beam, phantom))
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def has_referenceimages_catphan(machine, beam, phantom):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT EXISTS(SELECT 1 FROM CatphanReferenceImages WHERE Machine=? "
                 "AND Beam=? AND Phantom=?)", (machine, beam, phantom))
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def add_referenceimage_catphan(machine, beam, phantom, orthanc_series):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO CatphanReferenceImages (Machine, Beam, Phantom, Path"
                 ") VALUES (?, ?, ?, ?)",
                 (machine, beam, phantom, orthanc_series))
    conn.commit()
    curs.close()
    conn.close()

def remove_referenceimage_catphan(ref_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM CatphanReferenceImages WHERE rowid = ?", (ref_id,) )
    conn.commit()
    curs.close()
    conn.close()


######################## FLATSYM ###########################################

def get_treatmentunits_flatsym():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM FlatSymUnits ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_treatmentunit_flatsym(machine, beam):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO FlatSymUnits (Machine, Beam) VALUES (?, ?)", (machine, beam))
    conn.commit()
    curs.close()
    conn.close()

def remove_treatmentunit_flatsym(unit_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM FlatSymUnits WHERE rowid = ?", (unit_id, ) )
    conn.commit()
    curs.close()
    conn.close()
    
def get_settings_flatsym():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE_FLAT, TOLERANCE_SYM, GENERATE_PDF_REPORT FROM FlatSymSettings WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_settings_flatsym(tolerance_flat, tolerance_sym, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE FlatSymSettings SET TOLERANCE_FLAT=?, TOLERANCE_SYM=?, GENERATE_PDF_REPORT=? WHERE ROWID=1", (tolerance_flat, tolerance_sym, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()
   
def get_tolerance_flatsym():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, TOLERANCE_FLAT, TOLERANCE_SYM, GENERATE_PDF_REPORT FROM FlatSymTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_flatsym(user_machine):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE_FLAT, TOLERANCE_SYM, GENERATE_PDF_REPORT FROM FlatSymTolerance WHERE Machine=?", (user_machine,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_tolerance_flatsym(machine, tolerance_flat, tolerance_sym, generate_pdf_tol):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO FlatSymTolerance (Machine, TOLERANCE_FLAT, TOLERANCE_SYM, GENERATE_PDF_REPORT) VALUES (?, ?, ?, ?)",
                 (machine, tolerance_flat, tolerance_sym, generate_pdf_tol))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_flatsym(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM FlatSymTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()

######################## VMAT ###########################################

def get_treatmentunits_vmat():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM VmatUnits ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_treatmentunit_vmat(machine, beam):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO VmatUnits (Machine, Beam) VALUES (?, ?)", (machine, beam))
    conn.commit()
    curs.close()
    conn.close()

def remove_treatmentunit_vmat(unit_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM VmatUnits WHERE rowid = ?", (unit_id, ) )
    conn.commit()
    curs.close()
    conn.close()
    
def get_settings_vmat():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE, GENERATE_PDF_REPORT FROM VmatSettings WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_settings_vmat(tolerance, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE VmatSettings SET TOLERANCE=?, GENERATE_PDF_REPORT=? WHERE ROWID=1", (tolerance, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()
   
def get_tolerance_vmat():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, TOLERANCE, GENERATE_PDF_REPORT FROM VmatTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_vmat(user_machine):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE, GENERATE_PDF_REPORT FROM VmatTolerance WHERE Machine=?", (user_machine,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_tolerance_vmat(machine, tolerance, generate_pdf):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO VmatTolerance (Machine, TOLERANCE, GENERATE_PDF_REPORT) VALUES (?, ?, ?)",
                 (machine, tolerance, generate_pdf))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_vmat(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM VmatTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()


############################## FIELDSIZE #####################################

def get_treatmentunits_fieldsize():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM FieldSizeUnits ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_treatmentunit_fieldsize(machine, beam):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO FieldSizeUnits (Machine, Beam) VALUES (?, ?)", (machine, beam))
    conn.commit()
    curs.close()
    conn.close()

def remove_treatmentunit_fieldsize(unit_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM FieldSizeUnits WHERE rowid = ?", (unit_id, ) )
    conn.commit()
    curs.close()
    conn.close()
    
def get_settings_fieldsize():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT SMALL_NOMINAL, MEDIUM_NOMINAL, LARGE_NOMINAL, "
                 "SMALL_EXP_MLC, MEDIUM_EXP_MLC, LARGE_EXP_MLC, "
                 "SMALL_EXP_JAW, MEDIUM_EXP_JAW, LARGE_EXP_JAW, "
                 "TOLERANCE_SMALL_MLC, TOLERANCE_MEDIUM_MLC, TOLERANCE_LARGE_MLC, "
                 "TOLERANCE_SMALL_JAW, TOLERANCE_MEDIUM_JAW, TOLERANCE_LARGE_JAW, "
                 "TOLERANCE_ISO FROM FieldSizeSettings WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_settings_fieldsize(small_nominal, medium_nominal, large_nominal,
                              small_exp_mlc, medium_exp_mlc, large_exp_mlc,
                              small_exp_jaw, medium_exp_jaw, large_exp_jaw,
                              tolerance_small_mlc, tolerance_medium_mlc, tolerance_large_mlc,
                              tolerance_small_jaw, tolerance_medium_jaw, tolerance_large_jaw,
                              tolerance_iso):

    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE FieldSizeSettings SET SMALL_NOMINAL=?, MEDIUM_NOMINAL=?, LARGE_NOMINAL=?, "
                 "SMALL_EXP_MLC=?, MEDIUM_EXP_MLC=?, LARGE_EXP_MLC=?, "
                 "SMALL_EXP_JAW=?, MEDIUM_EXP_JAW=?, LARGE_EXP_JAW=?, "
                 "TOLERANCE_SMALL_MLC=?, TOLERANCE_MEDIUM_MLC=?, TOLERANCE_LARGE_MLC=?, "
                 "TOLERANCE_SMALL_JAW=?, TOLERANCE_MEDIUM_JAW=?, TOLERANCE_LARGE_JAW=?, "
                 "TOLERANCE_ISO=? WHERE ROWID=1",
                 (small_nominal, medium_nominal, large_nominal,
                  small_exp_mlc, medium_exp_mlc, large_exp_mlc,
                  small_exp_jaw, medium_exp_jaw, large_exp_jaw,
                  tolerance_small_mlc, tolerance_medium_mlc, tolerance_large_mlc,
                  tolerance_small_jaw, tolerance_medium_jaw, tolerance_large_jaw,
                  tolerance_iso))
    conn.commit()
    curs.close()
    conn.close()
   
def get_tolerance_fieldsize():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, SMALL_NOMINAL, MEDIUM_NOMINAL, LARGE_NOMINAL, "
                 "SMALL_EXP_MLC, MEDIUM_EXP_MLC, LARGE_EXP_MLC, "
                 "SMALL_EXP_JAW, MEDIUM_EXP_JAW, LARGE_EXP_JAW, "
                 "TOLERANCE_SMALL_MLC, TOLERANCE_MEDIUM_MLC, TOLERANCE_LARGE_MLC, "
                 "TOLERANCE_SMALL_JAW, TOLERANCE_MEDIUM_JAW, TOLERANCE_LARGE_JAW, "
                 "TOLERANCE_ISO FROM FieldSizeTolerance ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_fieldsize(user_machine):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT SMALL_NOMINAL, MEDIUM_NOMINAL, LARGE_NOMINAL, "
                 "SMALL_EXP_MLC, MEDIUM_EXP_MLC, LARGE_EXP_MLC, "
                 "SMALL_EXP_JAW, MEDIUM_EXP_JAW, LARGE_EXP_JAW, "
                 "TOLERANCE_SMALL_MLC, TOLERANCE_MEDIUM_MLC, TOLERANCE_LARGE_MLC, "
                 "TOLERANCE_SMALL_JAW, TOLERANCE_MEDIUM_JAW, TOLERANCE_LARGE_JAW, "
                 "TOLERANCE_ISO FROM FieldSizeTolerance WHERE Machine=?", (user_machine,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_tolerance_fieldsize(machine, small_nominal, medium_nominal, large_nominal,
                            small_exp_mlc, medium_exp_mlc, large_exp_mlc,
                            small_exp_jaw, medium_exp_jaw, large_exp_jaw,
                            tolerance_small_mlc, tolerance_medium_mlc, tolerance_large_mlc,
                            tolerance_small_jaw, tolerance_medium_jaw, tolerance_large_jaw,
                            tolerance_iso):
    
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO FieldSizeTolerance (Machine, SMALL_NOMINAL, MEDIUM_NOMINAL, LARGE_NOMINAL, "
                 "SMALL_EXP_MLC, MEDIUM_EXP_MLC, LARGE_EXP_MLC, "
                 "SMALL_EXP_JAW, MEDIUM_EXP_JAW, LARGE_EXP_JAW, "
                 "TOLERANCE_SMALL_MLC, TOLERANCE_MEDIUM_MLC, TOLERANCE_LARGE_MLC, "
                 "TOLERANCE_SMALL_JAW, TOLERANCE_MEDIUM_JAW, TOLERANCE_LARGE_JAW, "
                 "TOLERANCE_ISO) VALUES "
                 "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (machine, small_nominal, medium_nominal, large_nominal,
                  small_exp_mlc, medium_exp_mlc, large_exp_mlc,
                  small_exp_jaw, medium_exp_jaw, large_exp_jaw,
                  tolerance_small_mlc, tolerance_medium_mlc, tolerance_large_mlc,
                  tolerance_small_jaw, tolerance_medium_jaw, tolerance_large_jaw,
                  tolerance_iso))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_fieldsize(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM FieldSizeTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()


############################## FIELD ROTATION #################################

def get_treatmentunits_fieldrotation():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, Beam FROM FieldRotationUnits ORDER BY Machine")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_treatmentunit_fieldrotation(machine, beam):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO FieldRotationUnits (Machine, Beam) VALUES (?, ?)", (machine, beam))
    conn.commit()
    curs.close()
    conn.close()

def remove_treatmentunit_fieldrotation(unit_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM FieldRotationUnits WHERE rowid = ?", (unit_id, ) )
    conn.commit()
    curs.close()
    conn.close()
    
def get_settings_fieldrotation():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE_COLLABS, TOLERANCE_COLLREL, TOLERANCE_COUCHREL FROM FieldRotationSettings WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data

def update_settings_fieldrotation(tolerance_collabs, tolerance_collrel, tolerance_couchrel):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("UPDATE FieldRotationSettings SET TOLERANCE_COLLABS=?, TOLERANCE_COLLREL=?, TOLERANCE_COUCHREL=? "
                 "WHERE ROWID=1", (tolerance_collabs, tolerance_collrel, tolerance_couchrel))
    conn.commit()
    curs.close()
    conn.close()
   
def get_tolerance_fieldrotation():
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT rowid, Machine, TOLERANCE_COLLABS, TOLERANCE_COLLREL, TOLERANCE_COUCHREL "
                 "FROM FieldRotationTolerance")
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def get_tolerance_user_machine_fieldrotation(user_machine):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT TOLERANCE_COLLABS, TOLERANCE_COLLREL, TOLERANCE_COUCHREL "
                 "FROM FieldRotationTolerance WHERE Machine=?", (user_machine,))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

def add_tolerance_fieldrotation(machine, tolerance_collabs, tolerance_collrel, tolerance_couchrel):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO FieldRotationTolerance (Machine, TOLERANCE_COLLABS, TOLERANCE_COLLREL, TOLERANCE_COUCHREL"
                 ") VALUES (?, ?, ?, ?)",
                 (machine, tolerance_collabs, tolerance_collrel, tolerance_couchrel))
    conn.commit()
    curs.close()
    conn.close()

def remove_tolerance_fieldrotation(tol_id):
    conn = sql.connect(config.GENERAL_DATABASE)
    curs = conn.cursor()
    curs.execute("DELETE FROM FieldRotationTolerance WHERE rowid = ?", (tol_id,) )
    conn.commit()
    curs.close()
    conn.close()


########################## VARIOUS FUNCTIONS ############################
def get_energy_from_imgdescription(imgdescription):
    if imgdescription=="Not available" or imgdescription=="" or imgdescription==None:
        return None
    else:
        return imgdescription.splitlines()[0].split(",")[0]

def get_user_machine_and_energy(dicomname, dicomenergy):
    # Get user names from dicom names
    mapping = get_mapping()
    username = ""
    userenergy = ""
    for m in mapping:
        if m[1]==dicomname:
            username=m[3]  # repeats if energy not found. Bad but works
            if m[2]==dicomenergy:
                userenergy=m[4]
                break
    return [username, userenergy]

def get_machines_and_energies(module_list):
    # Group machine/energiy list
    res = defaultdict(list) 
    for item in module_list:
        key = item[1]
        res[key].append(item[2])
    final_list = []
    for key in res:
        temp = []
        for val in res[key]:
            temp.append(val)
        final_list.append([key, temp])
    return final_list

def delete_files_in_subfolders(file_paths):
    # Function for deleting images after transfer - subfolders

    for ff in file_paths:
        try:
            shutil.rmtree(ff)
        except:
            warnings.warn(ff + " could not be deleted")
            continue

def Read_from_dcm_database():
    # Function that reads from the orthanc database and gives a list of patients.

    p = RestToolbox.GetPatientIds(config.ORTHANC_URL)
    data = RestToolbox.GetPatientData(config.ORTHANC_URL, p)

    names = []
    IDs = []
    if len(data) != 0:
        for d in data:
            try:
                names.append(d["MainDicomTags"]["PatientName"].replace("^", " "))
            except:
                names.append("UnknownPatient")
            try:
                IDs.append(d["MainDicomTags"]["PatientID"])
            except:
                IDs.append("UnknownPatientID")
    
        order = np.array(sorted(range(len(names)), key=names.__getitem__))

        # Add empty first lines for dropdowns (so that you can use onchange event in js)

        variables = {"orthanc_id": ["FirstLineEmptyLineFromJavascriptPatient"] + list(np.array(p)[order]),
                     "names": ["-----------"] + list(np.array(names)[order]),
                     "IDs": ["--"] + list(np.array(IDs)[order]),
                     "orthanc_url": config.ORTHANC_URL,
                     "institution": config.INSTITUTION
                     }
    else:
        variables = {"orthanc_id": [],
                     "names": [],
                     "IDs": [],
                     "orthanc_url": config.ORTHANC_URL,
                     "institution": config.INSTITUTION
                     }
    return variables

def get_contenttime_seccheck_wl(dicomfile):
    # This function is used for consistency check. It returns content date/time
    # and instance number or image label for a specified dicom file
    metadata = dicomfile.metadata
    date_var = ""
    time_var = ""
    label = ""
    try:
        date_var = metadata.ContentDate
        time_var = metadata.ContentTime
    except:
        date_var = "Unknown ContentDate"
        time_var = "Unknown ContentTime"
    try:
        manufact = metadata.Manufacturer
    except:
        manufact = "Undefined"
    if manufact in ["Varian Medical Systems"]:
        label = metadata.RTImageLabel
    else:
        label = metadata.InstanceNumber
    return date_var, time_var, label


def delete_figure(fig_list):
    # Function for deleting matplotlib figures
    for f in fig_list:
        f.clf()

def clip_around_image(img, clip_box):
    # Function that forces edges of the images to have background values
    img_size = img.shape
    phy_size = img.physical_shape
    background = img.array.min()
    if clip_box != 0:
        if (clip_box > phy_size[0]) or (clip_box > phy_size[1]):
            raise ValueError("Clipbox larger than the image itself")
        n_tb = int((img_size[0] - clip_box*img.dpmm)/2)  # Top bottom edge
        n_lr = int((img_size[1] - clip_box*img.dpmm)/2)  # Left right edge
        img.array[:, 0:n_lr] = background
        img.array[:, -n_lr:] = background
        img.array[0:n_tb, :] = background
        img.array[-n_tb:, :] = background

def MLCpositions_to_points(posA, posB, widths):
    # Converting MLC positions from dynalog files to cartesian points.
    # posA and posB are arrays of leaf positions
    # widths is an array of leaf horizontal edge positions, ranging from
    # bottom (y1) to top (y2)
    # Returns edge points for Bank A and Bank B seperately.
    if posA.shape[0] != widths.shape[0]-1:
        raise ValueError("Number of leaves does not match the MLC model")
    widths = np.vstack((np.vstack((widths[0], np.repeat(widths[1:-1], 2, axis=0))), widths[-1]))
    posA = np.repeat(posA, 2, axis=0)
    posB = np.repeat(posB, 2, axis=0)
    return [np.column_stack((posA, widths)), np.column_stack((posB, widths))]

def get_dataset_from_dlg(file, exclude_beam_off):

    if not os.path.isfile(file):
        raise ValueError("File "+file+" does not exist.")
    try:
        plg = Dynalog(file, exclude_beam_off=exclude_beam_off)
    except:
        raise ValueError("Cannot read dynalog file. Unknown problem.")

    return plg  # Read dlg file

class VarianDynalog(object):

    # input file path (must be .dlg or .DLG) of your dynalog
    def __init__(self, ds):

        self.log = ds

        if ds.header.plan_filename:
            if len(ds.header.plan_filename) == 2:
                self.plan_UID, self.beam_id = ds.header.plan_filename
            else:
                self.plan_UID = ds.header.plan_filename[0]
                self.beam_id = ds.header.plan_filename[0]
        else:
            self.plan_UID = "NA"
            self.beam_id = "NA"

        if ds.header.patient_name:
            self.patient_name = ds.header.patient_name
        else:
            self.patient_name = "NA"

        if ds.header.tolerance:
            self.tolerance = ds.header.tolerance
        else:
            self.tolerance = "NA"

        # Scale (important for zero of gantry/collimator angle)
        IEC = ds.header.clinac_scale
        if IEC == 0:
            self.scale = "Varian IEC"
        elif IEC == 1:
            self.scale = "IEC 60601-2-1"  # G 180  == 0

        self.number_of_leaves = int(ds.header.num_mlc_leaves)
        self.number_of_snapshots = int(ds.axis_data.num_snapshots)  # All snapshots!

        # Time line in seconds:
        self.time_line = np.arange(0, self.number_of_snapshots, 1)*0.05

        # Convert to Varian IEC
        gantry = ds.axis_data.gantry.actual
        collimator = ds.axis_data.collimator.actual
        if self.scale == "IEC 60601-2-1":
            for g in np.arange(0, self.number_of_snapshots, 1):
                if 180 - gantry[g] >= 0:
                    gantry[g] = 180 - gantry[g]
                else:
                    gantry[g] = 540 - gantry[g]

                if 180 - collimator[g] >= 0:
                    collimator[g] = 180 - collimator[g]
                else:
                    collimator[g] = 540 - collimator[g]
        self.gantry = gantry
        self.collimator = collimator

        mu = ds.axis_data.mu.actual
        self.mu = mu - mu[0]
        mu2 = ds.axis_data.mu.expected
        self.mu_expected = mu2 - mu2[0]

        self.beam_on = ds.axis_data.beam_on.actual
        self.beam_hold = ds.axis_data.beam_hold.actual
        self.num_beamholds = ds.num_beamholds

        self.x1 = -ds.axis_data.jaws.x1.actual
        self.x2 = ds.axis_data.jaws.x2.actual
        self.y1 = -ds.axis_data.jaws.y1.actual
        self.y2 = ds.axis_data.jaws.y2.actual

        # Read MLC positions:
        bankA_actual = []
        bankB_actual = []
        bankA_expected = []
        bankB_expected = []

        MLC = ds.axis_data.mlc.leaf_axes
        self.MLC_number = int(len(MLC))
        for k in np.arange(1, int(self.MLC_number/2+1), 1):
            bankA_actual.append(MLC[k].actual)
            bankB_actual.append(-MLC[self.MLC_number/2+k].actual)
            bankA_expected.append(MLC[k].expected)
            bankB_expected.append(-MLC[self.MLC_number/2+k].expected)

        self.bankA_actual = bankA_actual
        self.bankB_actual = bankB_actual
        self.bankA_expected = bankA_expected
        self.bankB_expected = bankB_expected

        self.carriageA_actual = ds.axis_data.carriage_A.actual
        self.carriageB_actual = ds.axis_data.carriage_B.actual

    def analyze_dynalog(self, DTA, DD, threshold, resolution):

        mlc_num = self.number_of_leaves
        num_snap = self.number_of_snapshots
        self.log.fluence.gamma.calc_map(doseTA=DD, distTA=DTA, threshold=threshold, resolution=resolution)
        gamma = [self.log.fluence.gamma.avg_gamma, self.log.fluence.gamma.pass_prcnt]
        gamma = [gamma[0] if np.isfinite(gamma[0]) else -1, gamma[1] if np.isfinite(gamma[1]) else -1]
        beam_on_temp = self.beam_on
        beam_hold_temp = self.beam_hold
        bankA_actual = np.array(self.bankA_actual).reshape(int(mlc_num/2), num_snap)
        bankB_actual = np.array(self.bankB_actual).reshape(int(mlc_num/2), num_snap)
        bankA_expected = np.array(self.bankA_expected).reshape(int(mlc_num/2), num_snap)
        bankB_expected = np.array(self.bankB_expected).reshape(int(mlc_num/2), num_snap)

        diffA = bankA_actual - bankA_expected
        diffB = bankB_actual - bankB_expected

        rmsA = np.sqrt(np.mean(np.square(diffA[:, beam_on_temp==1]), axis=1))
        rmsB = np.sqrt(np.mean(np.square(diffB[:, beam_on_temp==1]), axis=1))

        rmsA_hold = np.sqrt(np.mean(np.square(diffA[:, (beam_on_temp==1)&(beam_hold_temp==0)]), axis=1))
        rmsB_hold = np.sqrt(np.mean(np.square(diffB[:, (beam_on_temp==1)&(beam_hold_temp==0)]), axis=1))

        diff_max_on = np.max([np.max(np.abs(diffA[:, beam_on_temp==1])), np.max(np.abs(diffB[:, beam_on_temp==1]))])
        diff_max_hold = np.max([np.max(np.abs(diffA[:, (beam_on_temp==1)&(beam_hold_temp==0)])),
                                        np.max(np.abs(diffB[:, (beam_on_temp==1)&(beam_hold_temp==0)]))])

        return {
                "gamma": gamma,
                "rms_max_on": np.max([rmsA, rmsB]),
                "rms_max_hold": np.max([rmsA_hold, rmsB_hold]),
                "diff_max_on": diff_max_on,
                "diff_max_hold": diff_max_hold,
                "rms_avg": self.log.axis_data.mlc.get_RMS_avg(bank='both', only_moving_leaves=True)
                }
