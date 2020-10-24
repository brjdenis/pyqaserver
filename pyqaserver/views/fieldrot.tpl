<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Field rotation module</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
	<link href="/css/module_general.css" rel="stylesheet">

	<script type="application/javascript">
		function resizeIFrameToFitContent(iFrame) {
			if (iFrame.contentWindow.document.body.scrollHeight >= 800) {
				iFrame.height = iFrame.contentWindow.document.body.scrollHeight + 100 + "px";
			}
			if (iFrame.contentWindow.document.body.scrollHeight < 800) {
				iFrame.height = 800 + "px";
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

			var image1 = $('#image1');
			var image2 = $('#image2');
			enabledisable("image1", true);
			enabledisable("image2", true);

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
					changeOptions("image2", opt_images, temp["4"]);
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
					enabledisable("image2", false);
					document.getElementById("hidden_datetime").value = temp["3"][0]; // get date time from first row
					document.getElementById("hidden_station").value = temp["5"]; // to send back to server
				}
				
			}
			xmlhttp.open("POST", "/searchInstances/" + str, true);
			xmlhttp.send();
			document.getElementById("info_link").href = "{{orthanc_url}}" + "/app/explorer.html#series?uuid=" + str;
		}

		function Calculate() {
			var image1 = $('#image1').val();
			var image2 = $('#image2').val();

	        var optt_selecttype= document.getElementById("set_type");
	        var selecttype = optt_selecttype.options[optt_selecttype.selectedIndex].value;
	        
	        var optt_direction = document.getElementById("set_orientation");
	        var direction = optt_direction.options[optt_direction.selectedIndex].value;

	        var optt_direction2 = document.getElementById("set_orientation2");
	        var direction2 = optt_direction2.options[optt_direction2.selectedIndex].value;

	        // Get colormap
			var colormap = document.getElementById("set_colormap");
			var str_colormap = colormap.options[colormap.selectedIndex].value;

			document.getElementById("Calculate").disabled = true;
			document.getElementById("mySpinner").style.display = "block";
			enabledisable("PatientName", true);
			enabledisable("Study", true);
			enabledisable("Series", true);
			enabledisable("image1", true);
			enabledisable("image2", true);

			document.getElementById("hidden_type").value = selecttype;
			document.getElementById("hidden_direction").value = direction;
			document.getElementById("hidden_direction2").value = direction2;
			document.getElementById("hidden_points").value = document.getElementById("sample_points").value;
			document.getElementById("hidden_filter").value = document.getElementById("filter").value;
			document.getElementById("hidden_colormap").value = str_colormap;
			
			document.getElementById("hidden_margin").value = document.getElementById("margin").value;

			document.getElementById("hidden_invert").value = document.getElementById("invert_image").checked;
			document.getElementById("hidden_clipbox").value = document.getElementById("clipbox").value;
			document.getElementById("hidden_high_contrast").value = document.getElementById("high_contrast").checked;

			document.getElementById("send_calc").action = "/fieldrot/"+image1+"/"+image2;
			document.getElementById("send_calc").submit();
		
		}

		function enableButton() {
			enabledisable("PatientName", false);
			enabledisable("Study", false);
			enabledisable("Series", false);
			enabledisable("image1", false);
			enabledisable("image2", false);
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
				<div class="navbar-brand logo">Field rotation module</div>
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
					<select class="selectpicker form-control" data-live-search="true" data-size="15" id="PatientName">
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
						<h3 class="panel-title">Select images</h3>
					</div>
					<div class="panel-body">
						<div class="form-group">
							<p>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon2">Image 1:</span>
									<select class="selectpicker form-control" name="image1" id="image1" onchange="getImage();">
										<option value=""></option>
									</select>
								</div>
							</p>
							<p>
								<div class="input-group">
									<span class="input-group-addon" id="sizing-addon2">Image 2:</span>
									<select class="form-control" name="image2" id="image2">
										<option value=""></option>
									</select>
								</div>
							</p>
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
									<label class="control-label" for="set_type">Image type:</label>
									<div class="input-group">
										<span class="input-group-addon" id="sizing-addon">Type:</span>
										<select class="form-control" name="set_type" id="set_type">
											<option value="Collimator absolute">Collimator absolute</option>
											<option value="Collimator relative">Collimator relative</option>
											<option value="Couch relative">Couch relative</option>
										</select>
									</div>
								</div>
							
							<p>
								<div class="form-group">
									<label class="control-label" for="set_orientation">Sampling direction:</label>
									<div class="input-group">
										<span class="input-group-addon" id="sizing-addon">Image 1:</span>
										<select class="form-control" name="set_orientation" id="set_orientation">
											<option value="X">Left-right (x)</option>
											<option value="Y">Up-down (y)</option>
										</select>
									</div>
									<div class="input-group">
										<span class="input-group-addon" id="sizing-addon">Image 2:</span>
										<select class="form-control" name="set_orientation2" id="set_orientation2">
											<option value="X">Left-right (x)</option>
											<option value="Y">Up-down (y)</option>
										</select>
									</div>
								</div>
							</p>

							<label class="control-label" for="select_mlc">Analysis settings:</label>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Clipbox: </span>
								<input id="clipbox" class="form-control" type="text" onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">cm</span>
							</div>

							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Sampling lines: </span>
								<input id="sample_points" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="20" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%"></span>
							</div>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Margin: </span>
								<input id="margin" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="50" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">px</span>
							</div>
							<div class="input-group input-group-sm">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Median filter: </span>
								<input id="filter" class="form-control" type="text"  onkeyup="this.value=this.value.replace(/,/,'.')" value="0" />
								<span class="input-group-addon" id="sizing-addon" style="width:20%">pts</span>
							</div>
						</div>

						<div class="checkbox">
							<label>
								<input type="checkbox" id="invert_image" name="invert_image" value="False">
								Invert image?
							</label>
						</div>
						<div class="checkbox">
							<label>
								<input type="checkbox" id="high_contrast" name="high_contrast" value="False">
								High contrast (kV) images?
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
		<input type="hidden" name="hidden_type" id="hidden_type" value="" />
		<input type="hidden" name="hidden_direction" id="hidden_direction" value="" />
		<input type="hidden" name="hidden_direction2" id="hidden_direction2" value="" />
		<input type="hidden" name="hidden_points" id="hidden_points" value="" />
		<input type="hidden" name="hidden_margin" id="hidden_margin" value="" />
		<input type="hidden" name="hidden_invert" id="hidden_invert" value="" />
		<input type="hidden" name="hidden_clipbox" id="hidden_clipbox" value="" />
		<input type="hidden" name="hidden_colormap" id="hidden_colormap" value="" />
		<input type="hidden" name="hidden_filter" id="hidden_filter" value="" />
		<input type="hidden" name="hidden_imgdescription" id="hidden_imgdescription" value="" />
		<input type="hidden" name="hidden_displayname" id="hidden_displayname" value="{{displayname}}" />
		<input type="hidden" name="hidden_datetime" id="hidden_datetime" value="" />
		<input type="hidden" name="hidden_station" id="hidden_station" value="" />
		<input type="hidden" name="hidden_high_contrast" id="hidden_high_contrast" value="" />
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
			$('#image1').on('change', function(){
				getImage();
				getImageDescription();
			});
		});
	</script>
</body>


</html>