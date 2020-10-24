<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Planar imaging</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
	<link href="/css/module_general.css" rel="stylesheet">

	<script type="application/javascript">
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

		function get_machines(){
			var str = $('#phantom').val();

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

		function getImage() {
			var image = $('#image1').val();
			document.getElementById("img_preview").src = "";
			document.getElementById("img_preview").alt = "Loading";

			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xmlhttp = new XMLHttpRequest();
			} else {  // code for IE6, IE5
				xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xmlhttp.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					document.getElementById("img_preview").src = "data:image/png;base64," + this.responseText;
					document.getElementById("img_preview").alt = "";
				}
			}
			xmlhttp.open("POST", "/getInstanceImage/" + image, true);
			xmlhttp.send();
		}

		function getImageDescription() {
			var image = $('#image1').val();

			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xmlhttp = new XMLHttpRequest();
			} else {  // code for IE6, IE5
				xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xmlhttp.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					var imagedescription = document.getElementById("imagedescription_dd");
					imagedescription.innerHTML = "<small>"+this.responseText.replace(/(\r\n|\n|\r)/gm,"<br>")+"</small>";
				}
			}
			xmlhttp.open("POST", "/getInstanceImageDescription/" + image, true);
			xmlhttp.send();
		}

		function showTable() {
			var str = $('#Series').val();
			var button = document.getElementById("Calculate");
			button.disabled = true;
			
			var image1 = $('#image1');
			enabledisable("image1", true);

			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xmlhttp = new XMLHttpRequest();
			} else {  // code for IE6, IE5
				xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xmlhttp.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					temp = JSON.parse(this.responseText);
					var stationname = document.getElementById("stationname_dd");
					stationname.innerHTML = "Station: " + "<b>" + temp["5"] + "</b>";

					var table = document.getElementById("t03");
					var opt_images = [];
					for (var i = 0; i < temp["1"].length; i++) {
						opt_images.push(i + 1);
					}
					changeOptions("image1", opt_images, temp["4"]);
					deleteTable(table);

					for (m = 0; m < temp["3"].length; m++) {
						var row = table.insertRow(m + 1);
						row.insertCell(0).innerHTML = m + 1;
						row.insertCell(1).innerHTML = temp["1"][m];
						row.insertCell(2).innerHTML = temp["3"][m];
					}
					button.disabled = false;
					image1.change();
					enabledisable("image1", false);
					document.getElementById("hidden_datetime").value = temp["3"][0]; // get date time from first row
				}
				
			}
			xmlhttp.open("POST", "/searchInstances/" + str, true);
			xmlhttp.send();
			document.getElementById("info_link").href = "{{orthanc_url}}" + "/app/explorer.html#series?uuid=" + str;
		}

		function Calculate() {
	        var image1 = $('#image1').val();
			
			var phantom = $('#phantom').val();
			var machine = $('#machine').val();
			var beam = $('#beam').val();
			
			var leedstorrot1 = document.getElementById("leedstorrot1").value;
			var leedstorrot2 = document.getElementById("leedstorrot2").value;
			var clip_box = document.getElementById("clip_box").value;
			var invert = document.getElementById("invertcheckbox").checked;
			var bbox = document.getElementById("bbox").checked;
			// Get colormap
			var colormap = document.getElementById("set_colormap");
			var str_colormap = colormap.options[colormap.selectedIndex].value;
			
			if (clip_box==""||leedstorrot1==""||leedstorrot2=="") {
				alert("Boxes must not be empty! Put 0 for undefined value.");
			}
			else {
				document.getElementById("hidden_clipbox").value = clip_box;
				document.getElementById("hidden_phantom").value = phantom;
				document.getElementById("hidden_machine").value = machine;
				document.getElementById("hidden_beam").value = beam;
				document.getElementById("hidden_leedsrot1").value = leedstorrot1;
				document.getElementById("hidden_leedsrot2").value = leedstorrot2;
				document.getElementById("hidden_inv").value = invert;
				document.getElementById("hidden_bbox").value = bbox;
				document.getElementById("hidden_ref").value = document.getElementById("usereference").checked;

				document.getElementById("Calculate").disabled = true;
				document.getElementById("mySpinner").style.display = "block";
				enabledisable("PatientName", true);
				enabledisable("Study", true);
				enabledisable("Series", true);
				enabledisable("image1", true);
				document.getElementById("hidden_colormap").value = str_colormap;
				document.getElementById("send_calc").action = "/planar_imaging_calculate/"+image1;
				document.getElementById("send_calc").submit();
			}
		}

		function enableButton() {
			enabledisable("PatientName", false);
			enabledisable("Study", false);
			enabledisable("Series", false);
			enabledisable("image1", false);
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
				<div class="navbar-brand logo">Planar imaging</div>
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
						<h3 class="panel-title">Select image</h3>
					</div>
					<div class="panel-body">
						<div class="form-group">
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon2">Image:</span>
								<select class="selectpicker form-control" name="image1" id="image1">
									<option value=""></option>
								</select>
							</div>
						</div>
						<div class="form-group">
							<div class="thumbnail" id="img_thumbnail">
								<img id="img_preview" src="" alt="">
							</div>
						</div>
						<div class="form-group">
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

							<label class="control-label" for="select_mlc">Analysis settings:</label>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Clipbox: </span>
								<input id="clip_box" class="form-control" type="text" onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">cm</span>
							</div>
					
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Force angle 1: </span>
								<input id ="leedstorrot1" class="form-control" type="text" onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">deg</span>
							</div>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Force angle 2: </span>
								<input id ="leedstorrot2" class="form-control" type="text" onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">deg</span>
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
						<div class="checkbox">
							<label>
								<input type="checkbox" id = "bbox" checked name="bbox">
								Show bounding box?
							</label>
						</div>
						<div class="checkbox">
							<label>
								<input type="checkbox" id = "invertcheckbox" name="invertcheckbox">
								Invert image?
							</label>
						</div>
						<div class="checkbox">
							<label>
								<input type="checkbox" checked id = "usereference"  name="usereference">
								Analyze reference?
							</label>
						</div>
						
					</div>
				</div>
				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Image list</h3>
					</div>
					<div class="panel-body">
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
							</tr>
						</table>
					</div>
				</div>
			</div>

			<div class="col-xs-12 col-md-9">
				<iframe name="receiver2" height="100%" width="100%" id="receiver2" onload="resizeIFrameToFitContent(this);enableButton();"></iframe>
			</div>
		</div>
	</div>

	<form target = "receiver2" id = "send_calc" method="post" autocomplete="off">
		<input type="hidden" name="hidden_phantom" id="hidden_phantom" value="" />
		<input type="hidden" name="hidden_machine" id="hidden_machine" value="" />
		<input type="hidden" name="hidden_beam" id="hidden_beam" value="" />
		<input type="hidden" name="hidden_leedsrot1" id="hidden_leedsrot1" value="" />
		<input type="hidden" name="hidden_leedsrot2" id="hidden_leedsrot2" value="" />
		<input type="hidden" name="hidden_inv" id="hidden_inv" value="" />
		<input type="hidden" name="hidden_bbox" id="hidden_bbox" value="" />
		<input type="hidden" name="hidden_clipbox" id="hidden_clipbox" value="" />
		<input type="hidden" name="hidden_ref" id="hidden_ref" value="" />
		<input type="hidden" name="hidden_colormap" id="hidden_colormap" value="" />
		<input type="hidden" name="hidden_displayname" id="hidden_displayname" value="{{displayname}}" />
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
			$('#image1').on('change', function(){
				getImage();
				getImageDescription();
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