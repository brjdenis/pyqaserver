"""Orthanc calls."""

import contextlib
from datetime import datetime as dt
from datetime import timezone as tz
from pathlib import Path

import requests
from flask import Blueprint, request
from flask_login import login_required

from pyqaserver import abort_text
from pyqaserver.models import db_general

NULL_DATE = "19700101"  # beginning of epoch (UTC)
NULL_TIME = "000000"

BLUEPRINT_PATH = Path(__file__).parent.resolve()

orthanc_bp = Blueprint(
    "orthanc_calls",
    "orthanc_calls",
    template_folder=BLUEPRINT_PATH / "templates",
    static_folder=BLUEPRINT_PATH / "static",
    url_prefix="/orthanc",
)


def make_orthanc_request(uri, headers, auth, timeout=10):
    """Common orthanc http request."""
    try:
        resp = requests.get(uri, headers=headers, auth=auth, timeout=timeout)
        resp.raise_for_status()
    except requests.HTTPError:
        abort_text(500, description="Orthanc HTTP error.")
    except requests.ConnectionError:
        abort_text(500, description="Orthanc connection error.")
    except requests.Timeout:
        abort_text(504, description="Orthanc connection timeout.")
    else:
        return resp


def test_orthanc():
    """Get system status as a way of checking orthanc connection."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = f"http://{address.ip}:{address.port}/system"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=10)
    return resp.json()


def get_patients():
    """Collect list of patients for patient-select widget."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = f"http://{address.ip}:{address.port}/patients"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=10)
    resp = resp.json()

    headers["Connection"] = "keep-alive"
    pat_data = []
    for orth_id in resp:
        uri = f"http://{address.ip}:{address.port}/patients/{orth_id}"
        resp2 = make_orthanc_request(uri, headers, auth, timeout=60)
        pat_data.append(resp2.json())

    if len(pat_data) == 0:
        return {"orthanc_ids": [], "patients_names": [], "patients_ids": []}

    orthanc_ids = []
    pat_names = []
    pat_ids = []
    for patient in pat_data:
        dicomtags = patient["MainDicomTags"]
        if "PatientName" in dicomtags:
            pat_names.append(dicomtags["PatientName"].replace("^", " "))
        else:
            pat_names.append("UnknownPatient")
        if "PatientID" in dicomtags:
            pat_ids.append(dicomtags["PatientID"])
        else:
            pat_ids.append("UnknownPatientID")
        orthanc_ids.append(patient["ID"])

    pat_names_sorted, pat_ids_sorted, orthanc_ids_sorted = zip(
        *sorted(zip(pat_names, pat_ids, orthanc_ids), key=lambda i: i[0].casefold())
    )

    return {
        "orthanc_ids": list(orthanc_ids_sorted),
        "patients_names": list(pat_names_sorted),
        "patients_ids": list(pat_ids_sorted),
    }


