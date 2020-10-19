import sqlite3 as sql
import sys

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    import config
else:
    from . import config

def create_trends_database(path):
    conn = sql.connect(path)
    c = conn.cursor()
    c.execute("""PRAGMA user_version = 1;
              """)
              
    ####################### WINSTON LUTZ #######################################
    c.execute("""CREATE TABLE WinstonlutzUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    
    c.execute("""CREATE TABLE Winstonlutz (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                BBshiftX REAL,
                                BBshiftY REAL,
                                BBshiftZ REAL,
                                BeamDeviation REAL,
                                CollAsymX REAL,
                                CollAsymY REAL,
                                WobbleColl REAL,
                                WobbleGnt REAL,
                                WobbleCouch REAL,
                                EpidDevX REAL,
                                EpidDevY REAL,
                                RadiusMax REAL,
                                CouchAxisLAT REAL,
                                CouchAxisLONG REAL,
                                CouchAxisDIST REAL,
                                Max2DbbCAX REAL,
                                Median2DbbCAX REAL,
                                GntIsoSize REAL,
                                MaxGntRMS REAL,
                                MaxEpidRMS REAL,
                                GntColl3DisoSize REAL,
                                Coll2DisoSize REAL,
                                MaxCollRMS REAL,
                                Couch2DisoDia REAL,
                                MaxCouchRMS REAL
                                )
              """)
    
    ############################## STARSHOT ################################
    c.execute("""CREATE TABLE StarshotUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE Starshot (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                Radius TEXT
                                )
              """)
    
    ############################## PICKETFENCE ################################
    c.execute("""CREATE TABLE PicketfenceUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE Picketfence (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                PassPrcnt TEXT,
                                MaxError TEXT,
                                MaxErrorPckt TEXT,
                                MaxErrorLeaf TEXT,
                                MedianError TEXT,
                                MeanPicketSpacing TEXT,
                                MeanFWHM TEXT
                                )
              """)
    ############################## PLANAR IMAGING ############################
    c.execute("""CREATE TABLE PlanarImagingUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    
    c.execute("""CREATE TABLE PlanarImaging (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                f30 TEXT,
                                f40 TEXT,
                                f50 TEXT,
                                f80 TEXT,
                                MedianContrast TEXT,
                                MedianCNR TEXT
                                )
              """)
    ############################## CATPHAN ############################
    c.execute("""CREATE TABLE CatphanUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)

    c.execute("""CREATE TABLE Catphan (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                MTF30 TEXT,
                                MTF50 TEXT,
                                MTF80 TEXT,
                                LCV TEXT,
                                SliceThickness TEXT,
                                Scaling TEXT,
                                PhantomRoll TEXT,
                                PhantomCenterX TEXT,
                                PhantomCenterY TEXT,
                                OriginSlice TEXT,
                                mm_per_pixel TEXT,
                                UniformityIndex TEXT,
                                UniformityAbsoluteValue TEXT,
                                LowContrastROIsSeen TEXT,
                                LowContrastCNR TEXT,
                                Air_HU TEXT,
                                PMP_HU TEXT,
                                LDPE_HU TEXT,
                                Poly_HU TEXT,
                                Acrylic_HU TEXT,
                                Delrin_HU TEXT,
                                Teflon_HU TEXT,
                                Bone20_HU TEXT,
                                Bone50_HU TEXT,
                                Air_CNR TEXT,
                                PMP_CNR TEXT,
                                LDPE_CNR TEXT,
                                Poly_CNR TEXT,
                                Acrylic_CNR TEXT,
                                Delrin_CNR TEXT,
                                Teflon_CNR TEXT,
                                Bone20_CNR TEXT,
                                Bone50_CNR TEXT
                                )
              """)
    
    ############################## FLATSYM ################################
    c.execute("""CREATE TABLE FlatSymUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE FlatSym (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                Symmetry_hor TEXT,
                                Symmetry_vrt TEXT,
                                Flatness_hor TEXT,
                                Flatness_vrt TEXT,
                                Horizontal_width TEXT,
                                Vertical_width TEXT,
                                Horizontal_penumbra_width TEXT,
                                Vertical_penumbra_width TEXT
                                )
              """)

    ############################## VMAT ################################
    c.execute("""CREATE TABLE VmatUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam)
                                )
              """)
    
    c.execute("""CREATE TABLE Vmat (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                Max_diff TEXT,
                                Mean_diff TEXT
                                )
              """)
    ####################### FIELD SIZE #######################################
    c.execute("""CREATE TABLE FieldSizeUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    
    c.execute("""CREATE TABLE FieldSize (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                LeafSide1 TEXT,
                                LeafSide2 TEXT,
                                JawSide1 TEXT,
                                JawSide2 TEXT,
                                LeafWidth TEXT,
                                JawWidth TEXT,
                                IsoOffsetX TEXT,
                                IsoOffsetY TEXT,
                                FieldRot TEXT,
                                IsoMethod TEXT
                                )
              """)
    ####################### FIELD ROTATION ###################################
    c.execute("""CREATE TABLE FieldRotationUniqueNames (
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                UNIQUE(Machine, Beam, Phantom)
                                )
              """)
    
    c.execute("""CREATE TABLE FieldRotation (
                                User TEXT,
                                Datetime TEXT,
                                Machine TEXT,
                                Beam TEXT,
                                Phantom TEXT,
                                TestType TEXT,
                                Comment TEXT,
                                Angle TEXT
                                )
              """)
    
    conn.commit()
    conn.close()