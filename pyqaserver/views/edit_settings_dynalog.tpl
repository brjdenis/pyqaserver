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
	<link href="/css/module_general.css" rel="stylesheet">
	
	<style> 
        .dropdown-menu li:hover {
    		cursor: pointer;
		}
    </style> 
	
	<script type="text/javascript">
		
		function start_analysis(){
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
						document.getElementById("update_error").innerHTML = temp;
					}
				}
				xmlhttp.open("POST", "/dynalog_start_batch_analysis", true);
				xmlhttp.send();
		}

		function check_status(){
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
				xmlhttp.onreadystatechange = function () {
					if (this.readyState == 4 && this.status == 200) {
						temp = JSON.parse(this.responseText);
						$('#in_progress').text(temp["in_progress"]);
						$('#current_folder').text(temp["current_folder"]);
						$('#current_file').text(temp["current_file"]+ " %");
						$('#progress_bar').css("width", temp["current_file"] + "%");
					}
				}
				xmlhttp.open("POST", "/get_dynalog_analysis_status", true);
				xmlhttp.send();
		}


	
	</script>

</head>


<body>
	<div class="container">
		<div class="panel panel-default">
		  <div class="panel-heading">Start batch analysis</div>
		  	<div class="panel-body">
				<div class="col-xs-12 col-md-12">
					<div class="alert alert-warning" role="alert">Warning: Once started, the analysis cannot be stopped.</div>
					<div class="form-group">
						<ul class="list-group">
							<li class="list-group-item">
								<span class="badge" id="in_progress">Click Check status</span>
						    	Is analysis already in progress?
						  	</li>
						  	<li class="list-group-item">
								<span class="badge" id="current_folder">Click Check status</span>
						    	Current folder
						  	</li>
						  	<li class="list-group-item">
								<span class="badge" id="current_file">Click Check status</span>
						    	Progress (click Check Status to update)
						    	<p></p>
						    	<div class="progress">
								  <div class="progress-bar" id="progress_bar" role="progressbar" aria-valuenow="1" aria-valuemin="0" aria-valuemax="100">
								  </div>
								</div>
						  	</li>
						</ul>

						<button type="submit" class="btn btn-default" name="view_record_button" onclick="check_status();">Check Status</button>

						<button type="submit" class="btn btn-default" name="view_record_button" onclick="start_analysis();">Start Analysis</button>
						
						<strong><p class="text-danger"><small id="update_error"></small></p></strong>
					</div>
				</div>
			</div>
		</div>

	</div>

	<script>
		$(document).ready(function() {
            //check_status();
        });
	</script>
</body>


</html>