def get_studies(patient_orthanc_id):
    """Get a list of studies that belong to the selected patient."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = f"http://{address.ip}:{address.port}/patients/{patient_orthanc_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=60)

    resp = resp.json()

    resp = list(resp["Studies"]) if "Studies" in resp else []

    headers["Connection"] = "keep-alive"
    data = []
    for orth_id in resp:
        uri = f"http://{address.ip}:{address.port}/studies/{orth_id}"
        resp2 = make_orthanc_request(uri, headers, auth, timeout=60)
        data.append(resp2.json())

    if len(data) == 0:
        return {"orthanc_ids": [], "study_ids": [], "study_desc": [], "study_dates": []}

    orthanc_ids = []
    study_ids = []
    study_desc = []
    study_dates = []
    for study in data:
        dicomtags = study["MainDicomTags"]
        if "StudyID" in dicomtags:
            study_ids.append(dicomtags["StudyID"])
        else:
            study_ids.append("UnknownStudyID")
        if "StudyDescription" in dicomtags:
            study_desc.append(dicomtags["StudyDescription"])
        else:
            study_desc.append("")
        try:
            study_dates.append(
                dt.strptime(dicomtags["StudyDate"], "%Y%m%d").astimezone(tz.utc)
            )
        except (KeyError, ValueError):
            study_dates.append(dt.strptime(NULL_DATE, "%Y%m%d").astimezone(tz.utc))
        orthanc_ids.append(study["ID"])

    study_dates_srt, study_desc_srt, study_ids_srt, orthanc_ids_srt = zip(
        *sorted(
            zip(study_dates, study_desc, study_ids, orthanc_ids), key=lambda i: i[0]
        )
    )
    study_dates_srt = [i.strftime("%Y-%m-%d") for i in study_dates_srt]

    return {
        "orthanc_ids": list(orthanc_ids_srt),
        "study_ids": list(study_ids_srt),
        "study_desc": list(study_desc_srt),
        "study_dates": study_dates_srt,
    }


def get_series(study_orthanc_id):
    """Get a sorted list of series that belong to a particular study_id."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = f"http://{address.ip}:{address.port}/studies/{study_orthanc_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=60)

    resp = resp.json()

    resp = list(resp["Series"]) if "Series" in resp else []

    headers["Connection"] = "keep-alive"
    data = []
    for orth_id in resp:
        uri = f"http://{address.ip}:{address.port}/series/{orth_id}"
        resp2 = make_orthanc_request(uri, headers, auth, timeout=60)
        data.append(resp2.json())

    if len(data) == 0:
        return {
            "orthanc_ids": [],
            "series_num": [],
            "series_desc": [],
            "series_dates": [],
        }

    orthanc_ids = []
    series_num = []
    series_desc = []
    series_dt = []
    for series in data:
        dicomtags = series["MainDicomTags"]
        if "SeriesNumber" in dicomtags:
            series_num.append(dicomtags["SeriesNumber"])
        else:
            series_num.append("")
        if "SeriesDescription" in dicomtags:
            series_desc.append(dicomtags["SeriesDescription"])
        else:
            series_desc.append("")
        # Get first instance of the series and get date from that
        if "Instances" in series:
            series_dt.append(get_series_dt(series["Instances"][0]))
        else:
            st = NULL_DATE + " " + NULL_TIME
            series_dt.append(dt.strptime(st, "%Y%m%d %H:%M:%S").astimezone(tz.utc))
        orthanc_ids.append(series["ID"])

    series_dt_srt, series_desc_srt, series_num_srt, orthanc_ids_srt = zip(
        *sorted(
            zip(series_dt, series_desc, series_num, orthanc_ids), key=lambda i: i[0]
        )
    )
    series_dt_srt = [i.strftime("%Y-%m-%d / %H:%M:%S") for i in series_dt_srt]

    return {
        "orthanc_ids": list(orthanc_ids_srt),
        "series_num": list(series_num_srt),
        "series_desc": list(series_desc_srt),
        "series_datetimes": series_dt_srt,
    }


def get_series_dt(instance_orthanc_id):
    """Gets date and time for a series to which instance belongs."""
    # Search by MainDicomTags, faster
    # If Creation datetime is not found, search in full tag list, slower
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = f"http://{address.ip}:{address.port}/instances/{instance_orthanc_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=60)
    resp = resp.json()
    tags = resp["MainDicomTags"]
    try:
        st = (
            tags["InstanceCreationDate"]
            + " "
            + tags["InstanceCreationTime"].strip()[0:6]
        )
        series_dt = dt.strptime(st, "%Y%m%d %H%M%S").astimezone(tz.utc)
    except (KeyError, ValueError):
        series_dt = get_instance_dt(instance_orthanc_id)
    return series_dt


