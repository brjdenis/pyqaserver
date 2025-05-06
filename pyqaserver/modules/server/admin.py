"""Blueprint for the admin pages."""

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from pyqaserver import app, db
from pyqaserver.models import db_general


class MyModelView(ModelView):
    """Overrides the original ModelView so that admin is protected."""

    def is_accessible(self):
        """Override authentification for admin pages."""
        # If in development mode, login is 'disabled'.
        if app.config["LOGIN_DISABLED"]:
            return True
        # For normal use:
        if current_user.is_authenticated:
            user = db_general.User.get_user(current_user.username)
            return user.is_admin
        return False


def register_admin():
    """Adds admin tabs to admin pages."""
    app_admin = Admin(app, name="Admin", template_mode="bootstrap4")
    app_admin.add_view(MyModelView(db_general.User, db.session))
    app_admin.add_view(MyModelView(db_general.Orthanc, db.session))
    app_admin.add_view(MyModelView(db_general.Machine, db.session))
    app_admin.add_view(MyModelView(db_general.DicomMapping, db.session))
    app_admin.add_view(MyModelView(db_general.ReferenceImage, db.session))
    app_admin.add_view(MyModelView(db_general.Tolerance, db.session))
    app_admin.add_view(MyModelView(db_general.ModuleSetting, db.session))
