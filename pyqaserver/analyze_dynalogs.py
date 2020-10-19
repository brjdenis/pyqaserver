import sys
import datetime
import os
import zipfile
from shutil import copyfile
import tempfile
import sqlite3 as sql
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pandas as pd

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    import config
    import general_functions
else:
    from . import config
    from . import general_functions

# Load configuration from config.ini
CONFIG = configparser.ConfigParser()
CONFIG.read(config.DYNALOG_CONFIG)

PATHS = [os.path.abspath((k.strip())) for k in CONFIG["Dynalog"]["DYNALOG_REPOSITORIES"].split(",")]
PATH_LABELS = [k.strip() for k in CONFIG["Dynalog"]["REPOSITORIES_LABELS"].split(",")]
FOLDERS = {}
for i in range(0, len(PATHS), 1):
    FOLDERS[PATHS[i]] = PATH_LABELS[i]

DYNALOG_DATABASE = config.DYNALOG_DATABASE
CURRENT_MONTH = datetime.datetime.today().strftime("%Y-%m")
CURRENT_DATE = datetime.datetime.today().strftime("%Y-%m-%d")
ZIP_ARCHIVE = os.path.join(config.DYNALOG_ARCHIVE, CURRENT_MONTH + ".zip")
LOG_FILE = os.path.join(config.DYNALOG_FOLDER, "log.txt")
TEMP_FAILED_FOLDER = config.DYNALOG_FAILED

TOLERANCE_DTA = float(CONFIG["Dynalog"]["TOLERANCE_DTA"])
TOLERANCE_DD = float(CONFIG["Dynalog"]["TOLERANCE_DD"])
RESOLUTION = float(CONFIG["Dynalog"]["RESOLUTION"])
THRESHOLD = float(CONFIG["Dynalog"]["THRESHOLD"])
GAMMA_TOL_STR = str(TOLERANCE_DD)+" / "+str(TOLERANCE_DTA)+" / "+str(THRESHOLD)+" / "+str(RESOLUTION)

EXCLUDE_BEAM_OFF = True if CONFIG["Dynalog"]["EXCLUDE_BEAM_OFF"]=="True" else False
SEND_EMAIL = True if CONFIG["Dynalog"]["SEND_EMAIL"]=="True" else False

def copy_dynalogs(folder):
    temp_folder = tempfile.mkdtemp(prefix=CURRENT_DATE+"_", dir=TEMP_FAILED_FOLDER)
    for k in folder:
        path = os.path.dirname(k)
        file = os.path.basename(k)
        copyfile(os.path.join(path, "A"+file), os.path.join(temp_folder, "A"+file))
        copyfile(os.path.join(path, "B"+file), os.path.join(temp_folder, "B"+file))

def write_to_log(message):
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(message+"\n")
    except:
        return

def write_to_zipfile(dyn_A, dyn_B, path):
    with zipfile.ZipFile(ZIP_ARCHIVE, 'a', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(path, dyn_A), dyn_A)
        zipf.write(os.path.join(path, dyn_B), dyn_B)

def write_to_sql(data):
    
    conn = sql.connect(DYNALOG_DATABASE)
    curs = conn.cursor()
    curs.execute("INSERT INTO VarianDynalog(FileName, ZipArchive, PatientID, "\
                 "PatientName, PatientLastName, Date, Time, BeamID, Snapshots, "\
                 "Beamholds, RMSmax, RMSmax2, DIFFmax, DIFFmax2, RMSAvg, GammaAvg, "\
                 "GammaIndex, Gantry, GammaTol, DateEntered, Repository, "\
                 "ext1, ext2, ext3, ext4, ext5) "\
                 "VALUES ('"+data["filename"]+"','"+os.path.basename(ZIP_ARCHIVE)\
                 +"','"+data["ID"]+"','" + data["patientname"][1]+"','"+data["patientname"][0]\
                 +"','"+str(data["dateandtime"].date())+"','"+str(data["dateandtime"].time())\
                 +"','"+str(data["beam_id"])+"',"+ "{},{},{},{},{},{},{},{},{},{}".format(
                  data["num_snapshots"], data["num_beamholds"], round(data["rms_max_on"], 4),
                  round(data["rms_max_hold"], 4), round(data["diff_max_on"], 4),
                  round(data["diff_max_hold"], 4),  round(data["rms_avg"], 4), round(data["gamma"][0], 2),
                  round(data["gamma"][1], 2), round(data["gantry"], 1))\
                     +", '"+GAMMA_TOL_STR +"', '"+CURRENT_DATE+"', '"+data["folder"]+"', "\
                     "'', '', '', '', '')"
                  )
    conn.commit()
    curs.close()
    conn.close()

