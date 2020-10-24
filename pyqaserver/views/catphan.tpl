<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Catphan</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
	<link href="/css/module_general.css" rel="stylesheet">

	<script type="application/javascript">
		function resizeIFrameToFitContent(iFrame) {
			if (iFrame.contentWindow.document.body.scrollHeight >= 2000) {
				iFrame.height = iFrame.contentWindow.document.body.scrollHeight + 200 + "px";
			}
			if (iFrame.contentWindow.document.body.scrollHeight < 2000) {
				iFrame.height = 2300 + "px";
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
			xmlhttp.open("POST", "/searchStudies/" + str, true);
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
			xmlhttp.open("POST", "/searchSeries/" + str, true);
			xmlhttp.send();
		}


		function changeDecimal() {
			this.value = this.value.replace(/,/, '.');
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
					document.getElementById("stationname_dd").innerHTML = "<strong>" + "Station:</strong> "  + temp["6"] ;
					document.getElementById("datetime").innerHTML = "<strong>" + "Date/Time:</strong> " + temp["1"];
					document.getElementById("numofinstances").innerHTML = "<strong>" + "Instances:</strong> " + temp["2"];
					document.getElementById("manufacturer").innerHTML = "<strong>" + "Manufacturer:</strong> "  + temp["3"] ;
					document.getElementById("modality").innerHTML = "<strong>" + "Modality:</strong> "  + temp["4"] ;
					document.getElementById("protocol").innerHTML = "<strong>" + "Protocol:</strong> "  + temp["5"] ;
					document.getElementById("hidden_datetime").value = temp["1"];
					button.disabled = false;
				}
				
			}
			xmlhttp.open("POST", "/searchSeriesTags/" + str, true);
			xmlhttp.send();
			document.getElementById("info_link").href = "{{orthanc_url}}" + "/app/explorer.html#series?uuid=" + str;
		}

		function Calculate() {
			var phantom = $('#phantom').val();
			var machine = $('#machine').val();
			var beam = $('#beam').val();
			var series = $('#Series').val();
			// Get colormap
			var colormap = document.getElementById("set_colormap");
			var str_colormap = colormap.options[colormap.selectedIndex].value;

			document.getElementById("hidden_displayname").value = "{{displayname}}";
			document.getElementById("hidden_phantom").value = phantom;
			document.getElementById("hidden_machine").value = machine;
			document.getElementById("hidden_beam").value = beam;
			document.getElementById("hidden_ref").value = document.getElementById("usereference").checked;
			document.getElementById("hidden_HUdelta").value = document.getElementById("HU_delta").checked;
			document.getElementById("hidden_colormap").value = str_colormap;

			document.getElementById("Calculate").disabled = true;
			document.getElementById("mySpinner").style.display = "block";
			enabledisable("PatientName", true);
			enabledisable("Study", true);
			enabledisable("Series", true);

			document.getElementById("send_calc").action = "/catphan_calculate/"+series;
			document.getElementById("send_calc").submit();
			
		}

		function enableButton() {
			enabledisable("PatientName", false);
			enabledisable("Study", false);
			enabledisable("Series", false);
			document.getElementById("mySpinner").style.display = "none";
			document.getElementById("Calculate").disabled = false;
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
				<div class="navbar-brand logo">Catphan</div>
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
					<select class="selectpicker form-control" data-live-search="true" data-size="15" name="Series" id="Series">
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
						<h3 class="panel-title">Selected series</h3>
					</div>
					<div class="panel-body">
						
						<div class="form-group">
							<p class="text-left" id="stationname_dd"><strong>Station:</strong></p>
							<p class="text-left" id="datetime"><strong>Date/Time:</strong></p>
							<p class="text-left" id="numofinstances"><strong>Instances:</strong></p>
							<p class="text-left" id="manufacturer"><strong>Manufacturer:</strong></p>
							<p class="text-left" id="modality"><strong>Modality:</strong></p>
							<p class="text-left" id="protocol"><strong>Protocol:</strong></p>

							<a href="" target="_blank" id="info_link" class="btn btn-default btn-block" role="button">View all images</a>
						</div>
					</div>
				</div>

				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Settings</h3>
					</div>
					<div class="panel-body">
						<div class="form-group">
							<div class="form-group">
								<label class="control-label" for="select_mlc">Select phantom:</label>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon">Phantom:</span>
									<select class="selectpicker form-control" name="phantom" id="phantom">
										% for k in machines_beams_phantoms:
											<option value="{{k}}">{{k}}</option>
										% end
									</select>
								</div>
							</div>
							<div class="form-group">
								<label class="control-label" for="select_mlc">Select machine:</label>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon">Machine:</span>
									<select class="selectpicker form-control" name="machine" id="machine">
										% for k in machines_beams_phantoms[list(machines_beams_phantoms.keys())[0]]:
											<option value="{{k[0]}}">{{k[0]}}</option>
										% end
									</select>
								</div>
							</div>
							<div class="form-group">
								<label class="control-label" for="select_mlc">Select beam:</label>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon">Beam:</span>
									<select class="selectpicker form-control" name="beam" id="beam">
										% if machines_beams_phantoms[list(machines_beams_phantoms.keys())[0]]:
										% 	for k in machines_beams_phantoms[list(machines_beams_phantoms.keys())[0]][0][1]:
												<option value="{{k}}">{{k}}</option>
										% 	end
										% end
									</select>
								</div>
							</div>
						</div>
						<div class="checkbox">
							<label>
								<input type="checkbox" checked id = "usereference"  name="usereference">
								Analyze reference?
							</label>
						</div>
						<div class="checkbox">
							<label>
								<input type="checkbox" checked id = "HU_delta"  name="HU_delta">
								Show HU Delta?
							</label>
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
			</div>
			<div class="col-xs-12 col-md-9">
				<iframe name="receiver2" height="100%" width="100%" id="receiver2" onload="resizeIFrameToFitContent(this); enableButton();"></iframe>
			</div>
		</div>
	</div>


	<form target = "receiver2" id = "send_calc" method="post" autocomplete="off">
		<input type="hidden" name="hidden_phantom" id="hidden_phantom" value="" />
		<input type="hidden" name="hidden_beam" id="hidden_beam" value="" />
		<input type="hidden" name="hidden_machine" id="hidden_machine" value="" />
		<input type="hidden" name="hidden_ref" id="hidden_ref" value="" />
		<input type="hidden" name="hidden_HUdelta" id="hidden_HUdelta" value="" />
		<input type="hidden" name="hidden_colormap" id="hidden_colormap" value="" />
		<input type="hidden" name="hidden_displayname" id="hidden_displayname" value="" />
		<input type="hidden" name="hidden_datetime" id="hidden_datetime" value="" />
	</form>


	<script>
		var MACHINES_ENERGIES =  {{!machines_beams_phantoms}};

		function change_machines(){
			var selected_phantom = $('#phantom').val();
			var selected_machine = MACHINES_ENERGIES[selected_phantom];
            var html = [];
            for (j = 0; j < selected_machine.length; j++) {
            	html.push("<option " + "value='" + selected_machine[j][0] + "' selected>" + selected_machine[j][0] + "");
            }

            $('#machine').html(html);
            $('#machine').selectpicker('refresh');
            change_beams();
        }

        function change_beams(){
			var selected_phantom = $('#phantom').val();
			var selected_machines = $('#machine').prop('selectedIndex');
			
			if (MACHINES_ENERGIES[selected_phantom].length!=0){
				var selected_beams = MACHINES_ENERGIES[selected_phantom][selected_machines][1];
			}
			else{
				var selected_beams = [];
			}

            var html = [];
            for (j = 0; j < selected_beams.length; j++) {
            	html.push("<option " + "value='" + selected_beams[j] + "' selected>" + selected_beams[j] + "");
            }

            $('#beam').html(html);
            $('#beam').selectpicker('refresh');
        }

		$(document).ready(function() {
			$('#PatientName').on('change', function(){
				getStudy();
			});
			$('#Study').on('change', function(){
				getSeries();
			});
			$('#Series').on('change', function(){
				showTable();
			});
			$('#phantom').on('change', function(){
				change_machines();
			});
			$('#machine').on('change', function(){
				change_beams();
			});
		});
	</script>
</body>


</html>