def get_dt_from_instance(resp_json):
    """Gets date and time from the orthanc json meta of an instance."""
    try:
        date_var = resp_json["AcquisitionDate"]
        time_var = resp_json["AcquisitionTime"]
    except (KeyError, ValueError):
        try:
            date_var = resp_json["InstanceCreationDate"]
            time_var = resp_json["InstanceCreationTime"]
        except (KeyError, ValueError):
            try:
                date_var = resp_json["ContentDate"]
                time_var = resp_json["ContentTime"]
            except (KeyError, ValueError):
                try:
                    date_var = resp_json["StudyDate"]
                    time_var = resp_json["StudyTime"]
                except (KeyError, ValueError):
                    date_var = NULL_DATE
                    time_var = NULL_TIME
    # prevent empty date_var/time_var
    try:
        tt = date_var.strip() + " " + time_var.strip()[0:6]
        datetime = dt.strptime(tt, "%Y%m%d %H%M%S").astimezone(tz.utc)
    except ValueError:
        tt = NULL_DATE + " " + NULL_TIME
        datetime = dt.strptime(tt, "%Y%m%d %H%M%S").astimezone(tz.utc)
    return datetime


def get_instance_dt(instance_orthanc_id):
    """Gets the date and time of a particular instance."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = (
        f"http://{address.ip}:{address.port}"
        f"/instances/{instance_orthanc_id}/simplified-tags"
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=60)
    resp = resp.json()
    return get_dt_from_instance(resp)


def get_instance_dt_and_label(instance_orthanc_id):
    """Gets date and time together with the label for an instance."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = (
        f"http://{address.ip}:{address.port}"
        f"/instances/{instance_orthanc_id}/simplified-tags"
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=60)
    resp = resp.json()
    try:
        manufact = resp["Manufacturer"]
    except (KeyError, ValueError):
        manufact = "Unknown"

    search_instance_label = "InstanceNumber"
    if manufact in ["Varian Medical Systems"]:
        search_instance_label = "RTImageLabel"
    try:
        label = resp[search_instance_label]
    except (KeyError, ValueError):
        label = "Unknown"
    return {"datetime": get_dt_from_instance(resp), "label": label}


def get_instances(series_orthanc_ids):
    """Gets all the instance ids, labels and datetimes that belong to the series."""
    instance_orthanc_ids = []
    instance_labels = []
    instance_datetime = []
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    for series_id in series_orthanc_ids:
        uri = f"http://{address.ip}:{address.port}/series/{series_id}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Connection": "close",
        }
        resp = make_orthanc_request(uri, headers, auth, timeout=60)
        resp = resp.json()
        resp = list(resp["Instances"]) if "Instances" in resp else []

        for instance_id in resp:
            instance_orthanc_ids.append(instance_id)
            dt_and_label = get_instance_dt_and_label(instance_id)
            instance_datetime.append(dt_and_label["datetime"])
            instance_labels.append(dt_and_label["label"])

    if len(instance_orthanc_ids) == 0:
        return {"orthanc_id": [], "instance_label": [], "instance_datetime": []}

    instance_datetime_srt, instance_labels_srt, orthanc_ids_srt = zip(
        *sorted(
            zip(instance_datetime, instance_labels, instance_orthanc_ids),
            key=lambda i: i[0],
        )
    )
    instance_datetime_srt = [
        i.strftime("%Y-%m-%d / %H:%M:%S") for i in instance_datetime_srt
    ]
    return {
        "orthanc_id": orthanc_ids_srt,
        "instance_label": instance_labels_srt,
        "instance_datetime": instance_datetime_srt,
    }


