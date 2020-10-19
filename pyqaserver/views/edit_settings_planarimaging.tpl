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
	

		function tolerance_table(){

			var table3 = new Tabulator("#table3", {
				columns:[
			        {title:"Id", field:"Id"},
			        {title:"Machine", field:"Machine"},
			        {title:"Beam", field:"Beam"},
			        {title:"Phantom", field:"Phantom"},
			        {title:"LOW_THRESHOLD", field:"LOW_THRESHOLD"},
			        {title:"HIGH_THRESHOLD", field:"HIGH_THRESHOLD"},
			        {title:"GENERATE_PDF_REPORT", field:"GENERATE_PDF_REPORT"}
			    ],
			    layout:"fitData", //fit columns to width of table (optional)
			    ajaxURL:"{{plweb_folder}}/get_tolerance_planarimaging", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("{{plweb_folder}}/get_user_data", {}, "post");

		}

		function referenceimages_table(){

			var table4 = new Tabulator("#table4", {
				columns:[
			        {title:"Id", field:"Id"},
			        {title:"Machine", field:"Machine"},
			        {title:"Beam", field:"Beam"},
			        {title:"Phantom", field:"Phantom"},
			        {title:"Path", field:"Path"}
			    ],
			    layout:"fitData", //fit columns to width of table (optional)
			    ajaxURL:"{{plweb_folder}}/get_referenceimages_planarimaging", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("{{plweb_folder}}/get_user_data", {}, "post");

		}

		function add_tolerance(){
			var formData = new FormData();
			
			var machine_tol = document.getElementById("machine_tol").value;
			var beam_tol = document.getElementById("beam_tol").value;
			var phantom_tol = $('#phantom_tol').val();
			var low_threshold_tol = document.getElementById("low_threshold_tol").value;
			var high_threshold_tol = document.getElementById("high_threshold_tol").value;
			var generate_pdf_tol = document.getElementById("generate_pdf_tol").checked;
			
			formData.append("machine_tol", machine_tol);
			formData.append("beam_tol", beam_tol);
			formData.append("phantom_tol", phantom_tol);
			formData.append("low_threshold_tol", low_threshold_tol);
			formData.append("high_threshold_tol", high_threshold_tol);
			formData.append("generate_pdf_tol", generate_pdf_tol);
			
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
				xmlhttp.open("POST", "{{plweb_folder}}/add_tolerance_planarimaging", true);
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
				xmlhttp.open("POST", "{{plweb_folder}}/remove_tolerance_planarimaging", true);
				xmlhttp.send(formData);
		}

		function add_referenceimage(){
			var formData = new FormData();
			var machine = document.getElementById("machine_ref").value;
			var beam = document.getElementById("beam_ref").value;
			var phantom = $("#phantom_ref").val();
			var instance = document.getElementById("Orthanc_instance_ref").value;
			formData.append("Machine", machine);
			formData.append("Beam", beam);
			formData.append("Phantom", phantom);
			formData.append("Instance", instance);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("ref_add_error").innerHTML = temp;
						referenceimages_table();
					}
				}
				xmlhttp.open("POST", "{{plweb_folder}}/add_referenceimage_planarimaging", true);
				xmlhttp.send(formData);
				document.getElementById("ref_add_error").innerHTML = "Working on it ... ";
		}
		function remove_referenceimage(){
			var formData = new FormData();
			var ref_id = document.getElementById("remove_ref_id").value;
			formData.append("ref_id", ref_id);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("ref_remove_error").innerHTML = temp;
						referenceimages_table();
					}
				}
				xmlhttp.open("POST", "{{plweb_folder}}/remove_referenceimage_planarimaging", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Planar imaging machines and tolerances</div>
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
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Beam:</span>
								<input type="text" class="form-control" id="beam_tol" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:25%">Phantom:</span>
								<select class="selectpicker form-control" data-selected-text-format="values" name="phantom_tol" id="phantom_tol" >
									% for k in phantoms:
										<option value="{{k}}">{{k}}</option>
									% end
								</select>
							</div>
							
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">High threshold:</span>
								<input type="text" class="form-control" id="high_threshold_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Low threshold.:</span>
								<input type="text" class="form-control" id="low_threshold_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="checkbox">
									<label>
										<input type="checkbox" id="generate_pdf_tol" name="generate_pdf_tol" value="True">
										Generate PDF?
									</label>
							</div>
							<p></p>

							<button type="submit" class="btn btn-default" name="view_record_button" onclick="add_tolerance();">Add threshold</button>
							<strong><p class="text-danger"><small id="tol_add_error"></small></p></strong>
						</div>
						<div class="form-group">
							<label class="control-label">Remove threshold:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Id:</span>
								<input type="text" class="form-control" id="remove_tol_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="remove_tolerance();">Remove threshold</button>
							<strong><p class="text-danger"><small id="tol_remove_error"></small></p></strong>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="panel panel-default">
		  <div class="panel-heading">Planar imaging reference images</div>
		  	<div class="panel-body">
				<div class="row">
					 <div class="col-xs-12 col-md-8">
						<div id="table4">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-4">
						<div class="form-group">
							<label class="control-label">Settings:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Machine:</span>
								<input type="text" class="form-control" id="machine_ref" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Beam:</span>
								<input type="text" class="form-control" id="beam_ref" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:25%">Phantom:</span>
								<select class="selectpicker form-control" data-selected-text-format="values" name="phantom_ref" id="phantom_ref" >
									% for k in phantoms:
										<option value="{{k}}">{{k}}</option>
									% end
								</select>
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Orthanc instance:</span>
								<input type="text" class="form-control" id="Orthanc_instance_ref" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							
							<p></p>

							<button type="submit" class="btn btn-default" name="view_record_button" onclick="add_referenceimage();">Save  reference image</button>
							<strong><p class="text-danger"><small id="ref_add_error"></small></p></strong>
						</div>
						<div class="form-group">
							<label class="control-label">Remove reference image:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Id:</span>
								<input type="text" class="form-control" id="remove_ref_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="remove_referenceimage();">Remove</button>
							<strong><p class="text-danger"><small id="ref_remove_error"></small></p></strong>
						</div>
					</div>
				</div>
			</div>
		</div>

	</div>
	
	<script>
		$(document).ready(function() {
			tolerance_table();
			referenceimages_table();
		});
	</script>

</body>


</html>