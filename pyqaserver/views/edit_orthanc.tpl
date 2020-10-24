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
		
		function orthanc_table(){
			var table = new Tabulator("#table", {
				columns:[
					{title: "Setting", field: "Setting"},
			        {title:"Value", field:"Value"}
			    ],
			    layout:"fitColumns", //fit columns to width of table (optional)
			    ajaxURL:"/get_orthanc_settings", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
		}

		function update_orthanc_settings(){
			var formData = new FormData();
			var ip_address = document.getElementById("IP").value;
			var port = document.getElementById("Port").value;
			var user = document.getElementById("User").value;
			var password = document.getElementById("Password").value;
			
			formData.append("IP", ip_address);
			formData.append("Port", port);
			formData.append("User", user);
			formData.append("Password", password);
			
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
						orthanc_table();
					}
				}
				xmlhttp.open("POST", "/update_orthanc_settings", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Edit orthanc connection</div>
		  	<div class="panel-body">
				<div class="col-xs-12 col-md-6">
						<div id="table">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-6">
						<div class="form-group">
							<label class="control-label">Change settings:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:50%" >IP address:</span>
								<input type="text" class="form-control" id="IP" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Port:</span>
								<input type="text" class="form-control" id="Port" autocomplete="off"  onkeyup="this.value=this.value.replace(/,/,'.')">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">User:</span>
								<input type="text" class="form-control" id="User" autocomplete="off">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:50%">Password:</span>
								<input type="text" class="form-control" id="Password" autocomplete="off">
							</div>

							<p></p>
							<button type="submit" class="btn btn-default" name="view_record_button" onclick="update_orthanc_settings();">Update</button>
							
							<strong><p class="text-danger"><small id="unit_update_error"></small></p></strong>
						</div>
					</div>
			</div>
		</div>

	</div>
	
	<script>
		$(document).ready(function() {
			orthanc_table();
		});
	</script>

</body>


</html>