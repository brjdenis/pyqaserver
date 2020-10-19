<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Dynalog analysis</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<link href="/css/module_general.css" rel="stylesheet">
	<link rel="stylesheet" href="{{bokeh_file_css}}" type="text/css" />
	<script type="text/javascript" src="{{bokeh_file_js}}"></script>
	<link rel="stylesheet" href="{{bokeh_widgets_css}}" type="text/css" />
	<script type="text/javascript" src="{{bokeh_widgets_js}}"></script>
	<script type="text/javascript">Bokeh.set_log_level("info");</script>
	<script>
			function beamOnOff(snap){
				var beam_on = {{!beam_on}};
				var beam_hold = {{!beam_hold}};
		
				if (beam_hold[snap] == 0){
					document.getElementById("beam_on").innerHTML = "<span class='label label-success'>CONT</span>";
				}else{
					document.getElementById("beam_on").innerHTML = "<span class='label label-danger'>HOLD</span>";
				}
				if (beam_on[snap] == 0){
					document.getElementById("beam_on").innerHTML += "&nbsp; <span class='label label-danger'>OFF</span>";
				}else{
					document.getElementById("beam_on").innerHTML += "&nbsp; <span class='label label-success'>ON</span>";
				}
				var gantry = {{!gantry}};
    			document.getElementById("gantry").innerHTML = gantry[snap].toFixed(2);

				var collimator = {{!collimator}};
    			document.getElementById("collimator").innerHTML = collimator[snap].toFixed(2);

				var x1 = {{!x1}};
				var x2 = {{!x2}};
				document.getElementById("x12").innerHTML = String(x1[snap].toFixed(2))+", "+ String(x2[snap].toFixed(2));

				var y1 = {{!y1}};
				var y2 = {{!y2}};
				document.getElementById("y12").innerHTML = String(y1[snap].toFixed(2))+", "+ String(y2[snap].toFixed(2));

				var MU = {{!MU}};
    			document.getElementById("MU").innerHTML = MU[snap].toFixed(4);

				var DR = {{!DR}};
				document.getElementById("progressBar").max = Math.max.apply(null, DR);
    			document.getElementById("progressBar").value = DR[snap];

				document.getElementById("time").innerHTML = (snap*0.05).toFixed(2);
			}
		</script>
	{{!script1}}
	{{!script3}}
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
				<div class="navbar-brand logo">Dynalog analysis: {{record}}, {{patient_name}}</div>
			</div>
			<div class="navbar-collapse collapse">
				<ul class="nav navbar-nav navbar-right">
					<li class="active"><a href="/docs/build/html/index.html" target="_blank">Help</a></li>
				</ul>
			</div>
		</div>
    </div>

	<div class="threepart-container container">
		<div class="row">
			<div class="col-xs-12 col-md-3">
				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Current status</h3>
					</div>
					<div class="panel-body" id="settings_panel">
						<table class="table">
							<tr>
								<td class="col-md-6">Property</td>
								<td class="col-md-6">Value</td>
							</tr>
							<tr>
								<td class="col-md-6">Beam Status</td>
								<td class="col-md-6"><div id = "beam_on"></div></td>
							</tr>
							<tr>
								<td class="col-md-6">Time [s]</td>
								<td class="col-md-6"><div id = "time"></div></td>
							</tr>
							<tr>
								<td class="col-md-6">Gantry</td>
								<td class="col-md-6"><div id = "gantry"></div></td>
							</tr>
							<tr>
								<td class="col-md-6">Collimator</td>
								<td class="col-md-6"><div id = "collimator"></div></td>
							</tr>
							<tr>
								<td class="col-md-6">X1, X2</td>
								<td class="col-md-6"><div id = "x12"></div></td>
							</tr>
							<tr>
								<td class="col-md-6">Y1, Y2</td>
								<td class="col-md-6"><div id = "y12"></div></td>
							</tr>
							<tr>
								<td class="col-md-6">Meterset</td>
								<td class="col-md-6"><div id = "MU"></div></td>
							</tr>
							<tr>
								<td class="col-md-6">Rel. DR</td>
								<td class="col-md-6">
									<progress id="progressBar" value="0" max="1" style="width:90%;"></progress>
								</td>
							</tr>
						</table>
					</div>
				</div>

				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Properties</h3>
					</div>
					<div class="panel-body" id="settings_panel">
						<table class="table table-condensed table-hover">

							<tr>
								<td>Property</td>
								<td>Value</td>
							</tr>
							<tr>
								<td>Beam ID</td>
								<td>{{beam_id}}</td>
							</tr>
							<tr>
								<td>Number of snapshots</td>
								<td>{{num_snapshots}}</td>
							</tr>
							<tr>
								<td>Number of holdoffs</td>
								<td>{{num_beamholds}}</td>
							</tr>
							<tr>
								<td>Tolerance</td>
								<td>{{tolerance}}</td>
							</tr>
						</table>
					</div>
				</div>
				<div class="panel panel-default">
					<div class="panel-heading">
						<h3 class="panel-title">Calculations</h3>
					</div>
					<div class="panel-body" id="settings_panel">
						<label class="control-label" for="table_general">General:</label>
						<table class="table table-condensed table-hover" id="table_general">
							<tr>
								<td>Property</td>
								<td>Value</td>
							</tr>
							<tr>
								<td>Gamma average</td>
								<td>{{gamma_avg}}</td>
							</tr>
							<tr>
								<td>Gamma pass percentage</td>
								<td>{{gamma_prcnt}}</td>
							</tr>
							<tr>
								<td>DD/DTA/threshold/resolution</td>
								<td>{{gamma_tol_str}}</td>
							</tr>
						</table>

						<label class="control-label" for="table_on">When beam is ON:</label>
						<table class="table table-condensed table-hover" id="table_on">
							<tr>
								<td>Max RMS A [mm]</td>
								<td>{{rmsA_max_on}}</td>
							</tr>
							<tr>
								<td>Max RMS B [mm]</td>
								<td>{{rmsB_max_on}}</td>
							</tr>
							
							<tr>
								<td>Max DIFF A [mm]</td>
								<td>{{diffA_max_on}}</td>
							</tr>
							<tr>
								<td>Max DIFF B [mm]</td>
								<td>{{diffB_max_on}}</td>
							</tr>
						</table>
						<label class="control-label" for="table_on">Beam ON and no holdoffs:</label>
						<table class="table table-condensed table-hover" id="table_on">
						<tr>
								<td>Max RMS2 A [mm]</td>
								<td>{{rmsA_max_hold}}</td>
							</tr>
							<tr>
								<td>Max RMS2 B [mm]</td>
								<td>{{rmsB_max_hold}}</td>
							</tr>
							<tr>
								<td>Max DIFF2 A [mm]</td>
								<td>{{diffA_max_hold}}</td>
							</tr>
							<tr>
								<td>Max DIFF2 B [mm]</td>
								<td>{{diffB_max_hold}}</td>
							</tr>
							<tr>
								<td>Avg RMS2 A [mm]</td>
								<td>{{rmsA_hold_avg}}</td>
							</tr>
							<tr>
								<td>Avg RMS2 B [mm]</td>
								<td>{{rmsB_hold_avg}}</td>
							</tr>
						</table>
					</div>
				</div>
			</div>
            <div class="col-xs-12 col-md-9">
				<ul class="nav nav-tabs nav-justified">
					<li class="active">
						<a data-toggle="pill" href="#menu1">MLC</a>
					</li>
					<li>
						<a data-toggle="pill" href="#menu2">Fluence</a>
					</li>
					<li>
						<a data-toggle="pill" href="#menu21">Error histogram</a>
					</li>
					<li>
						<a data-toggle="pill" href="#menu3">Dose rate</a>
					</li>
					<li>
						<a data-toggle="pill" href="#menu4">Carriage</a>
					</li>
				</ul>

				<div class="tab-content">
					<div id="menu1" class="tab-pane fade in active">
						{{!div1}}
					</div>
					<div id="menu2" class="tab-pane fade">
						{{!script2}}
						{{!div3}}
					</div>
					<div id="menu21" class="tab-pane fade">
						{{!script_MLC_rms}}
						<br>
						<p>
							<button class="btn btn-default" type="button" data-toggle="collapse" data-target="#collapseExample" aria-expanded="false" aria-controls="collapseExample">
								Show details
							</button>
							<div class="collapse" id="collapseExample">
								<div class="well">
									<table class="table-condensed table-hover">
										<tr>
											<td>Leaf #</td><td>RMS A [mm]</td> <td>RMS B [mm]</td><td>RMS2 A [mm]</td> <td>RMS2 B [mm]</td>
										</tr>
										% for k in range(0, len(rmsA_on), 1):
											% if rmsA_on[k] != 0 or rmsB_on[k] != 0:
												<tr>
													<td>{{k+1}}</td><td>{{rmsA_on[k]}}</td> <td>{{rmsB_on[k]}}</td><td>{{rmsA_hold[k]}}</td> <td>{{rmsB_hold[k]}}</td>
												</tr>
											% end
										% end
										<tr>
											<td>avg</td><td>{{rmsA_on_avg}}</td> <td>{{rmsB_on_avg}}</td><td>{{rmsA_hold_avg}}</td> <td>{{rmsB_hold_avg}}</td>
										</tr>
										<tr>
											<td>max</td><td>{{rmsA_max_on}}</td> <td>{{rmsB_max_on}}</td><td>{{rmsA_max_hold}}</td> <td>{{rmsB_max_hold}}</td>
										</tr>
									</table>
								</div>
							</div>
						</p>

					</div>
					<div id="menu3" class="tab-pane fade">
						{{!script_dose_rate}}
					</div>
					<div id="menu4" class="tab-pane fade">
						{{!script_carriage}}
					</div>
				</div>

				
			</div>
		</div>
	</div>

</body>



</html>