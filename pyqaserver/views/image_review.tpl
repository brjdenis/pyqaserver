<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Image review</title>

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
			xmlhttp.open("POST", "{{plweb_folder}}/getInstanceImage/" + image, true);
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
					imagedescription.innerHTML = "<small>"+this.responseText.replace(/(\r\n|\n|\r)/gm,"<br>")+"</small>";
				}
			}
			xmlhttp.open("POST", "{{plweb_folder}}/getInstanceImageDescription/" + image, true);
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
				}
				
			}
			xmlhttp.open("POST", "{{plweb_folder}}/searchInstances/" + str, true);
			xmlhttp.send();
			document.getElementById("info_link").href = "{{orthanc_url}}" + "/app/explorer.html#series?uuid=" + str;
		}

		function Calculate() {
			var image = $('#Images').val();
			// Get colormap
			var colormap = document.getElementById("set_colormap");
			var str_colormap = colormap.options[colormap.selectedIndex].value;

			document.getElementById("Calculate").disabled = true;
			document.getElementById("mySpinner").style.display = "block";
			enabledisable("PatientName", true);
			enabledisable("Study", true);
			enabledisable("Series", true);
			enabledisable("Images", true);
			document.getElementById("hidden_colormap").value = str_colormap;

			document.getElementById("hidden_converthu").value = document.getElementById("converthu").checked;
			document.getElementById("hidden_invert").value = document.getElementById("invert_image").checked;
			document.getElementById("hidden_histogram").value = document.getElementById("calculate_histogram").checked;
			document.getElementById("send_calc").action = "{{plweb_folder}}/image_review_calculate/" + image;
			document.getElementById("send_calc").submit();
			
		}

		function enableButton() {
			enabledisable("PatientName", false);
			enabledisable("Study", false);
			enabledisable("Series", false);
			enabledisable("Images", false);
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
				<div class="navbar-brand logo">Image review</div>
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
				<button type="submit" class="btn btn-default" id="Calculate" name="Calculate" onclick="Calculate();">Display</button>
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
						<div class="checkbox">
							<label>
								<input type="checkbox" id = "converthu"  name="converthu">
								Convert HU to pixel values?
							</label>
						</div>
						<div class="checkbox">
								<label>
									<input type="checkbox" id="invert_image" name="invert_image" value="False">
									Invert image?
								</label>
						</div>
						<div class="checkbox">
								<label>
									<input type="checkbox" id="calculate_histogram" name="calculate_histogram" value="False">
									Calculate histogram?
								</label>
						</div>

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
	<form target = "receiver2" id = "send_calc" method="post" autocomplete="off">
		<input type="hidden" name="hidden_converthu" id="hidden_converthu" value="" />
		<input type="hidden" name="hidden_invert" id="hidden_invert" value="" />
		<input type="hidden" name="hidden_colormap" id="hidden_colormap" value="" />
		<input type="hidden" name="hidden_histogram" id="hidden_histogram" value="" />
	</form>


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