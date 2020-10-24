<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/popper.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<link href="/css/menu.css" rel="stylesheet">

	<script type="text/javascript">


		function winston_lutz() {
			document.getElementById("form").action = "/winston_lutz";
			document.getElementById("form").submit();
		}
		function picket_fence() {
			document.getElementById("form").action = "/picket_fence";
			document.getElementById("form").submit();
		}
		function starshot() {
			document.getElementById("form").action = "/starshot";
			document.getElementById("form").submit();
		}
		function image_review() {
			document.getElementById("form").action = "/image_review";
			document.getElementById("form").submit();
		}
		function planar_imaging() {
			document.getElementById("form").action = "/planar_imaging";
			document.getElementById("form").submit();
		}
		function dynalog() {
			document.getElementById("form").action = "/dynalog";
			document.getElementById("form").submit();
		}
		function catphan() {
			document.getElementById("form").action = "/catphan";
			document.getElementById("form").submit();
		}
		function flatsym() {
			document.getElementById("form").action = "/flatsym";
			document.getElementById("form").submit();
		}
		function vvmat() {
			document.getElementById("form").action = "/vvmat";
			document.getElementById("form").submit();
		}
		function fieldsize() {
			document.getElementById("form").action = "/fieldsize";
			document.getElementById("form").submit();
		}
		function fieldrot() {
			document.getElementById("form").action = "/fieldrot";
			document.getElementById("form").submit();
		}
		function administration() {
			document.getElementById("form").action = "/administration";
			document.getElementById("form").submit();
		}
		function trends() {
			document.getElementById("form").action = "/review_trends";
			document.getElementById("form").submit();
		}
	</script>
	<title>pyQAserver Menu</title>
</head>

<body>
	
	<div class="container">

      <!-- Static navbar -->
      <nav class="navbar navbar-inverse">
        <div class="container-fluid">
          <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
              <span class="sr-only">Toggle navigation</span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="https://github.com/brjdenis/pyqaserver" target="_blank">pyQAserver</a>
          </div>
          <div id="navbar" class="navbar-collapse collapse">
            <ul class="nav navbar-nav">
              <li><a href="/docs/build/html/about.html" target="_blank">About</a></li>
              <li class="dropdown">
                <ul class="nav navbar-nav">
		        <li class="dropdown" >
		          <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="true" id="dropdownMenu1">Modules <span class="caret"></span></a>
		          <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">
		          	<li role="presentation"><a role="menuitem" tabindex="-1" onclick="winston_lutz();">Winston-Lutz module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="starshot();">Starshot module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="picket_fence();">Picket fence module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="vvmat();">VMAT module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="fieldsize();">Field size module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="fieldrot();">Field rotation module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="flatsym();">Flatness/symmetry module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="planar_imaging();">Planar imaging module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="catphan();">Catphan module</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="dynalog();">Dynalog module</a></li>
					
		          </ul>
		        </li>
		      </ul>
              </li>
              <li class="dropdown">
                <ul class="nav navbar-nav">
                <li role='button'><a role="menuitem" tabindex="-1" onclick="trends();">Trends</a></li>
		        <li class="dropdown" >
		          <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="true" id="dropdownMenu1">Tools <span class="caret"></span></a>
		          <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="window.open('{{orthanc_url}}');">Orthanc server</a></li>
					<li role="presentation"><a role="menuitem" tabindex="-1" onclick="image_review();">Image Review</a></li>
		          </ul>
		        </li>
		      </ul>
              </li>
			% if is_admin:
	              <li class="dropdown">
	                <ul class="nav navbar-nav">
			        <li class="dropdown" >
			          <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="true" id="dropdownMenu1">Administration <span class="caret"></span></a>
			          <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">
							<li role="presentation"><a role="menuitem" tabindex="-1" onclick="administration();">Administration</a></li>
			            <!--<li role="separator" class="divider"></li>-->
			          </ul>
			        </li>
			      </ul>
	              </li>
			% end



            </ul>
            <div class="navbar-collapse collapse">
				<ul class="nav navbar-nav navbar-right">
					<p class="navbar-text">Signed in as: <strong>{{displayname}}</strong></p>
					<li class="active"><a href="/login">Logout</a></li>
				</ul>
			</div>
          </div><!--/.nav-collapse -->
        </div><!--/.container-fluid -->
      </nav>

      <!-- Main component for a primary marketing message or call to action -->
   
			<div class="panel panel-default">
			  <div class="panel-body">
			    <h3>Getting started</h3>
			        <p>Read the documentation to get started with pyQAserver.</p>
			        <p>
			          <a class="btn btn-lg btn-danger" href="/docs/build/html/index.html" role="button" target="_blank">Read the docs &raquo;</a>
			        </p>
			  </div>
			</div>
			<div class="panel panel-default">
			  <div class="panel-body">
			    <h3>Pylinac</h3>
			        <p>Read the documentation.</p>
			        <p>
			          <a class="btn btn-lg btn-danger" href="https://pylinac.readthedocs.io/en/v2.3.2/" role="button" target="_blank">Pylinac &raquo;</a>
			        </p>
			  </div>
			</div>

    </div> <!-- /container -->

	<form id="form" method="post" target="_blank">
		<input type="hidden" name="hidden_displayname" id="hidden_displayname" value="{{displayname}}" />
	</form>

	<footer class="page-footer font-small blue pt-4">
		<div class="footer-copyright text-center py-3">
			<p>
				Version {{qaserver_version}}
			</p>
			Powered by <a target="_blank" href="https://pylinac.readthedocs.io/en/stable/">Pylinac</a>, 
			<a target="_blank" href="https://bottlepy.org/docs/dev/">Bottle</a> and <a target="_blank" href="https://www.orthanc-server.com/">Orthanc</a>.
		</div>
	</footer>

</body>


</html>