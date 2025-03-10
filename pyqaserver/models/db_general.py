'''Model for the database. The database contains everything,
from settings to measurement trends. Probably not the right way to go,
but I like the fact that everything is contained in a single sqlite file.

Only the dynalog/trajectory log module has its own database.'''

from sqlalchemy import JSON, event
from flask_login import UserMixin
from pyqaserver import db, app
from pyqaserver.utils.pswd import check_pswd_hash, generate_pswd_hash


class Orthanc(db.Model):
    rowid = db.Column(db.Integer, primary_key=True, nullable=False)
    ip = db.Column(db.String, nullable=False)
    port = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    @classmethod
    def get_address(cls):
        with app.app_context():
            return db.session.execute(db.select(Orthanc)).scalar_one()


class User(db.Model, UserMixin):
    rowid = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    display_name = db.Column(db.String, nullable=False)

    @classmethod
    def get_user(cls, name):
        with app.app_context():
            return db.session.execute(
                db.select(User).filter_by(username=name)
                ).scalar()

    @classmethod
    def change_pass(cls, name, new_pswd):
        with app.app_context():
            user = db.session.execute(
                db.select(cls)
                .filter_by(username=name)
                ).scalar()
            user.password = new_pswd  # Autohashed if called during request
            db.session.commit()

    def check_pass(self, tried_pswd):
        return check_pswd_hash(tried_pswd, self.password)

    def get_id(self):
        return self.rowid  # Override for flask-login


class DicomMapping(db.Model):
    __table_args__ = (db.UniqueConstraint('dicom_name', 'dicom_energy'), )
    rowid = db.Column(db.Integer, primary_key=True)
    dicom_energy = db.Column(db.String)
    dicom_name = db.Column(db.String)
    user_energy = db.Column(db.String)
    user_name = db.Column(db.String)


class Machine(db.Model):
    __table_args__ = (db.UniqueConstraint('machine', 'beam', 'phantom'), )
    rowid = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String)
    machine = db.Column(db.String)
    beam = db.Column(db.String)
    phantom = db.Column(db.String)


class ReferenceImage(db.Model):
    rowid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    module = db.Column(db.String)
    machine = db.Column(db.String)
    beam = db.Column(db.String)
    phantom = db.Column(db.String)
    type = db.Column(db.String)
    orth_series = db.Column(db.String)


class Tolerance(db.Model):
    __table_args__ = (db.UniqueConstraint('machine', 'beam', 'phantom'), )
    rowid = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String)
    machine = db.Column(db.String)
    beam = db.Column(db.String)
    phantom = db.Column(db.String)
    tolerance1 = db.Column(JSON, nullable=True)
    tolerance2 = db.Column(JSON, nullable=True)


class ModuleSetting(db.Model):
    rowid = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String)
    settings = db.Column(JSON, nullable=True)


def add_starting_data():
    with app.app_context():
        user = User(
            rowid=1,
            username='admin',
            password=generate_pswd_hash('admin'),
            is_admin=True,
            display_name='Admin'
            )
        orth = Orthanc(
            rowid=1,
            ip='127.0.0.1',
            port='8042',
            user='admin',
            password='admin'
        )
        db.session.add(user)
        db.session.add(orth)
        db.session.commit()


def add_psswd_hasher():
    # Listener that converts input password into hash on changing User
    @event.listens_for(User.password, 'set', retval=True)
    def hash_user_password(target, value, oldvalue, initiator):
        if value != oldvalue:
            return generate_pswd_hash(value)
        return value
