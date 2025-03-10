$(document).ready(function() {
    testOrthanc();
    setInterval(testOrthanc, 5000);
    getPatients();

    $('#patient-select-widget').on('change', function(){
        if ($('#patient-select-widget').prop('selectedIndex') != 0){
            getStudies($('#patient-select-widget').val());
        }
        else{
            changeOptions('study-select-widget', [''], ['']);
            $('#studies-select-widget').prop('selectedIndex', 0);
        }
    });

    $('#study-select-widget').on('change', function(){
        if ($('#study-select-widget').prop('selectedIndex') != 0){
            getSeries($('#study-select-widget').val());
        }
        else{
            changeOptions('series-select-widget', [''], ['']);
            $('#series-select-widget').prop('selectedIndex', 0);
        }
    });

    $('#series-select-widget').on('change', function(){
        if ($('#series-select-widget').prop('selectedIndex') != 0){
            loadInstanceTable();
            if ($('#series-select-widget').val().length > 0){
                getSeriesDescription($('#series-select-widget').val(), function(data) {
                    $("#stationDescriptionText").text('Station: ' + data['station']);
                });
            }
            else{
                $("#stationDescriptionText").text('Station:');
            }
        }
        else{
            instanceTable.setData([]);
            $("#stationDescriptionText").text('Station:');
        }
    });

    $('#refresh-orthanc-button').on('click', function(){
        getPatients();
        $('#patient-select-widget').prop('selectedIndex', 0);
        changeOptions('study-select-widget', [''], ['']);
        changeOptions('series-select-widget', [''], ['']);
        $('#patient-select-widget').selectpicker('refresh');
        $('#study-select-widget').selectpicker('refresh');
        $('#series-select-widget').selectpicker('refresh');
    });

    var instanceTable = new Tabulator("#instanceTable", {
        ajaxConfig:"POST",
        ajaxContentType:"json",
        maxHeight:"400px",
        layout:"fitDataFill",
        placeholder:"No Data Set",
        movableRows:true,
        selectable:true,
        index:"num",
        columns:[
            {title:"", field:"num", resizable:true, headerSort:true, hozAlign:"center"},
            {title:"OrthancInstance", field:"orthanc_id", resizable:false, headerSort:false, visible:false},
            {title:"Date / Time", field:"instance_datetime", resizable:true, headerSort:false, hozAlign:"center"},
            {title:"Label", field:"instance_label", resizable:false, headerSort:false, hozAlign:"center"}
        ],
    });

    function loadInstanceTable(){
        var series_orthanc_ids = $('#series-select-widget').val();  //multiple select possible
        instanceTable.setData(orthancCallsGetInstancesForSeries, {'series_orthanc_ids': series_orthanc_ids})
        .then(function(){
            instanceTable.selectRow();
        });
    };

    instanceTable.on("rowSelectionChanged", function(data, rows, selected, deselected){
        //rows - array of row components for the currently selected rows in order of selection
        //data - array of data objects for the currently selected rows in order of selection
        //selected - array of row components that were selected in the last action
        //deselected - array of row components that were deselected in the last action
        //console.log(rows[0].getData().orthanc_id);
        if (rows.length > 0){
            getImageDescription(rows[0].getData().orthanc_id, function(data) {
                $("#imageDescriptionText").text(data);
            });
        }
        else{
            $("#imageDescriptionText").text('');
        }
    });

    $('#instanceTableSelectAllButton').on("click", function(){
        instanceTable.selectRow();
    });
    $('#instanceTableDeselectAllButton').on("click", function(){
        instanceTable.deselectRow();
    });
    
});

function getImageDescription(orthanc_instance_id, callback){
    $.ajax({
        type: 'POST', 
        url: orthancCallsGetImageDescription,
        data: JSON.stringify({'orthanc_instance_id': orthanc_instance_id}), 
        dataType: 'html',
        contentType: 'application/json'
    })
    .done(callback)
    .fail(function( jqXHR, textStatus, error ) {

    });
}

function getSeriesDescription(orthanc_series_id, callback){
    $.ajax({
        type: 'POST', 
        url: orthancCallsGetSeriesDescription,
        data: JSON.stringify({'orthanc_series_id': orthanc_series_id}), 
        dataType: 'json',
        contentType: 'application/json'
    })
    .done(callback)
    .fail(function( jqXHR, textStatus, error ) {
        
    });
}