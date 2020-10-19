<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Winston-Lutz module</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
	<link href="/css/module_general.css" rel="stylesheet">
	
	<script type="application/javascript">
		var SEND_INSTANCES = [];

		function resizeIFrameToFitContent(iFrame) {
			if (iFrame.contentWindow.document.body.scrollHeight >= 2000) {
				iFrame.height = iFrame.contentWindow.document.body.scrollHeight + 20 + "px";
			}
			if (iFrame.contentWindow.document.body.scrollHeight < 2000) {
				iFrame.height = 2000 + "px";
			}
		}

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

		function getStudy() {
			var str = $('#PatientName').val();

			enabledisable('Study', true);
			enabledisable('Series', true);

			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xmlhttp = new XMLHttpRequest();
			} else {  // code for IE6, IE5
				xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xmlhttp.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					temp = JSON.parse(this.responseText);
					changeOptions("Study", temp[1], temp[0]);
					enabledisable('Study', false);
				}
			}
			xmlhttp.open("POST", "{{plweb_folder}}/searchStudies/" + str, true);
			xmlhttp.send();
		}

		function getSeries() {
			var str = $('#Study').val();

			enabledisable('Series', true);

			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xmlhttp = new XMLHttpRequest();
			} else {  // code for IE6, IE5
				xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xmlhttp.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					temp = JSON.parse(this.responseText);
					changeOptions("Series", temp[1], temp[0]);
					enabledisable('Series', false);
				}
			}
			xmlhttp.open("POST", "{{plweb_folder}}/searchSeries/" + str, true);
			xmlhttp.send();
		}
		
		function changeDecimal() {
			this.value = this.value.replace(/,/, '.');
		}

		function disable_pylinac(){
			if (document.getElementById("couch_test").checked){
				document.getElementById("pylinac").checked=false;
				document.getElementById("pylinac").disabled=true;
				document.getElementById("start_point_x").disabled=false;
				document.getElementById("start_point_y").disabled=false;
				//document.getElementById("show_epid_points").checked=false;
				//document.getElementById("show_epid_points").disabled=true;
				document.getElementById("set_testtype").disabled=false;
			} else {
				document.getElementById("pylinac").disabled=false;
				//document.getElementById("show_epid_points").disabled=false;
				document.getElementById("set_testtype").disabled=true;
				document.getElementById("start_point_x").disabled=true;
				document.getElementById("start_point_y").disabled=true;
			}
		}

		function showTable() {

			var str = $('#Series').val();

			var button = document.getElementById("Calculate");
			button.disabled = true;
			
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
					var tableGNT = document.getElementById("t04");

					deleteTable(table);
					deleteTable(tableGNT);
					
					SEND_INSTANCES = temp["4"];
					var stationname = document.getElementById("stationname_dd");
					document.getElementById("hidden_station").value = temp["5"]; // to send back to server
					stationname.innerHTML = "Station: " + "<b>" + temp["5"] + "</b>";
					var imagedescription = document.getElementById("imagedescription_dd");
					document.getElementById("hidden_imgdescription").value = temp["6"]; // to send back to server
					imagedescription.innerHTML = "<small>"+temp["6"].replace(/(\r\n|\n|\r)/gm,"<br>")+"</small>";
					var pylinac_value = document.getElementById("pylinac").checked;

					for (m = 0; m < temp["3"].length; m++) {
						var row = table.insertRow(m + 1);
						row.insertCell(0).innerHTML = m + 1;
						row.insertCell(1).innerHTML = temp["1"][m];
						row.insertCell(2).innerHTML = temp["3"][m];

						var c = document.createElement("input");
						c.setAttribute("type", "checkbox");
						c.setAttribute("id", "useimg" + String(m + 1));
						c.setAttribute("name", "useimg" + String(m + 1));
						c.setAttribute("checked", true);

						row.insertCell(3).appendChild(c);
					}

					if (pylinac_value == true) {
						for (m = 0; m < temp["3"].length; m++) {
							var gantry = document.createElement('input');
							gantry.setAttribute("id", "gantry" + String(m + 1));
							gantry.setAttribute("name", "gantry" + String(m + 1));
							gantry.setAttribute("type", "text");
							gantry.setAttribute("size", 4);
							gantry.onkeyup = changeDecimal;
							var coll = document.createElement('input');
							coll.setAttribute("id", "coll" + String(m + 1));
							coll.setAttribute("name", "coll" + String(m + 1));
							coll.setAttribute("type", "text");
							coll.setAttribute("size", 4);
							coll.onkeyup = changeDecimal;
							var couch = document.createElement('input');
							couch.setAttribute("id", "couch" + String(m + 1));
							couch.setAttribute("name", "couch" + String(m + 1));
							couch.setAttribute("type", "text");
							couch.setAttribute("size", 4);
							couch.onkeyup = changeDecimal;

							var row = tableGNT.insertRow(m + 1);

							row.insertCell(0).innerHTML = m + 1;

							row.insertCell(1).appendChild(gantry);
							row.insertCell(2).appendChild(coll);
							row.insertCell(3).appendChild(couch);
						}
					}
					button.disabled = false;
					document.getElementById("hidden_datetime").value = temp["3"][0]; // get date time from first row
				}
			}

			xmlhttp.open("POST", "{{plweb_folder}}/searchInstances/" + str.join("/"), true);
			xmlhttp.send();
			document.getElementById("info_link").href = "{{orthanc_url}}" + "/app/explorer.html#series?uuid=" + str[0];
		}

		function Calculate() {
			var series = $('#Series').val();
			var clip_box = document.getElementById("clip_size").value;
			var FitCheckBox_value = document.getElementById("FitCheckBox").checked;
			var pylinac_value = document.getElementById("pylinac").checked;
			var fit;
			var pyl;
			var gnt_angles_empty = false;
			if (FitCheckBox_value == true) {
				fit = "True";
			}
			else {
				fit = "False";
			}
			if (pylinac_value == true) {
				pyl = "True";
				var gnttable = document.getElementById("t04");
				var gnt_angles = [];
				for (m = 1; m < gnttable.rows.length; m++) {
					gnt_angles.push(document.getElementById("gantry" + String(m)).value);
					gnt_angles.push(document.getElementById("coll" + String(m)).value);
					gnt_angles.push(document.getElementById("couch" + String(m)).value);
				}
				document.getElementById("pylinacangles").value = JSON.stringify(gnt_angles);

				var empty_num = 0;
				for (m = 0; m < gnt_angles.length; m++) {
					if (gnt_angles[m] == "") {
						empty_num = empty_num + 1;
					}
				}
				if ((empty_num < gnt_angles.length) && (empty_num > 0)) {
					gnt_angles_empty = true;
				}
			}
			else {
				pyl = "False";
			}

			//Collect which images should be analyzed:
			var useimgtable = document.getElementById("t03");
			var useimglist = [];
			for (m = 1; m < useimgtable.rows.length; m++) {
				useimglist.push(document.getElementById("useimg" + String(m)).checked);
			}
			document.getElementById("useimglist").value = JSON.stringify(useimglist);

			// Get colormap
			var colormap = document.getElementById("set_colormap");
			var str_colormap = colormap.options[colormap.selectedIndex].value;
			
			// Get test type (only couch)
			var test_type = document.getElementById("set_testtype");
			var str_test_type = test_type.options[test_type.selectedIndex].value;

			if (clip_box == "") {
				alert("Box must not be empty!");
			}
			else if (gnt_angles_empty == true) {
				alert("Table of Gantry/Coll/Couch angles must be either empty or full");
			}
			else {
				document.getElementById("instances_list").value = JSON.stringify(SEND_INSTANCES);
				document.getElementById("Calculate").disabled = true;
				document.getElementById("mySpinner").style.display = "block";
				enabledisable("PatientName", true);
				enabledisable("Study", true);
				enabledisable("Series", true);
				document.getElementById("hidden_startx").value = document.getElementById("start_point_x").value;
				document.getElementById("hidden_starty").value = document.getElementById("start_point_y").value;;
				document.getElementById("hidden_colormap").value = str_colormap;
				document.getElementById("hidden_show_epid_points").value = document.getElementById("show_epid_points").checked;
				document.getElementById("hidden_testtype").value = str_test_type;
				document.getElementById("hidden_usecouch").value = document.getElementById("couch_test").checked;
				document.getElementById("send_calc").action = "{{plweb_folder}}/winston_lutz_calculate/" + clip_box + "/" + fit + "/" + pyl;
				document.getElementById("send_calc").submit();
			}
		}

		function enableButton() {
			enabledisable("PatientName", false);
			enabledisable("Study", false);
			enabledisable("Series", false);

			document.getElementById("mySpinner").style.display = "none";
			document.getElementById("Calculate").disabled = false;
		}

		function checkgroup(checked){
			var useimgtable = document.getElementById("t03");
			if (checked){
				for (m = 1; m < useimgtable.rows.length; m++) {
					document.getElementById("useimg" + String(m)).checked = true;
				}
			}
			else{
				for (m = 1; m < useimgtable.rows.length; m++) {
					document.getElementById("useimg" + String(m)).checked = false;
				}
			}
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
				<div class="navbar-brand logo">Winston Lutz</div>
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
					<span class="input-group-addon" id="sizing-addon2">Patient:</span>
					<select class="selectpicker form-control" data-live-search="true" data-size="15" name="PatientName" id="PatientName">
						% for p in range(0, len(names), 1):
						<option value="{{orthanc_id[p]}}">{{names[p]}} ({{IDs[p]}})</option>
						% end
					</select>
				</div>
			</div>
			<div class="col-xs-12 col-md-3">
				<div class="input-group">
					<span class="input-group-addon" id="sizing-addon2">Study:</span>
					<select class="selectpicker form-control" data-live-search="true" data-size="15" name="Study" id="Study">
						<option value=""></option>
					</select>
				</div>
			</div>
			<div class="col-xs-12 col-md-3">
				<div class="input-group">
					<span class="input-group-addon" id="sizing-addon2">Series:</span>
					<select class="selectpicker form-control" multiple data-selected-text-format="count" name="Series" data-live-search="true" data-size="15" id="Series">
						<option value=""></option>
					</select>
				</div>
			</div>
			<div class="col-xs-4 col-md-3">
				<button type="submit" class="btn btn-default" id="Calculate" name="Calculate" onclick="Calculate();">Analyze</button>
				<div class="spinner" id="mySpinner"></div>
			</div>
		</div>
	</div>

	<div class="threepart-container container">
		<div class="row">
			<div class="col-xs-12 col-md-3">

				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Settings</h3>
					</div>
					<div class="panel-body" id="settings_panel">

						<div class="input-group input-group-sm">
							<span class="input-group-addon">Clip box: </span>
							<input id="clip_size" class="form-control" type="text" size="2" onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
							<span class="input-group-addon">cm</span>
						</div>

						<div class="checkbox">
							<label>
								<input type="checkbox" checked id="FitCheckBox" name="FitCheckBox" value="True">
								Zoom in on field?
							</label>
						</div>

						<div class="checkbox">
							<label>
								<input type="checkbox" id="pylinac" name="pylinac" value="False" onchange="showTable();">
								Use Pylinac?
							</label>
						</div>

						<div class="checkbox">
							<label>
								<input type="checkbox" id="show_epid_points" name="show_epid_points" value="False">
								Show EPID2CAX on scatter plot?
							</label>
						</div>	
						<div class="checkbox">
							<label>
								<input type="checkbox" id="couch_test" name="couch_test" value="False" onchange="disable_pylinac();">
								Set test type?
							</label>
						</div>	
						<p>
							<div class="form-group">
								<label class="control-label" for="set_orientation">Choose test type:</label>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon">Test type</span>
									<select class="form-control" name="set_testtype" id="set_testtype" disabled>
										<option value="Gnt/coll + couch rotation">Gnt/coll + couch rotation</option>
										<option value="Couch only">Couch only</option>
										<option value="Collimator only">Collimator only</option>
									</select>
								</div>
							</div>
						</p>
						<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Axis initial guess: </span>
								<input id="start_point_x" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="0" disabled>
								<input id="start_point_y" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="0" disabled>
								<span class="input-group-addon" id="sizing-addon" style="width:20%">mm</span>
							</div>
						<p>
							<div class="form-group">
								<label class="control-label" for="set_orientation">Choose colormap:</label>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon">MPL colormap:</span>
									<select class="form-control" name="set_colormap" id="set_colormap">
										% for c in colormaps:
											<option value="{{c}}">{{c}}</option>
										% end
									</select>
								</div>
							</div>
						</p>
						
					</div>
				</div>

				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Selected images</h3>
					</div>
					<div class="panel-body">
				
						<p class="text-left" id="stationname_dd">Station:</p>
						
						<p>
							<button class="btn btn-default btn-block" type="button" data-toggle="collapse" data-target="#collapseExample" aria-expanded="false" aria-controls="collapseExample">
								Show image description
							</button>
							<div class="collapse" id="collapseExample">
								<div class="well" id="imagedescription_dd">
								</div>
							</div>
						</p>


						<a href="" target="_blank" id="info_link" class="btn btn-default btn-block" role="button">View images</a>

						<table id="t03" class="table table-condensed table-hover">
							<tr>
								<td>
									#
								</td>
								<td>
									Instance
								</td>
								<td>
									Date/Time
								</td>
								<td>
									<input type="checkbox" id="checkallimages" name="checkallimages" checked onchange="checkgroup(this.checked);">
								</td>
							</tr>
						</table>
					</div>
				</div>

				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Angles for pylinac</h3>
					</div>
					<div class="panel-body">
						<table id="t04" class="table table-condensed table-hover">
							<tr>
								<td>
									#
								</td>
								<td>
									Gantry
								</td>
								<td>
									Collimator
								</td>
								<td>
									Couch
								</td>
							</tr>
						</table>
					</div>
				</div>
			</div>

			<div class="col-xs-12 col-md-9">
				<iframe name="receiver2" height="100%" width="100%" id="receiver2" onload="resizeIFrameToFitContent(this); enableButton();"></iframe>
			</div>
		</div>
	</div>
	<form target="receiver2" id="send_calc" method="post" autocomplete="off">
		<input type="hidden" name="pylinacangles" id="pylinacangles" value="" />
		<input type="hidden" name="useimglist" id="useimglist" value="" />
		<input type="hidden" name="instances_list" id="instances_list" value="" />
		<input type="hidden" name="hidden_colormap" id="hidden_colormap" value="" />
		<input type="hidden" name="hidden_show_epid_points" id="hidden_show_epid_points" value="" />
		<input type="hidden" name="hidden_usecouch" id="hidden_usecouch" value="" />
		<input type="hidden" name="hidden_testtype" id="hidden_testtype" value="" />
		<input type="hidden" name="hidden_station" id="hidden_station" value="" />
		<input type="hidden" name="hidden_imgdescription" id="hidden_imgdescription" value="" />
		<input type="hidden" name="hidden_displayname" id="hidden_displayname" value="{{displayname}}" />
		<input type="hidden" name="hidden_datetime" id="hidden_datetime" value="" />
		<input type="hidden" name="hidden_startx" id="hidden_startx" value="" />
		<input type="hidden" name="hidden_starty" id="hidden_starty" value="" />
	</form>

	<script>
		$(document).ready(function() {
			$('#PatientName').on('change', function(){
				getStudy();
			})
			$('#Study').on('change', function(){
				getSeries();
			})
			$('#Series').on('change', function(){
				showTable();
			})
		});
	</script>
</body>


</html>