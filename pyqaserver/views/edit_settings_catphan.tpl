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
			        {title:"HU", field:"HU"},
			        {title:"LCV", field:"LCV"},
			        {title:"SCALING", field:"SCALING"},
			        {title:"THICKNESS", field:"THICKNESS"},
			        {title:"LOWCONTRAST", field:"LOWCONTRAST"},
			        {title:"CNR", field:"CNR"},
			        {title:"MTF", field:"MTF"},
			        {title:"UNIFORMITYIDX", field:"UNIFORMITYIDX"},
			        {title:"GENERATE_PDF_REPORT", field:"GENERATE_PDF_REPORT"}
			    ],
			    layout:"fitData", //fit columns to width of table (optional)
			    ajaxURL:"{{plweb_folder}}/get_tolerance_catphan", //ajax URL
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
			    ajaxURL:"{{plweb_folder}}/get_referenceimages_catphan", //ajax URL
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
			var hu_tol = document.getElementById("hu_tol").value;
			var lcv_tol = document.getElementById("lcv_tol").value;
			var scaling_tol = document.getElementById("scaling_tol").value;
			var thickness_tol = document.getElementById("thickness_tol").value;
			var lowcontrast_tol = document.getElementById("lowcontrast_tol").value;
			var cnr_tol = document.getElementById("cnr_tol").value;
			var mtf_tol = document.getElementById("mtf_tol").value;
			var uniformityidx_tol = document.getElementById("uniformityidx_tol").value;
			var generate_pdf_tol = document.getElementById("generate_pdf_tol").checked;
			
			formData.append("machine_tol", machine_tol);
			formData.append("beam_tol", beam_tol);
			formData.append("phantom_tol", phantom_tol);
			formData.append("hu_tol", hu_tol);
			formData.append("lcv_tol", lcv_tol);
			formData.append("scaling_tol", scaling_tol);
			formData.append("thickness_tol", thickness_tol);
			formData.append("lowcontrast_tol", lowcontrast_tol);
			formData.append("cnr_tol", cnr_tol);
			formData.append("mtf_tol", mtf_tol);
			formData.append("uniformityidx_tol", uniformityidx_tol);
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
				xmlhttp.open("POST", "{{plweb_folder}}/add_tolerance_catphan", true);
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
				xmlhttp.open("POST", "{{plweb_folder}}/remove_tolerance_catphan", true);
				xmlhttp.send(formData);
		}

		function add_referenceimage(){
			var formData = new FormData();
			var machine = document.getElementById("machine_ref").value;
			var beam = document.getElementById("beam_ref").value;
			var phantom = $("#phantom_ref").val();
			var series = document.getElementById("Orthanc_series_ref").value;
			formData.append("Machine", machine);
			formData.append("Beam", beam);
			formData.append("Phantom", phantom);
			formData.append("Series", series);
			
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
				xmlhttp.open("POST", "{{plweb_folder}}/add_referenceimage_catphan", true);
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
				xmlhttp.open("POST", "{{plweb_folder}}/remove_referenceimage_catphan", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Catphan machines and tolerances</div>
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
							<p></p>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">HU tolerance:</span>
								<input type="text" class="form-control" id="hu_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">LCV tolerance:</span>
								<input type="text" class="form-control" id="lcv_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Scaling tolerance:</span>
								<input type="text" class="form-control" id="scaling_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Thickness tol.:</span>
								<input type="text" class="form-control" id="thickness_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Low contrast tol.:</span>
								<input type="text" class="form-control" id="lowcontrast_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">CNR threshold:</span>
								<input type="text" class="form-control" id="cnr_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">MTF tolerance:</span>
								<input type="text" class="form-control" id="mtf_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Uniformity tol.:</span>
								<input type="text" class="form-control" id="uniformityidx_tol" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="checkbox">
								<label>
									<input type="checkbox" id="generate_pdf_tol" name="generate_pdf_tol" value="True">
									Generate PDF?
								</label>
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

		<div class="panel panel-default">
		  <div class="panel-heading">Catphan reference scans</div>
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
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Orthanc series:</span>
								<input type="text" class="form-control" id="Orthanc_series_ref" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							
							<p></p>

							<button type="submit" class="btn btn-default" name="view_record_button" onclick="add_referenceimage();">Save  reference scan</button>
							<strong><p class="text-danger"><small id="ref_add_error"></small></p></strong>
						</div>
						<div class="form-group">
							<label class="control-label">Remove reference scan:</label>
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