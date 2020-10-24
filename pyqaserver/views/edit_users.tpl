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
		function user_table(){
			var table = new Tabulator("#table", {
				columns:[
					{title: "id", field: "id"},
			        {title:"Name", field:"Name"},
			        {title:"Displayname", field:"Displayname"},
			        {title:"Is admin?", field:"Admin"}
			    ],
			    layout:"fitColumns", //fit columns to width of table (optional)
			    ajaxURL:"/get_user_data", //ajax URL
			    ajaxParams:{}, //ajax parameters
			    ajaxConfig:"post", //ajax HTTP request type
			});
			//table.setData("/get_user_data", {}, "post");

		}

		function add_user(){
			var formData = new FormData();
			var username = document.getElementById("username").value;
			var password = document.getElementById("password").value;
			var displayname = document.getElementById("displayname").value;
			var is_admin =  document.getElementById("is_admin").checked;
			formData.append("username", username);
			formData.append("password", password);
			formData.append("is_admin", is_admin);
			formData.append("displayname", displayname);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("user_add_error").innerHTML = temp;
						user_table();
					}
				}
				xmlhttp.open("POST", "/add_user", true);
				xmlhttp.send(formData);
		}

		function remove_user(){
			var formData = new FormData();
			var user_id = document.getElementById("remove_user_id").value;
			formData.append("user_id", user_id);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = this.responseText;
						document.getElementById("user_remove_error").innerHTML = temp;
						user_table();
					}
				}
				xmlhttp.open("POST", "/remove_user", true);
				xmlhttp.send(formData);
		}
	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Edit users</div>
		  	<div class="panel-body">
				<div class="row">
					 <div class="col-xs-12 col-md-6">
						<div id="table">
							
						</div>
					</div>
					<div class="col-xs-12 col-md-6">
						<div class="form-group">
							<label class="control-label">Add user:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:40%" >Username:</span>
								<input type="text" class="form-control" id="username" autocomplete="off">
							</div>
						
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon"  style="width:40%">Password:</span>
								<input type="password" class="form-control" id="password" autocomplete="off">
							</div>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:40%" >Display name:</span>
								<input type="text" class="form-control" id="displayname" autocomplete="off">
							</div>
							<div class="checkbox">
								<label>
									<input type="checkbox" id="is_admin" name="is_admin" value="False">
									Admin privileges?
								</label>
							</div>
							<button type="submit" class="btn btn-default" id="add_user_btn" name="view_record_button" onclick="add_user();">Add user</button>
							<strong><p class="text-danger"><small id="user_add_error"></small></p></strong>
						</div>

						<div class="form-group">
							<label class="control-label">Remove user:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:40%">Id:</span>
								<input type="text" class="form-control" id="remove_user_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" id="remove_user_btn" name="view_record_button" onclick="remove_user();">Remove user</button>
							<strong><p class="text-danger"><small id="user_remove_error"></small></p></strong>
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