def analyze(path, file):

    log = general_functions.VarianDynalog(general_functions.get_dataset_from_dlg(file, exclude_beam_off=EXCLUDE_BEAM_OFF))
    calculations = log.analyze_dynalog(TOLERANCE_DTA, TOLERANCE_DD, THRESHOLD, RESOLUTION)

    time = os.path.basename(file)[1:].split("_")[0]
    dateandtime = datetime.datetime.strptime(str(time), '%Y%m%d%H%M%S')

    return {
            "filename": os.path.splitext(os.path.basename(file))[0][1:],
            "folder": FOLDERS[path],
            "ID": log.patient_name[2],
            "patientname": log.patient_name,
            #"patientname": ["Blanked", "Blanked"],  #Changed so that there is no patient name in the database
            "mlc_num": log.number_of_leaves,
            "beam_id": log.beam_id,
            "num_snapshots": int(log.number_of_snapshots),
            "gamma": calculations["gamma"],
            "num_beamholds": int(log.num_beamholds),
            "rms_max_on": calculations["rms_max_on"],
            "rms_max_hold": calculations["rms_max_hold"],
            "diff_max_on": calculations["diff_max_on"],
            "diff_max_hold": calculations["diff_max_hold"],
            "rms_avg": calculations["rms_avg"],
            "dateandtime": dateandtime,
            "gantry": log.gantry[0]
            }
   
