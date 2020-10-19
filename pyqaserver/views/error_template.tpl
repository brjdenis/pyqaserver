<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<title>Error</title>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <script src="/bootstrap/js/jquery.min.js"></script>
    <script src="/bootstrap/js/bootstrap.min.js"></script>
	<style>
		body {
			background-color: #f5f5f5;
		}
	</style>
</head>

<body>
	<div class="alert alert-danger" role="alert">
		An error has occured. This message was sent from the server:
		<br><br>
		<b>{{error_message}}</b>
	</div>
</body>

</html>