<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Dynalog module</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-datepicker.min.js"></script>
    <link href="/css/module_general.css" rel="stylesheet">
	<link href="/bootstrap/css/bootstrap-datepicker.css" rel="stylesheet">
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">

	<script type="application/javascript">

			function deleteTable(table) {
				while (table.rows.length > 1) {
					table.deleteRow(1);
				}
			}

			function enabledisable(element, truefalse){
				$('#'+element).prop('disabled', truefalse);
				$('#'+element).selectpicker('refresh');
			}

			function changeOptions(select_id, options, values) {
				var html = [];
				for (j = 0; j < options.length; j++) {
					html.push("<option " + "value='" + values[j] + "'>" + options[j] + "");
				}
				$('#' + select_id).html(html);
				$('#' + select_id).selectpicker('refresh');
				return;
			}

			function getPatients() {
				var selected_dates = $('#date').datepicker('getFormattedDate');

				var formData = new FormData();
				var selected_folder = document.getElementById("filter_folder");
				var folder = selected_folder.options[selected_folder.selectedIndex].value;
				formData.append("folder", folder);

				if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = JSON.parse(this.responseText);
						changeOptions("Patient", temp[0], temp[1]);
					}
				}
				xmlhttp.open("POST", "/dynalogPatients/" + selected_dates, true);
				xmlhttp.send(formData);
			}
		

			function getRecords(id) {
				var str = $('#'+id).val();
				var formData = new FormData();
				formData.append("patient", str);

				if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = JSON.parse(this.responseText);
						changeOptions("Records", temp, temp);
					}
				}
				xmlhttp.open("POST", "/dynalogRecords", true);
				xmlhttp.send(formData);
			}

			function showTable() {
				var str_patient = $('#Patient').val();
				var str_record = $('#Records').val();
				var formData = new FormData();
				formData.append("record", str_record);
				formData.append("patient", str_patient);

				if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}

				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {

						temp = JSON.parse(this.responseText);
						var table = document.getElementById("t03");
						deleteTable(table);

						var view_records_table = [];
						var view_records_nr = [];
						for (m = 0; m < temp.length; m++) {
							current_row = temp[m];
							var row = table.insertRow(m + 1);
							row.insertCell(0).innerHTML = m + 1;
							row.insertCell(1).innerHTML = current_row[0];
							row.insertCell(2).innerHTML = current_row[1];
							row.insertCell(3).innerHTML = current_row[2];
							row.insertCell(4).innerHTML = current_row[3];
							row.insertCell(5).innerHTML = current_row[4];
							row.insertCell(6).innerHTML = current_row[5];
							row.insertCell(7).innerHTML = current_row[6];
							row.insertCell(8).innerHTML = current_row[7];
							row.insertCell(9).innerHTML = current_row[8];
							row.insertCell(10).innerHTML = current_row[9];
							row.insertCell(11).innerHTML = current_row[10];
							row.insertCell(12).innerHTML = current_row[11];
							row.insertCell(13).innerHTML = current_row[14];
							row.insertCell(14).innerHTML = current_row[15];
							view_records_table.push(current_row[13] + ",,," + current_row[12]);
							view_records_nr.push(m+1);
						}
						changeOptions("view_record", view_records_nr, view_records_table);
					}
				}
				xmlhttp.open("POST", "/dynalogRecordData", true);
				xmlhttp.send(formData);
			}

			function RetrieveAllPatients(){
				if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = JSON.parse(this.responseText);
						changeOptions("Patient", temp[0], temp[1]);
					}
				}
				xmlhttp.open("POST", "/dynalogPatients/" + "getall", true);
				xmlhttp.send();
				
			}

			function RetrieveFilteredPatients(){

				var filter = document.getElementById("patient_filter").value;
				var formData = new FormData();
				formData.append("filter", filter);

				var selected_label = document.getElementById("filter_folder");
				var label = selected_label.options[selected_label.selectedIndex].value;
				formData.append("label", label);

				if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = JSON.parse(this.responseText);
						changeOptions("Patient", temp[0], temp[1]);
					}
				}
				xmlhttp.open("POST", "/dynalogPatients/" + "getfiltered", true);
				xmlhttp.send(formData);
			}

			function GetReportLast(){
				var selected_folder = document.getElementById("filter_folder");
				var folder = selected_folder.options[selected_folder.selectedIndex].value;
				document.getElementById("hidden_folder").value = folder;
				document.getElementById("hidden_date").value = "";
				document.getElementById("get_report").action = "/dynalogGetReportDate";
				document.getElementById("get_report").submit();
			}


			function GetHistograms(){
				var selected_folder = document.getElementById("filter_folder");
				var folder = selected_folder.options[selected_folder.selectedIndex].value;
				var selected_date = $('#date').datepicker('getFormattedDate');
				var selected_date2 = $('#date2').datepicker('getFormattedDate');
				document.getElementById("hidden_histdensity").value = document.getElementById("histogram_density").checked;
				document.getElementById("hidden_histlog").value = document.getElementById("histogram_log").checked;
				document.getElementById("hidden_folder").value = folder;
				document.getElementById("hidden_date").value = selected_date;
				document.getElementById("hidden_date2").value = selected_date2;
				document.getElementById("get_report").action = "/dynalogHistograms";
				document.getElementById("get_report").submit();

			}

			function GetReportSelectedDate(){

				var selected_date = $('#date').datepicker('getFormattedDate');
				var selected_date2 = $('#date2').datepicker('getFormattedDate');
				if (selected_date=="" || selected_date2==""){
					alert("Please define the time interval.");
				}
				else{
					var selected_folder = document.getElementById("filter_folder");
					var folder = selected_folder.options[selected_folder.selectedIndex].value;
					document.getElementById("hidden_folder").value = folder;
					document.getElementById("hidden_date").value = selected_date;
					document.getElementById("hidden_date2").value = selected_date2;
					document.getElementById("get_report").action = "/dynalogGetReportDate";
					document.getElementById("get_report").submit();
				}
			}

			function GetBigError(){
				var selected_date = $('#date').datepicker('getFormattedDate');
				var selected_date2 = $('#date2').datepicker('getFormattedDate');
				if ((selected_date=="" && selected_date2!="")||(selected_date!="" && selected_date2=="")){
					alert("Either leave dates empty (full search), or define both.");
				}
				else{
					var selected_folder = document.getElementById("filter_folder");
					var folder = selected_folder.options[selected_folder.selectedIndex].value;
					var error = document.getElementById("set_diffmax2").value;
					document.getElementById("hidden_folder").value = folder;
					document.getElementById("hidden_date").value = selected_date;
					document.getElementById("hidden_date2").value = selected_date2;
					document.getElementById("get_report").action = "/dynalogGetBigError/"+error;
					document.getElementById("get_report").submit();
				}

			}
			
			function GetReportSelectedPatient(){
				str = $('#Patient').val();
				if (str==""){
					alert("Please pick a patient.");
				}
				else{
					document.getElementById("hidden_patient").value = str;
					document.getElementById("get_report").action = "/dynalogGetReportPatient";
					document.getElementById("get_report").submit();
				}
			}

			function GetReportUploads(){
				document.getElementById("get_report").action = "/dynalogGetReportUploads";
				document.getElementById("get_report").submit();
			}

			function Analyze(){
				var str_selected_file = $('#view_record').val();
				var str_selected_mlc = $('#select_mlc').val();

				var form = document.getElementById("send_calc");
				form.action = "/dynalog_analyze";
				document.getElementById("filename_calc").value = str_selected_file;
				document.getElementById("mlc").value = str_selected_mlc;
				document.getElementById("gamma_DTA").value = document.getElementById("set_DTA").value;
				document.getElementById("gamma_DD").value = document.getElementById("set_DD").value;
				document.getElementById("gamma_thres").value = document.getElementById("set_threshold").value;
				document.getElementById("gamma_res").value = document.getElementById("set_resolution").value;
				form.submit();
			}
	</script>
	
