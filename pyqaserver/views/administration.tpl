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
		function resizeIFrameToFitContent(iFrame) {
			if (iFrame.contentWindow.document.body.scrollHeight >= 2000) {
				iFrame.height = iFrame.contentWindow.document.body.scrollHeight + 20 + "px";
			}
			if (iFrame.contentWindow.document.body.scrollHeight < 3000) {
				iFrame.height = 3000 + "px";
			}
		}

		function edit_users(){
			document.getElementById("send_calc").action = "/edit_users";
			document.getElementById("send_calc").submit();
		}
		function edit_orthanc(){
			document.getElementById("send_calc").action = "/edit_orthanc";
			document.getElementById("send_calc").submit();
		}
		function edit_institution(){
			document.getElementById("send_calc").action = "/edit_institution";
			document.getElementById("send_calc").submit();
		}
		function edit_settings_winstonlutz(){
			document.getElementById("send_calc").action = "/edit_settings_winstonlutz";
			document.getElementById("send_calc").submit();
		}
		function edit_settings_starshot(){
			document.getElementById("send_calc").action = "/edit_settings_starshot";
			document.getElementById("send_calc").submit();
		}
		function machine_mapping(){
			document.getElementById("send_calc").action = "/edit_machine_mapping";
			document.getElementById("send_calc").submit();
		}
		function edit_picketfence(){
			document.getElementById("send_calc").action = "/edit_settings_picketfence";
			document.getElementById("send_calc").submit();
		}
		function edit_planarimaging(){
			document.getElementById("send_calc").action = "/edit_settings_planarimaging";
			document.getElementById("send_calc").submit();
		}
		function edit_catphan(){
			document.getElementById("send_calc").action = "/edit_settings_catphan";
			document.getElementById("send_calc").submit();
		}
		function edit_flatsym(){
			document.getElementById("send_calc").action = "/edit_settings_flatsym";
			document.getElementById("send_calc").submit();
		}
		function edit_vmat(){
			document.getElementById("send_calc").action = "/edit_settings_vmat";
			document.getElementById("send_calc").submit();
		}
		function edit_fieldsize(){
			document.getElementById("send_calc").action = "/edit_settings_fieldsize";
			document.getElementById("send_calc").submit();
		}
		function edit_fieldrotation(){
			document.getElementById("send_calc").action = "/edit_settings_fieldrotation";
			document.getElementById("send_calc").submit();
		}
		function edit_settings_dynalog(){
			document.getElementById("send_calc").action = "/edit_settings_dynalog";
			document.getElementById("send_calc").submit();
		}

	
	
	</script>

</head>


<body>
	<div class="navbar navbar-inverse navbar-fixed-top">
		<div class="container">
			<div class="navbar-header">
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>
				<div class="navbar-brand logo">Administration</div>
			</div>

			<ul class="nav navbar-nav">
		        <li class="dropdown" >
		          <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="true" id="dropdownMenu1">General <span class="caret"></span></a>
		          <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">
		            <li><a role="menuitem" tabindex="-1" onclick="edit_users();">Edit user list</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_orthanc();">Edit orthanc connection</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_institution();">Edit institution name</a></li>
		            <!--<li role="separator" class="divider"></li>-->
		          </ul>
		        </li>
		      </ul>

		      <ul class="nav navbar-nav">
		        <li class="dropdown" >
		          <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="true" id="dropdownMenu1">Module settings <span class="caret"></span></a>
		          <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">
		          	<li><a role="menuitem" tabindex="-1" onclick="machine_mapping();">Machine mapping</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_settings_winstonlutz();">Winston Lutz settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_settings_starshot();">Starshot settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_picketfence();">Picket Fence settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_vmat();">Vmat settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_fieldsize();">Field size settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_fieldrotation();">Field rotation settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_flatsym();">Flatness/Symmetry settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_planarimaging();">Planar imaging settings</a></li>
		            <li><a role="menuitem" tabindex="-1" onclick="edit_catphan();">Catphan settings</a></li>
		            
		            
		            <!--<li role="separator" class="divider"></li>-->
		          </ul>
		        </li>
		      </ul>
		      <ul class="nav navbar-nav">
		        <li class="dropdown" >
		          <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="true" id="dropdownMenu1">Dynalog analysis <span class="caret"></span></a>
		          <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">
		            <li><a role="menuitem" tabindex="-1" onclick="edit_settings_dynalog();">Check/start analysis</a></li>
		          </ul>
		        </li>
		      </ul>

			<div class="navbar-collapse collapse">
				<ul class="nav navbar-nav navbar-right">
					<p class="navbar-text">Signed in as: <strong>{{displayname}}</strong></p>
					<li class="active"><a href="/docs/build/html/index.html" target="_blank">Help</a></li>
				</ul>
			</div>
		</div>
	</div>
	<div class="container">
		<div class="row">
			<iframe name="receiver2" height="100%" width="100%" id="receiver2" onload="resizeIFrameToFitContent(this);"></iframe>
		</div>
	</div>

	
	<form target = "receiver2" id = "send_calc" method="post" autocomplete="off">

	</form>

</body>


</html>