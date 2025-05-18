function testOrthancConnection() {
    $.ajax({
        type: 'POST',
        url: orthancCallsTestOrthancConnection,
        data: '',
        dataType: 'json',
        contentType: 'application/json'
    })
        .done(function (data) {
            alert("Orthanc connection established.");
        })
        .fail(function () {
            alert("Orthanc connection not established.");
        });
};

function checkCookiesEnabled() {
    if (!navigator.cookieEnabled) {
        alert("Cookies must be enabled for pyqaserver to work.");
    }
}

function changeOptions(selectId, options, values) {
    var html = [];
    for (j = 0; j < options.length; j++) {
        html.push('<option ' + 'value="' + values[j] + '">' + options[j] + '');
    }
    $('#' + selectId).html(html);
    $('#' + selectId).selectpicker('refresh');
    return;
}

function setSelectWidgetsSpinner(truefalse) {
    if (truefalse == true) {
        $("#orthancSpinner").prop('class', 'spinner-border spinner-border-sm text-danger');
    }
    else {
        $("#orthancSpinner").prop('class', 'spinner-border spinner-border-sm text-info');
    }
}

function disableSelectWidgets(truefalse) {
    setSelectWidgetsSpinner(truefalse);
    $('#patient-select-widget').prop('disabled', truefalse);
    $('#patient-select-widget').selectpicker('refresh');
    $('#study-select-widget').prop('disabled', truefalse);
    $('#study-select-widget').selectpicker('refresh');
    $('#series-select-widget').prop('disabled', truefalse);
    $('#series-select-widget').selectpicker('refresh');
    $('#refresh-orthanc-button').prop('disabled', truefalse);
    $('#analyze-button').prop('disabled', truefalse);
}

function getPatients() {
    disableSelectWidgets(true);
    $.ajax({
        type: 'POST',
        url: orthancCallsGetPatientsAll,
        data: '',
        dataType: 'json',
        contentType: 'application/json'
    })
        .done(function (data) {
            var orthancIds = [''].concat(data['orthanc_ids']);
            var patientNames = [''].concat(data['patients_names']);
            var patientIds = [''].concat(data['patients_ids']);

            var opt = [''];
            for (i = 1; i < orthancIds.length; i++) {
                var patientNameString = patientNames[i] + ' (' + patientIds[i] + ')';
                opt.push(patientNameString)
            }
            changeOptions('patient-select-widget', opt, orthancIds);
            disableSelectWidgets(false);
        })
        .fail(function (jqXHR, textStatus, error) {
            alert(jqXHR.responseText);
            setSelectWidgetsSpinner(false);
        });
}

function getStudies(patientOrthancId) {
    disableSelectWidgets(true);
    $.ajax({
        type: 'POST',
        url: orthancCallsGetStudiesForPatient,
        data: JSON.stringify({ 'patient_orthanc_id': patientOrthancId }),
        dataType: 'json',
        contentType: 'application/json'
    })
        .done(function (data) {
            var orthancIds = [''].concat(data['orthanc_ids']);
            var studyIds = [''].concat(data['study_ids']);
            var studyDesc = [''].concat(data['study_desc']);
            var studyDates = [''].concat(data['study_dates']);

            var opt = [''];
            for (i = 1; i < orthancIds.length; i++) {
                var studyDescriptionString = ' - ';
                if (studyDesc != '') {
                    studyDescriptionString = ' (' + studyDesc[i] + ') | ';
                }
                opt.push(studyIds[i] + studyDescriptionString + studyDates[i])
            }
            changeOptions('study-select-widget', opt, orthancIds);
            disableSelectWidgets(false);
        })
        .fail(function (jqXHR, textStatus, error) {
            alert(jqXHR.responseText);
            setSelectWidgetsSpinner(false);
        });
}

function getSeries(studyOrthancId) {
    disableSelectWidgets(true);
    $.ajax({
        type: 'POST',
        url: orthancCallsGetSeriesForStudy,
        data: JSON.stringify({ 'study_orthanc_id': studyOrthancId }),
        dataType: 'json',
        contentType: 'application/json'
    })
        .done(function (data) {
            var orthancIds = [''].concat(data['orthanc_ids']);
            var seriesNum = [''].concat(data['series_num']);
            var seriesDesc = [''].concat(data['series_desc']);
            var seriesDates = [''].concat(data['series_datetimes']);

            var opt = [''];
            for (i = 1; i < orthancIds.length; i++) {
                var seriesNumString = ' - ';
                if (seriesNum != '') {
                    seriesNumString = ' (' + seriesNum[i] + ') | ';
                }
                opt.push(seriesDesc[i] + seriesNumString + seriesDates[i])
            }
            changeOptions('series-select-widget', opt, orthancIds);
            disableSelectWidgets(false);
        })
        .fail(function (jqXHR, textStatus, error) {
            alert(jqXHR.responseText);
            setSelectWidgetsSpinner(false);
        });
}

function changeDecimal() {
    this.value = this.value.replace(/,/, '.');
}

function goToOrthancExplorer() {
    if ($('#series-select-widget').val().length < 1) {
        alert('Pick a series.');
        return;
    }
    var series_orthanc_ids = $('#series-select-widget').val()[0];
    $.ajax({
        type: 'POST',
        url: orthancCallsGoToOrthancExplorer,
        data: JSON.stringify({ 'series_orthanc_id': series_orthanc_ids }),
        dataType: 'json',
        contentType: 'application/json'
    })
        .done(function (data) {
            window.open(data['uri'], '_blank');
        })
        .fail(function (jqXHR, textStatus, error) {

        });
}

