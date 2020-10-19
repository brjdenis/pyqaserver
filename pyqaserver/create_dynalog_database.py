#Create sql Varian Dynalog database
import sys
import sqlite3 as sql

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    import config
else:
    from . import config

def create_dynalog_database(path):
    conn = sql.connect(path)
    c = conn.cursor()
    c.execute("""PRAGMA user_version = 1;
              """)
    c.execute("""CREATE TABLE VarianDynalog (
                                FileName TEXT UNIQUE,
                                ZipArchive TEXT,
                                PatientID TEXT,
                                PatientName TEXT,
                                PatientLastName TEXT,
                                Date TEXT,
                                Time TEXT,
                                BeamID TEXT,
                                Gantry REAL,
                                Snapshots INTEGER,
                                Beamholds INTEGER,
                                RMSmax REAL,
                                RMSmax2 REAL,
                                DIFFmax REAL,
                                DIFFmax2 REAL,
                                RMSAvg REAL,
                                GammaAvg REAL,
                                GammaIndex REAL,
                                GammaTol TEXT,
                                DateEntered TEXT,
                                Repository TEXT,
                                ext1 TEXT,
                                ext2 TEXT,
                                ext3 TEXT,
                                ext4 TEXT,
                                ext5 TEXT
                                )
              """)
    
    conn.commit()
    conn.close()
