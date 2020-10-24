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
			    ajaxURL:"/get_treatmentunits_fieldrotation", //ajax URL
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
			    ajaxURL:"/get_settings_fieldrotation", //ajax URL
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
			        {title:"TOLERANCE_COLLABS", field:"TOLERANCE_COLLABS"},
			        {title:"TOLERANCE_COLLREL", field:"TOLERANCE_COLLREL"},
			        {title:"TOLERANCE_COUCHREL", field:"TOLERANCE_COUCHREL"}
			    ],
			    layout:"fitData", //fit columns to width of table (optional)
			    ajaxURL:"/get_tolerance_fieldrotation", //ajax URL
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
				xmlhttp.open("POST", "/add_treatmentunit_fieldrotation", true);
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
				xmlhttp.open("POST", "/remove_treatmentunit_fieldrotation", true);
				xmlhttp.send(formData);
		}

		function update_settings(){
			var formData = new FormData();
			var tolerance_collabs = document.getElementById("tolerance_collabs").value;
			var tolerance_collrel = document.getElementById("tolerance_collrel").value;
			var tolerance_couchrel = document.getElementById("tolerance_couchrel").value;
			formData.append("tolerance_collabs", tolerance_collabs);
			formData.append("tolerance_collrel", tolerance_collrel);
			formData.append("tolerance_couchrel", tolerance_couchrel);
			
			
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
				xmlhttp.open("POST", "/update_settings_fieldrotation", true);
				xmlhttp.send(formData);
		}
		
		function add_tolerance(){
			var formData = new FormData();
			var machine_tol = document.getElementById("machine_tol").value;
			var tolerance_collabs_tol = document.getElementById("tolerance_collabs_tol").value;
			var tolerance_collrel_tol = document.getElementById("tolerance_collrel_tol").value;
			var tolerance_couchrel_tol = document.getElementById("tolerance_couchrel_tol").value;
			
			formData.append("tolerance_collabs_tol", tolerance_collabs_tol);
			formData.append("tolerance_collrel_tol", tolerance_collrel_tol);
			formData.append("tolerance_couchrel_tol", tolerance_couchrel_tol);
			formData.append("machine_tol", machine_tol);

			
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
				xmlhttp.open("POST", "/add_tolerance_fieldrotation", true);
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
				xmlhttp.open("POST", "/remove_tolerance_fieldrotation", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Field rotation machines</div>
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
		  <div class="panel-heading">Field rotation generic tolerance</div>
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
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Tolerance coll. abs.:</span>
								<input type="text" class="form-control" id="tolerance_collabs" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Tolerance coll. rel.:</span>
								<input type="text" class="form-control" id="tolerance_collrel" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Tolerance couch. rel.:</span>
								<input type="text" class="form-control" id="tolerance_couchrel" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>

							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="update_settings();">Update</button>
							<strong><p class="text-danger"><small id="unit_update_error"></small></p></strong>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div class="panel panel-default">
		  <div class="panel-heading">Field rotation machine tolerance</div>
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
								<span class="input-group-addon" id="sizing-addon" style="width:60%" >Machine:</span>
								<input type="text" class="form-control" id="machine_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:60%" >Tolerance coll. abs.:</span>
								<input type="text" class="form-control" id="tolerance_collabs_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:60%" >Tolerance coll. rel.:</span>
								<input type="text" class="form-control" id="tolerance_collrel_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:60%" >Tolerance couch. rel.:</span>
								<input type="text" class="form-control" id="tolerance_couchrel_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
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
		});
	</script>

</body>


</html>