<!DOCTYPE html>
<html lang="en">

<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Administration</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
	<script src="/tabulator/js/tabulator.min.js"></script>
	<link href="/tabulator/css/tabulator.min.css" rel="stylesheet">
	<link href="/css/module_general.css" rel="stylesheet">
	
	<style> 
        .dropdown-menu li:hover {
    		cursor: pointer;
		}
    </style> 
	
	<script type="text/javascript">

		function changeDecimal() {
			this.value = this.value.replace(/,/, '.');
		}


		function treatmentunits_table(){
			var table = new Tabulator("#table", {
				columns:[
					{title: "id", field: "id"},
			        {title:"Machine", field:"Machine"},
			        {title:"Beam", field:"Beam"}
			    ],
			    layout:"fitColumns", //fit columns to width of table (optional)
			    ajaxURL:"/get_treatmentunits_fieldsize", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
		}

		function settings_table(){

			var table2 = new Tabulator("#table2", {
				columns:[
			        {title:"Setting", field:"Setting"},
			        {title:"Value", field:"Value"}
			    ],
			    layout:"fitData", //fit columns to width of table (optional)
			    ajaxURL:"/get_settings_fieldsize", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("/get_user_data", {}, "post");

		}
		function tolerance_table(){

			var table3 = new Tabulator("#table3", {
				columns:[
			        {title:"Id", field:"Id"},
			        {title:"Machine", field:"Machine"},
			        {title:"SMALL_NOMINAL", field:"SMALL_NOMINAL"},
			        {title:"MEDIUM_NOMINAL", field:"MEDIUM_NOMINAL"},
			        {title:"LARGE_NOMINAL", field:"LARGE_NOMINAL"},
			        {title:"SMALL_EXP_MLC", field:"SMALL_EXP_MLC"},
			        {title:"MEDIUM_EXP_MLC", field:"MEDIUM_EXP_MLC"},
			        {title:"LARGE_EXP_MLC", field:"LARGE_EXP_MLC"},
			        {title:"SMALL_EXP_JAW", field:"SMALL_EXP_JAW"},
			        {title:"MEDIUM_EXP_JAW", field:"MEDIUM_EXP_JAW"},
			        {title:"LARGE_EXP_JAW", field:"LARGE_EXP_JAW"},
			        {title:"TOLERANCE_SMALL_MLC", field:"TOLERANCE_SMALL_MLC"},
			        {title:"TOLERANCE_MEDIUM_MLC", field:"TOLERANCE_MEDIUM_MLC"},
			        {title:"TOLERANCE_LARGE_MLC", field:"TOLERANCE_LARGE_MLC"},
			        {title:"TOLERANCE_SMALL_JAW", field:"TOLERANCE_SMALL_JAW"},
			        {title:"TOLERANCE_MEDIUM_JAW", field:"TOLERANCE_MEDIUM_JAW"},
			        {title:"TOLERANCE_LARGE_JAW", field:"TOLERANCE_LARGE_JAW"},
			        {title:"TOLERANCE_ISO", field:"TOLERANCE_ISO"}
			    ],
			    layout:"fitData", //fit columns to width of table (optional)
			    ajaxURL:"/get_tolerance_fieldsize", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("/get_user_data", {}, "post");

		}

		function add_treatmentunit(){
			var formData = new FormData();
			var machine = document.getElementById("Machine").value;
			var beam = document.getElementById("Beam").value;
			formData.append("Machine", machine);
			formData.append("Beam", beam);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("unit_add_error").innerHTML = temp;
						treatmentunits_table();
					}
				}
				xmlhttp.open("POST", "/add_treatmentunit_fieldsize", true);
				xmlhttp.send(formData);
		}

		function remove_treatmentunit(){
			var formData = new FormData();
			var unit_id = document.getElementById("remove_unit_id").value;
			formData.append("unit_id", unit_id);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("unit_remove_error").innerHTML = temp;
						treatmentunits_table();
					}
				}
				xmlhttp.open("POST", "/remove_treatmentunit_fieldsize", true);
				xmlhttp.send(formData);
		}

		function update_settings_wl(){
			var formData = new FormData();
			var small_nominal = document.getElementById("small_nominal").value;
			var medium_nominal = document.getElementById("medium_nominal").value;
			var large_nominal = document.getElementById("large_nominal").value;
			var small_exp_mlc = document.getElementById("small_exp_mlc").value;
			var medium_exp_mlc = document.getElementById("medium_exp_mlc").value;
			var large_exp_mlc = document.getElementById("large_exp_mlc").value;
			var small_exp_jaw = document.getElementById("small_exp_jaw").value;
			var medium_exp_jaw = document.getElementById("medium_exp_jaw").value;
			var large_exp_jaw = document.getElementById("large_exp_jaw").value;
			var tolerance_small_mlc = document.getElementById("tolerance_small_mlc").value;
			var tolerance_medium_mlc = document.getElementById("tolerance_medium_mlc").value;
			var tolerance_large_mlc = document.getElementById("tolerance_large_mlc").value;
			var tolerance_small_jaw = document.getElementById("tolerance_small_jaw").value;
			var tolerance_medium_jaw = document.getElementById("tolerance_medium_jaw").value;
			var tolerance_large_jaw = document.getElementById("tolerance_large_jaw").value;
			var tolerance_iso = document.getElementById("tolerance_iso").value;
			
			formData.append("small_nominal", small_nominal);
			formData.append("medium_nominal", medium_nominal);
			formData.append("large_nominal", large_nominal);
			formData.append("small_exp_mlc", small_exp_mlc);
			formData.append("medium_exp_mlc", medium_exp_mlc);
			formData.append("large_exp_mlc", large_exp_mlc);
			formData.append("small_exp_jaw", small_exp_jaw);
			formData.append("medium_exp_jaw", medium_exp_jaw);
			formData.append("large_exp_jaw", large_exp_jaw);
			formData.append("tolerance_small_mlc", tolerance_small_mlc);
			formData.append("tolerance_medium_mlc", tolerance_medium_mlc);
			formData.append("tolerance_large_mlc", tolerance_large_mlc);
			formData.append("tolerance_small_jaw", tolerance_small_jaw);
			formData.append("tolerance_medium_jaw", tolerance_medium_jaw);
			formData.append("tolerance_large_jaw", tolerance_large_jaw);
			formData.append("tolerance_iso", tolerance_iso);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("unit_update_error").innerHTML = temp;
						settings_table();
					}
				}
				xmlhttp.open("POST", "/update_settings_fieldsize", true);
				xmlhttp.send(formData);
		}
		
		function add_tolerance(){
			var formData = new FormData();
			var machine_tol = document.getElementById("machine_tol").value;
			var small_nominal_tol = document.getElementById("small_nominal_tol").value;
			var medium_nominal_tol = document.getElementById("medium_nominal_tol").value;
			var large_nominal_tol = document.getElementById("large_nominal_tol").value;
			var small_exp_tol_mlc = document.getElementById("small_exp_tol_mlc").value;
			var medium_exp_tol_mlc = document.getElementById("medium_exp_tol_mlc").value;
			var large_exp_tol_mlc = document.getElementById("large_exp_tol_mlc").value;
			var small_exp_tol_jaw = document.getElementById("small_exp_tol_jaw").value;
			var medium_exp_tol_jaw = document.getElementById("medium_exp_tol_jaw").value;
			var large_exp_tol_jaw = document.getElementById("large_exp_tol_jaw").value;
			var tolerance_small_tol_mlc = document.getElementById("tolerance_small_tol_mlc").value;
			var tolerance_medium_tol_mlc = document.getElementById("tolerance_medium_tol_mlc").value;
			var tolerance_large_tol_mlc = document.getElementById("tolerance_large_tol_mlc").value;
			var tolerance_small_tol_jaw = document.getElementById("tolerance_small_tol_jaw").value;
			var tolerance_medium_tol_jaw = document.getElementById("tolerance_medium_tol_jaw").value;
			var tolerance_large_tol_jaw = document.getElementById("tolerance_large_tol_jaw").value;
			var tolerance_iso_tol = document.getElementById("tolerance_iso_tol").value;
			
			formData.append("machine_tol", machine_tol);
			formData.append("small_nominal_tol", small_nominal_tol);
			formData.append("medium_nominal_tol", medium_nominal_tol);
			formData.append("large_nominal_tol", large_nominal_tol);
			formData.append("small_exp_tol_mlc", small_exp_tol_mlc);
			formData.append("medium_exp_tol_mlc", medium_exp_tol_mlc);
			formData.append("large_exp_tol_mlc", large_exp_tol_mlc);
			formData.append("small_exp_tol_jaw", small_exp_tol_jaw);
			formData.append("medium_exp_tol_jaw", medium_exp_tol_jaw);
			formData.append("large_exp_tol_jaw", large_exp_tol_jaw);
			formData.append("tolerance_small_tol_mlc", tolerance_small_tol_mlc);
			formData.append("tolerance_medium_tol_mlc", tolerance_medium_tol_mlc);
			formData.append("tolerance_large_tol_mlc", tolerance_large_tol_mlc);
			formData.append("tolerance_small_tol_jaw", tolerance_small_tol_jaw);
			formData.append("tolerance_medium_tol_jaw", tolerance_medium_tol_jaw);
			formData.append("tolerance_large_tol_jaw", tolerance_large_tol_jaw);
			formData.append("tolerance_iso_tol", tolerance_iso_tol);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("tol_add_error").innerHTML = temp;
						tolerance_table();
					}
				}
				xmlhttp.open("POST", "/add_tolerance_fieldsize", true);
				xmlhttp.send(formData);
		}

		function remove_tolerance(){
			var formData = new FormData();
			var tol_id = document.getElementById("remove_tol_id").value;
			formData.append("tol_id", tol_id);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("tol_remove_error").innerHTML = temp;
						tolerance_table();
					}
				}
				xmlhttp.open("POST", "/remove_tolerance_fieldsize", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Field size machines</div>
		  	<div class="panel-body">
				<div class="row" >
					 <div class="col-xs-12 col-md-6" >
						<div id="table">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-6">
						<div class="form-group">
							<label class="control-label">Add unit:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Machine:</span>
								<input type="text" class="form-control" id="Machine" autocomplete="off">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Beam:</span>
								<input type="text" class="form-control" id="Beam" autocomplete="off">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="add_treatmentunit();">Add unit</button>
							<strong><p class="text-danger"><small id="unit_add_error"></small></p></strong>
						</div>

						<div class="form-group">
							<label class="control-label">Remove unit:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Id:</span>
								<input type="text" class="form-control" id="remove_unit_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="remove_treatmentunit();">Remove unit</button>
							<strong><p class="text-danger"><small id="unit_remove_error"></small></p></strong>
						</div>

					</div>

				</div>
			</div>
		</div>

		<div class="panel panel-default">
		  <div class="panel-heading">Field size generic tolerance</div>
		  	<div class="panel-body">
				<div class="row">
					 <div class="col-xs-12 col-md-6">
						<div id="table2">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-6">
						<div class="form-group">
							<label class="control-label">Change settings:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Small nominal:</span>
								<input type="text" class="form-control" id="small_nominal" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Medium nominal:</span>
								<input type="text" class="form-control" id="medium_nominal" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>

							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Large nominal:</span>
								<input type="text" class="form-control" id="large_nominal" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Small expected mlc:</span>
								<input type="text" class="form-control" id="small_exp_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Medium expected mlc:</span>
								<input type="text" class="form-control" id="medium_exp_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Large expected mlc:</span>
								<input type="text" class="form-control" id="large_exp_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Small expected jaw:</span>
								<input type="text" class="form-control" id="small_exp_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Medium expected jaw:</span>
								<input type="text" class="form-control" id="medium_exp_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Large expected jaw:</span>
								<input type="text" class="form-control" id="large_exp_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Small tolerance mlc:</span>
								<input type="text" class="form-control" id="tolerance_small_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Medium tolerance mlc:</span>
								<input type="text" class="form-control" id="tolerance_medium_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Large tolerance mlc:</span>
								<input type="text" class="form-control" id="tolerance_large_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Small tolerance jaw:</span>
								<input type="text" class="form-control" id="tolerance_small_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Medium tolerance jaw:</span>
								<input type="text" class="form-control" id="tolerance_medium_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Large tolerance jaw:</span>
								<input type="text" class="form-control" id="tolerance_large_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Tolerance isocenter:</span>
								<input type="text" class="form-control" id="tolerance_iso" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="update_settings_wl();">Update</button>
							<strong><p class="text-danger"><small id="unit_update_error"></small></p></strong>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div class="panel panel-default">
		  <div class="panel-heading">Field size machine tolerance</div>
		  	<div class="panel-body">
				<div class="row">
					 <div class="col-xs-12 col-md-8">
						<div id="table3">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-4">
						<div class="form-group">
							<label class="control-label">Settings:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Machine:</span>
								<input type="text" class="form-control" id="machine_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Small nominal:</span>
								<input type="text" class="form-control" id="small_nominal_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Medium nominal:</span>
								<input type="text" class="form-control" id="medium_nominal_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>

							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Large nominal:</span>
								<input type="text" class="form-control" id="large_nominal_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Small expected mlc:</span>
								<input type="text" class="form-control" id="small_exp_tol_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Medium expected mlc:</span>
								<input type="text" class="form-control" id="medium_exp_tol_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Large expected mlc:</span>
								<input type="text" class="form-control" id="large_exp_tol_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Small expected jaw:</span>
								<input type="text" class="form-control" id="small_exp_tol_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Medium expected jaw:</span>
								<input type="text" class="form-control" id="medium_exp_tol_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Large expected jaw:</span>
								<input type="text" class="form-control" id="large_exp_tol_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Small tolerance mlc:</span>
								<input type="text" class="form-control" id="tolerance_small_tol_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Medium tolerance mlc:</span>
								<input type="text" class="form-control" id="tolerance_medium_tol_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Large tolerance mlc:</span>
								<input type="text" class="form-control" id="tolerance_large_tol_mlc" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Small tolerance jaw:</span>
								<input type="text" class="form-control" id="tolerance_small_tol_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Medium tolerance jaw:</span>
								<input type="text" class="form-control" id="tolerance_medium_tol_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Large tolerance jaw:</span>
								<input type="text" class="form-control" id="tolerance_large_tol_jaw" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:60%">Tolerance isocenter:</span>
								<input type="text" class="form-control" id="tolerance_iso_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>

							<button type="submit" class="btn btn-default" name="view_record_button" onclick="add_tolerance();">Add tolerance</button>
							<strong><p class="text-danger"><small id="tol_add_error"></small></p></strong>
						</div>
						<div class="form-group">
							<label class="control-label">Remove row:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Id:</span>
								<input type="text" class="form-control" id="remove_tol_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="remove_tolerance();">Remove tolerance</button>
							<strong><p class="text-danger"><small id="tol_remove_error"></small></p></strong>
						</div>
					</div>
				</div>
			</div>
		</div>


	</div>
	
	<script>
		$(document).ready(function() {
			treatmentunits_table();
			settings_table();
			tolerance_table();
		});
	</script>

</body>


</html>