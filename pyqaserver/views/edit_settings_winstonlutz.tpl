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
			    ajaxURL:"{{plweb_folder}}/get_treatmentunits_wl", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
		}

		function phantoms_table(){
			var table = new Tabulator("#table_phantom", {
				columns:[
					{title: "id", field: "id"},
			        {title:"Phantom", field:"Phantom"}
			    ],
			    layout:"fitColumns", //fit columns to width of table (optional)
			    ajaxURL:"{{plweb_folder}}/get_phantoms_wl", //ajax URL
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
			    ajaxURL:"{{plweb_folder}}/get_settings_wl", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("{{plweb_folder}}/get_user_data", {}, "post");

		}
		function tolerance_table(){

			var table3 = new Tabulator("#table3", {
				columns:[
			        {title:"Id", field:"Id"},
			        {title:"Machine", field:"Machine"},
			        {title:"PASS", field:"PASS_RATE"},
			        {title:"ACTION", field:"ACTION_RATE"},
			        {title:"APPLY_TOL_TO_COLL_ASYM", field:"APPLY_TOLERANCE_TO_COLL_ASYM"},
			        {title:"COLL_ASYM_TOL", field:"COLL_ASYM_TOL"},
			        {title:"BEAM_DEV_TOL", field:"BEAM_DEV_TOL"},
			        {title:"COUCH_DIST_TOL", field:"COUCH_DIST_TOL"}
			    ],
			    layout:"fitData", //fit columns to width of table (optional)
			    ajaxURL:"{{plweb_folder}}/get_tolerance_wl", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("{{plweb_folder}}/get_user_data", {}, "post");

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
				xmlhttp.open("POST", "{{plweb_folder}}/add_treatmentunit_wl", true);
				xmlhttp.send(formData);
		}

		function add_phantom(){
			var formData = new FormData();
			var Phantom = document.getElementById("Phantom").value;
			formData.append("Phantom", Phantom);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("phantom_add_error").innerHTML = temp;
						phantoms_table();
					}
				}
				xmlhttp.open("POST", "{{plweb_folder}}/add_phantom_wl", true);
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
				xmlhttp.open("POST", "{{plweb_folder}}/remove_treatmentunit_wl", true);
				xmlhttp.send(formData);
		}

		function update_settings_wl(){
			var formData = new FormData();
			var passrate = document.getElementById("passrate").value;
			var actionrate = document.getElementById("actionrate").value;
			var collasym = document.getElementById("collasym").checked;
			var collasym_tol_gen = document.getElementById("collasym_tol_gen").value;
			var beam_dev_tol_gen = document.getElementById("beam_dev_tol_gen").value;
			var couch_distance_gen = document.getElementById("couch_distance_gen").value;
			
			formData.append("passrate", passrate);
			formData.append("actionrate", actionrate);
			formData.append("collasym", collasym);
			formData.append("collasym_tol_gen", collasym_tol_gen);
			formData.append("beam_dev_tol_gen", beam_dev_tol_gen);
			formData.append("couch_distance_gen", couch_distance_gen);
			
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
				xmlhttp.open("POST", "{{plweb_folder}}/update_settings_wl", true);
				xmlhttp.send(formData);
		}
		
		function remove_phantom(){
			var formData = new FormData();
			var phantom_id = document.getElementById("remove_phantom_id").value;
			formData.append("phantom_id", phantom_id);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("phantom_remove_error").innerHTML = temp;
						phantoms_table();
					}
				}
				xmlhttp.open("POST", "{{plweb_folder}}/remove_phantom_wl", true);
				xmlhttp.send(formData);
		}

		function add_tolerance(){
			var formData = new FormData();
			var machine_tol = document.getElementById("machine_tol").value;
			var passrate_tol = document.getElementById("passrate_tol").value;
			var actionrate_tol = document.getElementById("actionrate_tol").value;
			var collasym_tol = document.getElementById("collasym_tol").checked;
			var collasym_tol_m = document.getElementById("collasym_tol_m").value;
			var beam_dev_tol_m = document.getElementById("beam_dev_tol_m").value;
			var couch_distance_m = document.getElementById("couch_distance_m").value;
			
			formData.append("machine_tol", machine_tol);
			formData.append("passrate_tol", passrate_tol);
			formData.append("actionrate_tol", actionrate_tol);
			formData.append("collasym_tol", collasym_tol);
			formData.append("collasym_tol_m", collasym_tol_m);
			formData.append("beam_dev_tol_m", beam_dev_tol_m);
			formData.append("couch_distance_m", couch_distance_m);
			
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
				xmlhttp.open("POST", "{{plweb_folder}}/add_tolerance_wl", true);
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
				xmlhttp.open("POST", "{{plweb_folder}}/remove_tolerance_wl", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Winston-Lutz machines</div>
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
		  <div class="panel-heading">Winston-Lutz phantoms</div>
		  	<div class="panel-body">
				<div class="row" >
					 <div class="col-xs-12 col-md-6" >
						<div id="table_phantom">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-6">
						<div class="form-group">
							<label class="control-label">Add phantom:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Phantom:</span>
								<input type="text" class="form-control" id="Phantom" autocomplete="off">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="add_phantom();">Add phantom</button>
							<strong><p class="text-danger"><small id="phantom_add_error"></small></p></strong>
						</div>

						<div class="form-group">
							<label class="control-label">Remove phantom:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Id:</span>
								<input type="text" class="form-control" id="remove_phantom_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="remove_phantom();">Remove phantom</button>
							<strong><p class="text-danger"><small id="phantom_remove_error"></small></p></strong>
						</div>

					</div>

				</div>
			</div>
		</div>

		<div class="panel panel-default">
		  <div class="panel-heading">Winston-Lutz generic tolerance</div>
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
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Pass tolerance:</span>
								<input type="text" class="form-control" id="passrate" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Action tolerance:</span>
								<input type="text" class="form-control" id="actionrate" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>

							<div class="checkbox">
									<label>
										<input type="checkbox" id="collasym" name="collasym" value="True">
										Apply to coll asymmetry?
									</label>
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Coll. asym. tol.:</span>
								<input type="text" class="form-control" id="collasym_tol_gen" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Beam dev. tol.:</span>
								<input type="text" class="form-control" id="beam_dev_tol_gen" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Couch dist. tol.:</span>
								<input type="text" class="form-control" id="couch_distance_gen" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
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
		  <div class="panel-heading">Winston-Lutz machine tolerance</div>
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
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Pass tolerance:</span>
								<input type="text" class="form-control" id="passrate_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Action tolerance:</span>
								<input type="text" class="form-control" id="actionrate_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="checkbox">
									<label>
										<input type="checkbox" id="collasym_tol" name="collasym_tol" value="True">
										Apply to coll asymmetry?
									</label>
								</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Coll. asym. tol.:</span>
								<input type="text" class="form-control" id="collasym_tol_m" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Beam dev. tol.:</span>
								<input type="text" class="form-control" id="beam_dev_tol_m" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Couch dist. tol.:</span>
								<input type="text" class="form-control" id="couch_distance_m" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<p></p>

							<button type="submit" class="btn btn-default" name="view_record_button" onclick="add_tolerance();">Add tolerance</button>
							<strong><p class="text-danger"><small id="tol_add_error"></small></p></strong>
						</div>
						<div class="form-group">
							<label class="control-label">Remove tolerance:</label>
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
			phantoms_table();
		});
	</script>

</body>


</html>