def get_image_description(orthanc_instance_id):
    """Gets the description of an instance."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = f"http://{address.ip}:{address.port}/instances/{orthanc_instance_id}/content"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=10)
    if "3002-0004" in resp.json():
        uri = (
            f"http://{address.ip}:{address.port}/instances/"
            f"{orthanc_instance_id}/content/3002-0004"
        )
        resp = make_orthanc_request(uri, headers, auth, timeout=10)
        return resp.content.decode()
    return "Unknown"


def get_series_description(orthanc_series_id):
    """Gets the description of a series."""
    address = db_general.Orthanc.get_address()
    auth = (address.user, address.password)
    uri = f"http://{address.ip}:{address.port}/series/{orthanc_series_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Connection": "close",
    }
    resp = make_orthanc_request(uri, headers, auth, timeout=10)
    resp = resp.json()

    manufacturer = "Unknown"
    modality = "Unknown"
    protocol = "Unknown"
    station = "Unknown"
    if "MainDicomTags" in resp:
        tags = resp["MainDicomTags"]
        with contextlib.suppress(KeyError, ValueError):
            manufacturer = tags["Manufacturer"]
        with contextlib.suppress(KeyError, ValueError):
            modality = tags["Modality"]
        with contextlib.suppress(KeyError, ValueError):
            protocol = tags["ProtocolName"]
        with contextlib.suppress(KeyError, ValueError):
            station = tags["StationName"]

    return {
        "manufacturer": manufacturer,
        "modality": modality,
        "protocol": protocol,
        "station": station,
    }


@orthanc_bp.route("/go_to_orthanc_explorer", methods=["POST"])
@login_required
def go_to_orthanc_explorer():
    """Send the address of the orthanc web explorer pointing to a specific series."""
    series_id = request.json["series_orthanc_id"]
    address = db_general.Orthanc.get_address()
    uri = (
        f"http://{address.ip}:{address.port}/app/explorer.html#series?uuid={series_id}"
    )
    return {"uri": uri}


@orthanc_bp.route("/test_orthanc", methods=["POST"])
@login_required
def test_orthanc_connection():
    """Tests the orthanc connection."""
    return test_orthanc()


@orthanc_bp.route("/get_patients_all", methods=["POST"])
@login_required
def get_patients_all():
    """Collects all patients from orthanc database."""
    patients_data = get_patients()
    return {
        "orthanc_ids": patients_data["orthanc_ids"],
        "patients_names": patients_data["patients_names"],
        "patients_ids": patients_data["patients_ids"],
    }


@orthanc_bp.route("/get_studies_for_patient", methods=["POST"])
@login_required
def get_studies_for_patient():
    """Collects all studies that belong to a specific patient."""
    studies = get_studies(request.json["patient_orthanc_id"])
    return {
        "orthanc_ids": studies["orthanc_ids"],
        "study_ids": studies["study_ids"],
        "study_desc": studies["study_desc"],
        "study_dates": studies["study_dates"],
    }


@orthanc_bp.route("/get_series_for_study", methods=["POST"])
@login_required
def get_series_for_study():
    """Collects all series that belong to a specific study."""
    series = get_series(request.json["study_orthanc_id"])
    return {
        "orthanc_ids": series["orthanc_ids"],
        "series_num": series["series_num"],
        "series_desc": series["series_desc"],
        "series_datetimes": series["series_datetimes"],
    }


@orthanc_bp.route("/get_instances_for_series", methods=["POST"])
@login_required
def get_instances_for_series():
    """Collects all instances that belong to multiple series."""
    # series_orthanc_id is an array of series orthanc_ids (multiple select)
    instances = get_instances(request.json["series_orthanc_ids"])
    nums = list(range(len(instances["orthanc_id"])))
    return [
        {
            "orthanc_id": instances["orthanc_id"][i],
            "num": i,
            "instance_label": instances["instance_label"][i],
            "instance_datetime": instances["instance_datetime"][i],
        }
        for i in nums
    ]


@orthanc_bp.route("/get_image_description_for_instance", methods=["POST"])
@login_required
def get_image_description_for_instance():
    """Gets the image description of an instance."""
    return get_image_description(request.json["orthanc_instance_id"])


@orthanc_bp.route("/get_description_for_series", methods=["POST"])
@login_required
def get_description_for_series():
    """Gets the description of a selected series."""
    return get_series_description(request.json["orthanc_series_id"][0])