def start_the_analysis():
    print("Job started.")
    dynalogs_final = []
    dynalogs_towrite_final = 0
    failed_dynalogs = []  # Those that were not processed correctly
    all_dynalogs = 0
    
    for path in PATHS:
        
        # First get all the files in the list
        write_to_log("\n===============================================")
        write_to_log("\nStart at: "+str(datetime.datetime.now())+".\n")
        write_to_log("Gathering files in " + path+".")
        print("Searching in "+path + ".")
        print("Gathering files that can be analyzed.")

        files_A = []
        files_B = []
        
        all_files = os.listdir(path)
        
        for filename in all_files:
            if os.path.splitext(filename)[1] in [".dlg", ".DLG"]:
                if filename[0] == "A":
                    files_A.append(filename[1:])
                elif filename[0] == "B":
                    files_B.append(filename[1:])
        
        # Get dynalogs that have both A and B files:
        cross = list(set(files_A) & set(files_B))
        all_dynalogs += len(cross)

        print("Done gathering files. Checking if records already exist.")

        # check which dynalogs can be written:
        write_to_log("Checking which files can be added to the database.")
        
        dynalogs_towrite = []
        conn = sql.connect(DYNALOG_DATABASE)
        curs = conn.cursor()
        for f in cross:
            curs.execute("SELECT EXISTS (SELECT 1 FROM VarianDynalog WHERE FileName='" + os.path.splitext(f)[0] + "')")
            rows = curs.fetchone()
            if rows[0] == 0:
                dynalogs_towrite.append(f)
        curs.close()
        conn.close()

        dynalogs_towrite_final += len(dynalogs_towrite)

        write_to_log(str(len(dynalogs_towrite)) + " dynalogs are to be analyzed and saved to database.")
        write_to_log(str(len(cross)-len(dynalogs_towrite)) + " dynalogs will be skiped.")
        print(str(len(dynalogs_towrite)) + " dynalogs are to be analyzed and saved to database.")
        print(str(len(cross)-len(dynalogs_towrite)) + " dynalogs will be skiped.")
        
        config.DYNALOG_CURRENT_FOLDER_ANALYSIS = path
        i = 1
        length_an = len(dynalogs_towrite)
        for dynalog in dynalogs_towrite:
            config.DYNALOG_CURRENT_PROGRESS = round(100*i/length_an, 2)
            i += 1
            
            try:
                analysis = analyze(path, os.path.join(path, "A"+dynalog))
                print(dynalog)
            except Exception as e:
                write_to_log("Analysis failed for " + dynalog +". "+str(e))
                print("Cannot analyze " + dynalog+". "+str(e))
                failed_dynalogs.append(os.path.join(path, dynalog))
                continue
            else:
                try:
                    write_to_sql(analysis)
                except Exception as e:
                    write_to_log("Could not write to database: " + ", ".join(analysis["patientname"]+ [str(dynalog)]) +
                                 ". "+str(e))
                    failed_dynalogs.append(os.path.join(path, dynalog))
                    print("Cannot write to sql: "+dynalog+". "+str(e))
                    continue
                else:
                    try:
                        write_to_zipfile("A" + dynalog, "B" + dynalog, path)
                        dynalogs_final.append(dynalog)
                    except Exception as e:
                          write_to_log("Could not write to zip archive: " + ", ".join(analysis["patientname"]+ [str(dynalog)])+
                                       ". "+str(e))
                          failed_dynalogs.append(os.path.join(path, dynalog))
                          print("Cannot write to zip: "+dynalog+". "+str(e))
                          continue

    if len(failed_dynalogs) > 0:
        copy_dynalogs(failed_dynalogs)
    write_to_log("Done.")
    print("Job completed.")
    
    # Write email and send it to the user
    if SEND_EMAIL and len(dynalogs_towrite)!=0:
        # Get data from database:
        conn = sql.connect(DYNALOG_DATABASE)
        curs = conn.cursor()
        data = []
        for dyn in dynalogs_final:
            name = os.path.splitext(os.path.basename(dyn))[0]
            curs.execute("SELECT PatientID, Repository, BeamID, Gantry, Time, Snapshots, Beamholds, RMSmax2, "\
                         "DIFFmax2, GammaAvg, GammaIndex "\
                         "FROM VarianDynalog WHERE FileName = '"+name+"' ORDER BY PatientID, BeamID, Date, Time")
            try:
                temp = curs.fetchall()[0]
            except IndexError:
                temp = [name.split("_")[-1], "Err",0,0,0,0,0,0,0,0,0]
            data.append(list(temp))
        curs.close()
        conn.close()

        # Create the email here:
        text = '''Pyqaserver: dynalog analysis.\n
                  Found dynalogs: '''+str(all_dynalogs)+'''\n
                  Dynalogs collected for analysis: '''+str(dynalogs_towrite_final)+'''\n
                  Skipped dynalogs (already in the database): '''+str(all_dynalogs-dynalogs_towrite_final)+'''\n
                  Dynalogs that could not be analyzed: '''+str(dynalogs_towrite_final-len(dynalogs_final))+'''\n
                  Max detected DIFF2: {maxdiff} mm for patient {patient}.\n
                  {table}'''
        
        html = '''<html>
                  <head>
                  <style> 
                  table, th, td {{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:left;}}
                  th, td {{padding: 5px;}}
                  </style>
                  </head>
                  <body><p>Pyqaserver: dynalog analysis.</p>
                  <p>Found dynalogs: '''+str(all_dynalogs)+'''<br>
                  Dynalogs collected for analysis: '''+str(dynalogs_towrite_final)+'''<br>
                  Skipped dynalogs (already in the database): '''+str(all_dynalogs-dynalogs_towrite_final)+'''<br>
                  Dynalogs that could not be analyzed: '''+str(dynalogs_towrite_final-len(dynalogs_final))+'''<br>
                  Max detected DIFF2: {maxdiff} mm for patient {patient}.</p>
                  {table}</body></html>'''
        
        field_names = ["Patient", "Folder", "Field", "Gantry", "Time", "Snaps","Holds",
                       "RMSmax2", "DIFFmax2", "GammaAvg", "GammaIndex"]
        pd_data = []
        for k in data:
            k[3] = round(float(k[3]), 1)
            k[7] = round(float(k[7])*10, 2)
            k[8] = round(float(k[8])*10, 2)
            k[9] = round(float(k[9])*10, 1)
            k[10] = round(float(k[10]), 1)
            pd_data.append(k)
        x = pd.DataFrame(pd_data, columns=field_names) 
        
        # Add those that could not be analyzed:
        for b in failed_dynalogs:
            first = os.path.dirname(b)
            second = os.path.splitext(os.path.basename(b))[0].split("_")[1]
            pd_temp = pd.DataFrame([[second, FOLDERS[first], 1,0.0,"Error",1,1,0.0,0.0,0.0,0.0]], columns=field_names)
            x = x.append(pd_temp, ignore_index=True)
        
        text = text.format(table=x.sort_values(by=['Folder', 'Patient', 'Time']).to_string(index=False),
                           maxdiff=x["DIFFmax2"].max(), patient=x["Patient"][x["DIFFmax2"].idxmax()])
        html = html.format(table=x.sort_values(by=['Folder', 'Patient', 'Time']).to_html(border=0, index=False, justify="left"),
                           maxdiff=x["DIFFmax2"].max(), patient=x["Patient"][x["DIFFmax2"].idxmax()])

        # Create the root message and fill in the from, to, and subject headers
        
        smtp_server = CONFIG["Dynalog"]["SMTP_SERVER"]
        smtp_port = int(CONFIG["Dynalog"]["SMTP_PORT"])
        send_from_user = CONFIG["Dynalog"]["SEND_FROM_USER"]
        send_from_password = CONFIG["Dynalog"]["SEND_FROM_PASSWORD"]
        send_to = [k.strip() for k in CONFIG["Dynalog"]["SEND_TO"].split(",")]
        
        message = MIMEMultipart("alternative", None, [MIMEText(text), MIMEText(html,'html')])
        message['Subject'] = 'Dynalog analysis ' + datetime.datetime.today().strftime("%Y-%m-%d")
        message['From'] = send_from_user
        message['To'] = ', '.join(send_to)
    
        # Send the email (this example assumes SMTP authentication is required)
        try:
            smtp = smtplib.SMTP(smtp_server, int(smtp_port))
            smtp.set_debuglevel(False)

            try:
                smtp = smtplib.SMTP(smtp_server, int(smtp_port))
                smtp.set_debuglevel(False)
                smtp.ehlo()
                if smtp.has_extn('STARTTLS'):
                    smtp.starttls()
                    smtp.ehlo() # re-identify ourselves over TLS connection
                    smtp.login(send_from_user, send_from_password)
                    print("Using TLS!")
                    write_to_log("Using TLS!")
                else:
                    print("Not using TLS!")
                    write_to_log("Not using TLS!")
                smtp.sendmail(send_from_user, send_to, message.as_string())

                print("E-Mail sent.")
                write_to_log("E-Mail sent. ")

            except Exception as e:
                print(e)
                write_to_log(str(e))
            finally:
                smtp.quit()
        except Exception as e:
            print("E-Mail not sent. "+str(e))
            write_to_log("E-Mail not sent. "+str(e))
