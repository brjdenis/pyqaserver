<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
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
		function user_table(){
			var table = new Tabulator("#table", {
				columns:[
					{title: "id", field: "id"},
			        {title:"Dicom name", field:"DicomName"},
			        {title:"Dicom energy", field:"DicomEnergy"},
			        {title:"User name", field:"UserName"},
			        {title:"User energy", field:"UserEnergy"}
			    ],
			    layout:"fitColumns", //fit columns to width of table (optional)
			    ajaxURL:"/get_mapping", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("/get_user_data", {}, "post");

		}

		function add_mapping(){
			var formData = new FormData();
			var DicomName = document.getElementById("DicomName").value;
			var DicomEnergy = document.getElementById("DicomEnergy").value;
			var UserName = document.getElementById("UserName").value;
			var UserEnergy = document.getElementById("UserEnergy").value;
			formData.append("DicomName", DicomName);
			formData.append("DicomEnergy", DicomEnergy);
			formData.append("UserName", UserName);
			formData.append("UserEnergy", UserEnergy);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("mapping_add_error").innerHTML = temp;
						user_table();
					}
				}
				xmlhttp.open("POST", "/add_mapping", true);
				xmlhttp.send(formData);
		}

		function remove_mapping(){
			var formData = new FormData();
			var mapping_id = document.getElementById("remove_mapping_id").value;
			formData.append("mapping_id", mapping_id);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("mapping_remove_error").innerHTML = temp;
						user_table();
					}
				}
				xmlhttp.open("POST", "/remove_mapping", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Mapping dicom machines</div>
		  	<div class="panel-body">
				<div class="row">
					 <div class="col-xs-12 col-md-8">
						<div id="table">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-4">
						<div class="form-group">
							<label class="control-label">Add match:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Dicom name:</span>
								<input type="text" class="form-control" id="DicomName" autocomplete="off">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >Dicom energy:</span>
								<input type="text" class="form-control" id="DicomEnergy" autocomplete="off">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">User name:</span>
								<input type="text" class="form-control" id="UserName" autocomplete="off">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">User energy:</span>
								<input type="text" class="form-control" id="UserEnergy" autocomplete="off">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" id="add_user_btn" name="view_record_button" onclick="add_mapping();">Add mapping</button>
							<strong><p class="text-danger"><small id="mapping_add_error"></small></p></strong>
						</div>

						<div class="form-group">
							<label class="control-label">Remove match:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%">Id:</span>
								<input type="text" class="form-control" id="remove_mapping_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" id="remove_mapping_btn" name="view_record_button" onclick="remove_mapping();">Remove mapping</button>
							<strong><p class="text-danger"><small id="mapping_remove_error"></small></p></strong>
						</div>

					</div>
				</div>
			</div>
		</div>

	</div>
	
	<script>
		$(document).ready(function() {
			user_table();
		});
	</script>

</body>


</html>