</head>


<body>
	<div class="navbar navbar-inverse navbar-fixed-top">
		<div class="container">
			<div class="navbar-header">
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>
				<div class="navbar-brand logo">Dynalogs</div>
			</div>
			<div class="navbar-collapse collapse">
				<ul class="nav navbar-nav navbar-right">
					<p class="navbar-text">Signed in as: <strong>{{displayname}}</strong></p>
					<li class="active"><a href="/docs/build/html/index.html" target="_blank">Help</a></li>
				</ul>
			</div>
		</div>
	</div>
	<div class="container">
		<div class="row">
			<div class="col-xs-12 col-md-3">
				<div class="input-group">
					<span class="input-group-addon" id="sizing-addon2">Filter by date1:</span>
					<input class="form-control" id="date" name="date" placeholder="DD/MM/YYYY" data-date-format="dd-mm-yyyy" type="text"> 
				</div>
			</div>
			<div class="col-xs-12 col-md-3">
				<div class="input-group">
					<span class="input-group-addon" id="sizing-addon2">Date2:</span>
					<input class="form-control" id="date2" name="date2" placeholder="DD/MM/YYYY" data-date-format="dd-mm-yyyy" type="text"> 
				</div>
			</div>
			<div class="col-xs-12 col-md-3">
				<div class="input-group">
					<span class="input-group-addon" id="sizing-addon2">Patient:</span>
					<select class="selectpicker form-control" data-live-search="true" data-size="15" name="Patient" id="Patient">
						<option value=""></option>
					</select>
				</div>
			</div>
			<div class="col-xs-12 col-md-3">
				<div class="input-group">
					<span class="input-group-addon" id="sizing-addon2">Records:</span>
					<select class="selectpicker form-control" data-live-search="true" data-size="15" name="Records" id="Records" onclick="showTable();">
						<option value=""></option>
					</select>
				</div>
			</div>
		</div>
	</div>

	<div class="threepart-container container">
		<div class="row">
			<div class="col-xs-12 col-md-3">
				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Analysis</h3>
					</div>
					<div class="panel-body" id="settings_panel">
						<div class="form-group">
							<label class="control-label" for="view_record">Select field for analysis:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon">Select field:</span>
								<select class="selectpicker form-control" data-size="15" name="view_record" id="view_record">
									<option value=""></option>
								</select>
							</div>
						</div>
						<div class="form-group">
							<label class="control-label" for="select_mlc">Select MLC:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon">Select MLC:</span>
								<select class="form-control" name="select_mlc" id="select_mlc">
									<option value="Varian_120">Varian_120</option>
									<option value="Varian_120HD">Varian_120HD</option>
									<option value="Varian_80">Varian_80</option>
								</select>
							</div>
						</div>
						<div class="form-group">
							<label class="control-label" for="select_mlc">Gamma analysis settings:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:60%">DTA [mm]:</span>
								<input type="text" class="form-control" id="set_DTA" value="{{DTA}}" placeholder="DTA" onkeyup="this.value=this.value.replace(/,/,'.');">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">DD [%]:</span>
								<input type="text" class="form-control" id="set_DD" value="{{DD}}" placeholder="DD" onkeyup="this.value=this.value.replace(/,/,'.');">
							</div>
					
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Threshold:</span>
								<input type="text" class="form-control" id="set_threshold" value="{{threshold}}" placeholder="Threshold" onkeyup="this.value=this.value.replace(/,/,'.');" >
							</div>
					
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Resolution [mm]:</span>
								<input type="text" class="form-control" id="set_resolution" value="{{resolution}}" placeholder="Resolution" onkeyup="this.value=this.value.replace(/,/,'.');">
							</div>
						</div>
						
						<button type="submit" class="btn btn-default btn-block" id="view_record_button" name="view_record_button" onclick="Analyze();">Analyze</button>
					</div>
				</div>
				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Other options</h3>
					</div>
					<div class="panel-body" id="settings_panel">
						<button type="button" class="btn btn-default btn-block" onclick="RetrieveAllPatients();">Get all patients!
						</button>
						<p>
							<div class="form-group">
								<label class="control-label" for="view_record">Filter patients:</label>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon">Select repository:</span>
									<select class="form-control" name="filter_folder" id="filter_folder">
										% for k in labels:
											<option value="{{k}}">{{k}}</option>
										% end
									</select>
								</div>
							</div>
							<div class="input-group">
								<input type="text" class="form-control" id="patient_filter" placeholder="Filter patient list...">
								<span class="input-group-btn">
									<button class="btn btn-default" type="button" onclick="RetrieveFilteredPatients();">Go!</button>
								</span>
							</div>
						</p>
						<p>
							<div class="form-group">
								<label class="control-label" for="view_record">Get report:</label>
								<button type="button" class="btn btn-default btn-block" onclick="GetReportLast();">Last upload</button>
								<button type="button" class="btn btn-default btn-block" onclick="GetReportSelectedDate();">Between dates</button>
								<button type="button" class="btn btn-default btn-block" onclick="GetReportSelectedPatient();">For selected patient</button>
								<button type="button" class="btn btn-default btn-block" onclick="GetReportUploads();">Get upload dates</button>
								<p>
									<div class="input-group">
									<span class="input-group-btn">
										<button class="btn btn-default" type="button" onclick="GetBigError();">MAX DIFF2 [mm] > </button>
									</span>
									<input type="text" class="form-control" id="set_diffmax2" placeholder="" value="5">
									</div>
								</p>
							</div>
						</p>
						<p>
							<div class="form-group">
								<label class="control-label" for="view_record">Histograms:</label>
								<div class="checkbox">
									<label>
										<input type="checkbox" id="histogram_density" name="histogram_density" value="False">
										Histogram - probability density?
									</label>
								</div>
								<div class="checkbox">
									<label>
										<input type="checkbox" id="histogram_log" name="histogram_log" value="False">
										Histogram - logarithmic scale?
									</label>
								</div>
							</div>
							<button type="button" class="btn btn-default btn-block" onclick="GetHistograms();">Histograms between dates</button>
						</p>
					</div>
				</div>
			</div>

			<div class="col-xs-12 col-md-9">
				<table id="t03" class="table table-condensed table-hover">
					<tr>
						<td>#</td>
						<td>Field</td>
						<td>Gantry</td>
						<td>Time</td>
						<td>Snaps</td>
						<td>Holds</td>
						<td>Max RMS<br>[mm]</td>
						<td>Max RMS2<br>[mm]</td>
						<td>Max DIFF<br>[mm]</td>
						<td>Max DIFF2<br>[mm]</td>
						<td>RMS avg<br>[mm]</td>
						<td>&gamma; avg.</td>
						<td>&gamma;<1 [%]</td>
						<td>dd/dta/thresh/res</td>
						<td>Repository</td>
					</tr>
				</table>
			</div>
		</div>
	</div>

	<form target="_blank" id="send_calc" method="post" autocomplete="off">
		<input type="hidden" name="filename_calc" id="filename_calc" value="" />
		<input type="hidden" name="mlc" id="mlc" value="" />
		<input type="hidden" name="gamma_DTA" id="gamma_DTA" value="" />
		<input type="hidden" name="gamma_DD" id="gamma_DD" value="" />
		<input type="hidden" name="gamma_thres" id="gamma_thres" value="" />
		<input type="hidden" name="gamma_res" id="gamma_res" value="" />
	</form>
	
	<form target="_blank" id="get_report" method="post" autocomplete="off">
		<input type="hidden" name="hidden_date" id="hidden_date" value=""/>
		<input type="hidden" name="hidden_patient" id="hidden_patient" value=""/>
		<input type="hidden" name="hidden_folder" id="hidden_folder" value=""/>
		<input type="hidden" name="hidden_histdensity" id="hidden_histdensity" value=""/>
		<input type="hidden" name="hidden_histlog" id="hidden_histlog" value=""/>
		<input type="hidden" name="hidden_date2" id="hidden_date2" value=""/>
	</form>

</body>

<script>
		$(document).ready(function () {
			var date_input = $('input[name="date"]'); //our date input has the name "date"
			var date_input2 = $('input[name="date2"]'); // date (final) for histograms
			var container = "body";
			var options = {
				format: "yyyy-mm-dd",
				container: container,
				todayHighlight: true,
				autoclose: true,
				clearBtn: true
			};
			date_input.datepicker(options).on('changeDate', function (e) {
				getPatients();
			});
			date_input2.datepicker(options).on('changeDate', function (e) {
				
			});

			$('#Patient').on('change', function(){
				getRecords(this.id);
			});
			$('#Records').on('change', function(){
				showTable();
			});

		});
</script>

</html>