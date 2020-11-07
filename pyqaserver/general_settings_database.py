import sqlite3 as sql
from passlib.context import CryptContext

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

def create_general_settings_database(path):
    conn = sql.connect(path)
    c = conn.cursor()
    c.execute("""PRAGMA user_version = 1;
              """)
    
    ############################## USERS LIST #################################
    c.execute("""CREATE TABLE Users (
                                Name TEXT UNIQUE,
                                Password TEXT,
                                Admin TEXT,
                                DisplayName TEXT
                                )
              """)
    c.execute("INSERT INTO Users (Name, Password, Admin, DisplayName) VALUES (?, ?, ?, ?)",
              ("admin", pwd_context.hash("admin"), "Yes", "Admin"))
    
    ############################## ORTHANC SETTINGS ###########################
    c.execute("""CREATE TABLE Orthanc (
                                IP TEXT,
                                Port TEXT,
                                User TEXT,
                                Password TEXT
                                )
              """)
    c.execute("INSERT INTO Orthanc (IP, Port, User, Password) VALUES (?, ?, ?, ?)",
              ("127.0.0.1", "8042", "orthancuser", "orthancpass"))
    
    ############################## INSTITUTION SETTINGS ###########################
    c.execute("""CREATE TABLE Institution (
                                Name TEXT
                                )
              """)
    c.execute("INSERT INTO Institution (Name) VALUES (?)", ("Put name here", ))
    
    ################################ MACHINE MAPPING #######################
    c.execute("""CREATE TABLE MachineMapping (
                                DicomName TEXT,
                                DicomEnergy TEXT,
                                UserName TEXT,
                                UserEnergy TEXT,
                                UNIQUE (DicomName, DicomEnergy)
                                )
              """)

    ################################ WINSTON LUTZ ############################
    c.execute("""CREATE TABLE WinstonLutzUnits (
                                Machine TEXT,
                                Beam TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE WinstonLutzSettings (
                                PASS_RATE TEXT,
                                SUCCESS_RATE TEXT,
                                APPLY_TOLERANCE_TO_COLL_ASYM TEXT,
                                COLL_ASYM_TOL TEXT,
                                BEAM_DEV_TOL TEXT,
                                COUCH_DIST_TOL TEXT
                                )
              """)
    
    c.execute("INSERT INTO WinstonLutzSettings (PASS_RATE, SUCCESS_RATE, APPLY_TOLERANCE_TO_COLL_ASYM, COLL_ASYM_TOL, BEAM_DEV_TOL, COUCH_DIST_TOL )"
              " VALUES (?, ?, ?, ?, ?, ?)", ("1.5", "1.0", "False", "0.5", "0.5", "0.5"))
    
    c.execute("""CREATE TABLE WinstonLutzTolerance (
                                Machine TEXT UNIQUE,
                                PASS_RATE TEXT,
                                SUCCESS_RATE TEXT,
                                APPLY_TOLERANCE_TO_COLL_ASYM TEXT,
                                COLL_ASYM_TOL TEXT,
                                BEAM_DEV_TOL TEXT,
                                COUCH_DIST_TOL TEXT
                                )
              """)

    c.execute("""CREATE TABLE WinstonLutzPhantoms (
                                Phantom TEXT UNIQUE
                                )
              """)
    c.execute("INSERT INTO WinstonLutzPhantoms (Phantom) VALUES (?)", ("Ballbearing", ))
    
    ######################  STARSHOT ############################################
    c.execute("""CREATE TABLE StarshotUnits (
                                Machine TEXT,
                                Beam TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE StarshotSettings (
                                TOLERANCE TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)
    c.execute("INSERT INTO StarshotSettings (TOLERANCE, GENERATE_PDF_REPORT "
              ") VALUES (?, ?)", ("1", "True"))
    
    c.execute("""CREATE TABLE StarshotTolerance (
                                Machine TEXT UNIQUE,
                                TOLERANCE TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)
    
    ############################# PICKETFENCE ####################################
    c.execute("""CREATE TABLE PicketfenceUnits (
                                Machine TEXT,
                                Beam TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE PicketfenceSettings (
                                ACTION_TOLERANCE TEXT,
                                TOLERANCE TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)
    c.execute("INSERT INTO PicketfenceSettings (ACTION_TOLERANCE, TOLERANCE, GENERATE_PDF_REPORT "
              ") VALUES (?, ?, ?)", ("0.25", "0.5", "True"))
    
    c.execute("""CREATE TABLE PicketfenceTolerance (
                                Machine TEXT UNIQUE,
                                ACTION_TOLERANCE TEXT,
                                TOLERANCE TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)

    ######################################## PLANAR IMAGING ############################
    c.execute("""CREATE TABLE PlanarImagingUnits (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)

    c.execute("""CREATE TABLE PlanarImagingTolerance (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                LOW_THRESHOLD TEXT,
                                HIGH_THRESHOLD TEXT,
                                GENERATE_PDF_REPORT TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    
    c.execute("""CREATE TABLE PlanarImagingReferenceImages (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                Path TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    ######################################## CATPHAN ############################
    c.execute("""CREATE TABLE CatphanUnits (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)

    c.execute("""CREATE TABLE CatphanTolerance (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                HU TEXT,
                                LCV TEXT,
                                SCALING TEXT,
                                THICKNESS TEXT,
                                LOWCONTRAST TEXT,
                                CNR TEXT,
                                MTF TEXT,
                                UNIFORMITYIDX TEXT,
                                GENERATE_PDF_REPORT TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    
    c.execute("""CREATE TABLE CatphanReferenceImages (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                Path TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    ######################  FLATSYM ############################################
    c.execute("""CREATE TABLE FlatSymUnits (
                                Machine TEXT,
                                Beam TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE FlatSymSettings (
                                TOLERANCE_FLAT TEXT,
                                TOLERANCE_SYM TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)
    
    c.execute("INSERT INTO FlatSymSettings (TOLERANCE_FLAT, TOLERANCE_SYM, GENERATE_PDF_REPORT"
              ") VALUES (?, ?, ?)", ("2", "2",  "True"))

    c.execute("""CREATE TABLE FlatSymTolerance (
                                Machine TEXT UNIQUE,
                                TOLERANCE_FLAT TEXT,
                                TOLERANCE_SYM TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)
    
    ################################### VMAT ####################################
    c.execute("""CREATE TABLE VmatUnits (
                                Machine TEXT,
                                Beam TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE VmatSettings (
                                TOLERANCE TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)
    c.execute("INSERT INTO VmatSettings (TOLERANCE, GENERATE_PDF_REPORT) "
              "VALUES (?, ?)", ("1.5", "True"))
    
    c.execute("""CREATE TABLE VmatTolerance (
                                Machine TEXT UNIQUE,
                                TOLERANCE TEXT,
                                GENERATE_PDF_REPORT TEXT
                                )
              """)
    
    ################################ FIELD SIZE ############################
    c.execute("""CREATE TABLE FieldSizeUnits (
                                Machine TEXT,
                                Beam TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE FieldSizeSettings (
                                SMALL_NOMINAL TEXT,
                                MEDIUM_NOMINAL TEXT,
                                LARGE_NOMINAL TEXT,
                                SMALL_EXP_MLC TEXT,
                                MEDIUM_EXP_MLC TEXT,
                                LARGE_EXP_MLC TEXT,
                                SMALL_EXP_JAW TEXT,
                                MEDIUM_EXP_JAW TEXT,
                                LARGE_EXP_JAW TEXT,
                                TOLERANCE_SMALL_MLC TEXT,
                                TOLERANCE_MEDIUM_MLC TEXT,
                                TOLERANCE_LARGE_MLC TEXT,
                                TOLERANCE_SMALL_JAW TEXT,
                                TOLERANCE_MEDIUM_JAW TEXT,
                                TOLERANCE_LARGE_JAW TEXT,
                                TOLERANCE_ISO TEXT
                                )
              """)
    
    c.execute("INSERT INTO FieldSizeSettings (SMALL_NOMINAL, MEDIUM_NOMINAL, LARGE_NOMINAL, "
              "SMALL_EXP_MLC, MEDIUM_EXP_MLC, LARGE_EXP_MLC, SMALL_EXP_JAW, MEDIUM_EXP_JAW, LARGE_EXP_JAW, "
              "TOLERANCE_SMALL_MLC, TOLERANCE_MEDIUM_MLC, TOLERANCE_LARGE_MLC, "
              "TOLERANCE_SMALL_JAW, TOLERANCE_MEDIUM_JAW, TOLERANCE_LARGE_JAW, "
              "TOLERANCE_ISO)"
              " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              ("5", "10", "20", "5", "10", "20", "5", "10", "20",
               "0.1", "0.1", "0.1", "0.1", "0.1", "0.1", "0.1"))
    
    c.execute("""CREATE TABLE FieldSizeTolerance (
                                Machine TEXT UNIQUE,
                                SMALL_NOMINAL TEXT,
                                MEDIUM_NOMINAL TEXT,
                                LARGE_NOMINAL TEXT,
                                SMALL_EXP_MLC TEXT,
                                MEDIUM_EXP_MLC TEXT,
                                LARGE_EXP_MLC TEXT,
                                SMALL_EXP_JAW TEXT,
                                MEDIUM_EXP_JAW TEXT,
                                LARGE_EXP_JAW TEXT,
                                TOLERANCE_SMALL_MLC TEXT,
                                TOLERANCE_MEDIUM_MLC TEXT,
                                TOLERANCE_LARGE_MLC TEXT,
                                TOLERANCE_SMALL_JAW TEXT,
                                TOLERANCE_MEDIUM_JAW TEXT,
                                TOLERANCE_LARGE_JAW TEXT,
                                TOLERANCE_ISO TEXT
                                )
              """)
    ################################### FIELD ROTATION ########################
    c.execute("""CREATE TABLE FieldRotationUnits (
                                Machine TEXT,
                                Beam TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE FieldRotationSettings (
                                TOLERANCE_COLLABS TEXT,
                                TOLERANCE_COLLREL TEXT,
                                TOLERANCE_COUCHREL TEXT
                                )
              """)
    c.execute("INSERT INTO FieldRotationSettings (TOLERANCE_COLLABS, TOLERANCE_COLLREL, TOLERANCE_COUCHREL) "
              "VALUES (?, ?, ?)", ("1", "1", "1"))
    
    c.execute("""CREATE TABLE FieldRotationTolerance (
                                Machine TEXT UNIQUE,
                                TOLERANCE_COLLABS TEXT,
                                TOLERANCE_COLLREL TEXT,
                                TOLERANCE_COUCHREL TEXT
                                )
              """)
    conn.commit()
    conn.close()