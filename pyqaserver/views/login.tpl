<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<link href="/css/signin.css" rel="stylesheet">

	<title>Sign in to pyQAserver</title>

	<script>
		function check_credentials(){
			var formData = new FormData();
			var username = document.getElementById("username").value;
			var password = document.getElementById("password").value;
			formData.append("username", username);
			formData.append("password", password);
			document.getElementById("error_message").innerHTML = "";
			if (window.XMLHttpRequest) {
	                    // code for IE7+, Firefox, Chrome, Opera, Safari
	                    xmlhttp = new XMLHttpRequest();
	                } else {  // code for IE6, IE5
	                    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	                }
            xmlhttp.onreadystatechange = function () {
                if (this.readyState == 4 && this.status == 200) {
                    temp = this.responseText;
                    console.log(temp);
                    if (temp != "Success!"){
                    	document.getElementById("error_message").innerHTML = temp;
                    }else{
                    	document.getElementById("form-id").submit();
                    }
                }
            }
            xmlhttp.open("POST", "{{plweb_folder}}/login_check_credentials", true);
            xmlhttp.send(formData);
	    }

	</script>
</head>

<body class="text-center">
	<div class="container">
		<div class="row">
			<div class="col-sm">
				<form class="form-signin" id="form-id" action="{{plweb_folder}}/login" method="POST" autocomplete="off">
					<img class="img" src="/{{image}}" id="logo_image">
					<h1 class="h3 mb-3 font-weight-normal">Sign in to pyQAserver</h1>
					<label>Username</label>
					<input type="text" id="username" name="username" class="form-control" required>
					<label>Password</label>
					<input type="password" id="password" name="password" class="form-control" required>
				</form>
				<button class="btn btn-primary" type="submit" onclick="check_credentials();">Sign in</button>
				<strong><p class="text-danger"><small id="error_message"> </small></p></strong>
			</div>
		</div>
	</div>

	<script>
		$(document).ready(function() {
	        if (!navigator.cookieEnabled) {
				alert("Cookies must be enabled.");
			}
	    });
	</script>
</body>

</html>