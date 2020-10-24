<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Starshot module</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
	<link href="/css/module_general.css" rel="stylesheet">

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
			var image = $('#Images').val();
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
			var image = $('#Images').val();

			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xmlhttp = new XMLHttpRequest();
			} else {  // code for IE6, IE5
				xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xmlhttp.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					var imagedescription = document.getElementById("imagedescription_dd");
					document.getElementById("hidden_imgdescription").value = temp["6"]; // to send back to server
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
			
			var images = $('#Images');
			enabledisable("Images", true);

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
					changeOptions("Images", opt_images, temp["4"]);
					deleteTable(table);

					for (m = 0; m < temp["3"].length; m++) {
						var row = table.insertRow(m + 1);
						row.insertCell(0).innerHTML = m + 1;
						row.insertCell(1).innerHTML = temp["1"][m];
						row.insertCell(2).innerHTML = temp["3"][m];
					}
					button.disabled = false;
					images.change();
					enabledisable("Images", false);
					document.getElementById("hidden_datetime").value = temp["3"][0]; // get date time from first row
					document.getElementById("hidden_station").value = temp["5"]; // to send back to server
				}
				
			}
			xmlhttp.open("POST", "/searchInstances/" + str, true);
			xmlhttp.send();
			document.getElementById("info_link").href = "{{orthanc_url}}" + "/app/explorer.html#series?uuid=" + str;
		}

		function Calculate() {
			var series = $('#Series').val();
			var image = $('#Images').val();
			
			var clip_box = document.getElementById("clip_size").value;
			var radius = document.getElementById("radius").value;
			var peak_height = document.getElementById("peak_height").value;
			var start_point_x = document.getElementById("start_point_x").value;
			var start_point_y = document.getElementById("start_point_y").value;
			var SID = document.getElementById("SID").value;
			var DPI = document.getElementById("DPI").value;

			if (clip_box==""||radius==""||peak_height==""||start_point_x==""||start_point_x==""||SID==""||DPI=="") {
				alert("Boxes must not be empty! Put 0 for undefined value.");
			}
			else {
				document.getElementById("input_nondicom_file").value = "";
				document.getElementById("hidden_clipbox").value = clip_box;
				document.getElementById("hidden_radius").value = radius;
				document.getElementById("hidden_mph").value = peak_height;
				document.getElementById("hidden_px").value = start_point_x;
				document.getElementById("hidden_py").value = start_point_y;
				document.getElementById("hidden_dpi").value = DPI;
				document.getElementById("hidden_sid").value = SID;
				document.getElementById("hidden_fwhm").value = document.getElementById("set_FWHM").checked;
				document.getElementById("hidden_recursive").value = document.getElementById("set_recursive").checked;
				document.getElementById("hidden_invert").value = document.getElementById("invert_image").checked;
				document.getElementById("hidden_dpi").value = DPI;
				document.getElementById("hidden_sid").value = SID;

				document.getElementById("Calculate").disabled = true;
				document.getElementById("mySpinner").style.display = "block";
				enabledisable("PatientName", true);
				enabledisable("Study", true);
				enabledisable("Series", true);
				enabledisable("Images", true);
				document.getElementById("send_calc").action = "/starshot_calculate/dicom/" + image;
				document.getElementById("send_calc").submit();
			}
		}

		function Calculate_nondicom() {
			
			var clip_box = document.getElementById("clip_size").value;
			var radius = document.getElementById("radius").value;
			var peak_height = document.getElementById("peak_height").value;
			var start_point_x = document.getElementById("start_point_x").value;
			var start_point_y = document.getElementById("start_point_y").value;
			var SID = document.getElementById("SID").value;
			var DPI = document.getElementById("DPI").value;

			if (clip_box==""||radius==""||peak_height==""||start_point_x==""||start_point_x==""||SID==""||DPI=="") {
				alert("Boxes must not be empty! Put 0 for undefined value.");
			}
			else {
				document.getElementById("hidden_clipbox").value = clip_box;
				document.getElementById("hidden_radius").value = radius;
				document.getElementById("hidden_mph").value = peak_height;
				document.getElementById("hidden_px").value = start_point_x;
				document.getElementById("hidden_py").value = start_point_y;
				document.getElementById("hidden_dpi").value = DPI;
				document.getElementById("hidden_sid").value = SID;
				document.getElementById("hidden_fwhm").value = document.getElementById("set_FWHM").checked;
				document.getElementById("hidden_recursive").value = document.getElementById("set_recursive").checked;
				document.getElementById("hidden_invert").value = document.getElementById("invert_image").checked;
				document.getElementById("hidden_dpi").value = DPI;
				document.getElementById("hidden_sid").value = SID;

				document.getElementById("button_nondicom").disabled = true;
				document.getElementById("mySpinner").style.display = "block";
				document.getElementById("send_calc").action = "/starshot_calculate/nondicom/none";
				document.getElementById("send_calc").submit();
			}
		}

		function enableButton() {
			enabledisable("PatientName", false);
			enabledisable("Study", false);
			enabledisable("Series", false);
			enabledisable("Images", false);
			document.getElementById("mySpinner").style.display = "none";
			document.getElementById("Calculate").disabled = false;
			document.getElementById("button_nondicom").disabled = false;
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
				<div class="navbar-brand logo">Starshot</div>
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
								<span class="input-group-addon" id="sizing-addon2">Select image:</span>
								<select class="selectpicker form-control" name="Images" id="Images">
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
							<label class="control-label" for="select_mlc">Analysis settings:</label>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Clipbox: </span>
								<input id="clip_size" class="form-control" type="text" onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">cm</span>
							</div>
					
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Radius: </span>
								<input id="radius" class="form-control" type="text" onkeyup="this.value=this.value.replace(/,/,'.')" value="0.85" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">rel</span>
							</div>

							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Min peak height: </span>
								<input id="peak_height" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="0.25" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">rel</span>
							</div>
						
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Start point: </span>
								<input id="start_point_x" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<input id="start_point_y" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">px</span>
							</div>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">SID: </span>
								<input id="SID" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">mm</span>
							</div>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">DPI: </span>
								<input id="DPI" class="form-control" type="text" onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
							</div>
						</div>

						<div class="checkbox">
							<label>
								<input type="checkbox" checked id="set_FWHM" name="set_FWHM" value="True">
								Set FWHM?
							</label>
						</div>


						<div class="checkbox">
							<label>
								<input type="checkbox" checked id="set_recursive" name="set_recursive" value="True">
								Recursive?
							</label>
						</div>

						<div class="checkbox">
							<label>
								<input type="checkbox" id="invert_image" name="invert_image" value="False">
								Invert image?
							</label>
						</div>
					</div>
				</div>
				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Load external image</h3>
					</div>
					<div class="panel-body">
						<label class="control-label" for="input_nondicom_file">Load tif image:</label>
						<form class="form-inline" id="send_calc" method="post" enctype="multipart/form-data" target="receiver2">
							<p>
								<input type="file" id="input_nondicom_file" class="filestyle" data-buttonName="btn-info" data-placeholder="No file" accept=".tif" name="input_nondicom_file"> 
							</p>
							<p>
								<button type="submit" class="btn btn-default btn-block" id="button_nondicom" onclick="Calculate_nondicom();">Calculate</button>
							</p>
							<input type="hidden" name="hidden_clipbox" id="hidden_clipbox" value="" />
							<input type="hidden" name="hidden_radius" id="hidden_radius" value="" />
							<input type="hidden" name="hidden_mph" id="hidden_mph" value="" />
							<input type="hidden" name="hidden_px" id="hidden_px" value="" />
							<input type="hidden" name="hidden_py" id="hidden_py" value="" />
							<input type="hidden" name="hidden_dpi" id="hidden_dpi" value="" />
							<input type="hidden" name="hidden_sid" id="hidden_sid" value="" />
							<input type="hidden" name="hidden_fwhm" id="hidden_fwhm" value="" />
							<input type="hidden" name="hidden_recursive" id="hidden_recursive" value="" />
							<input type="hidden" name="hidden_invert" id="hidden_invert" value="" />
							<input type="hidden" name="hidden_imgdescription" id="hidden_imgdescription" value="" />
							<input type="hidden" name="hidden_displayname" id="hidden_displayname" value="{{displayname}}" />
							<input type="hidden" name="hidden_datetime" id="hidden_datetime" value="" />
							<input type="hidden" name="hidden_station" id="hidden_station" value="" />
						</form>
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
				<iframe name="receiver2" height="100%" width="100%" id="receiver2" onload="enableButton();"></iframe>
			</div>
		</div>
	</div>

	<script>
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
			$('#Images').on('change', function(){
				getImage();
				getImageDescription();
			});
		});
	</script>
</body>


</html>