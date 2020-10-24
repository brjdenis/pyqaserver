<!DOCTYPE html>
<html lang="en">

<head>
	<link rel="icon" type="image/png" href="/images/favicon-32x32.png"/>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Trends</title>

	<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<script src="/bootstrap/js/jquery.min.js"></script>
	<script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="/bootstrap/js/bootstrap-datepicker.min.js"></script>
	<script src="/bootstrap/js/bootstrap-select.min.js"></script>
	<link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
	<script src="/tabulator/js/tabulator.min.js"></script>
	<script src="/js/plotly-latest.min.js"></script>
	<link href="/bootstrap/css/bootstrap-datepicker.css" rel="stylesheet">
	<link href="/tabulator/css/tabulator.min.css" rel="stylesheet">
	<link href="/css/module_general.css" rel="stylesheet">
	<script type="text/javascript" src="/js/xlsx.full.min.js"></script>
	<script src="/js/jspdf.min.js"></script>
	<script src="/js/jspdf.plugin.autotable.js"></script>
	
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
			if (iFrame.contentWindow.document.body.scrollHeight < 2000) {
				iFrame.height = 2000 + "px";
			}
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

				<div class="navbar-brand logo">Trends</div>
			</div>

			<div class="navbar-collapse collapse">
				<ul class="nav navbar-nav navbar-right">
					<p class="navbar-text">Signed in as: <strong>{{displayname}}</strong></p>
					<li class="active"><a href="/docs/build/html/index.html" target="_blank">Help</a></li>
				</ul>
			</div>
		</div>
	</div>
	<div class="container">
		<div class="well">
			<div class="row">
				<div class="col-xs-12 col-md-4 ">
					<div class="input-group">
	                     <span class="input-group-addon" id="sizing-addon2" style="min-width:100px;">Module:</span>
	                     <select class="selectpicker show-tick form-control" name="Module" id="Module">
							<option value=""></option>
						</select>
	                 </div>
				</div>
				<div class="col-xs-12 col-md-4">
					<div class="input-group">
	                     <span class="input-group-addon" id="sizing-addon2" style="min-width:100px;">Test type:</span>
	                     <select class="selectpicker show-tick form-control"  name="TestType" id="TestType">
							<option value=""></option>
						</select>
	                 </div>
				</div>
				<div class="col-xs-12 col-md-4">
					<div class="input-group">
	                     <span class="input-group-addon" id="sizing-addon2" style="min-width:100px;">Parameters:</span>
	                     <select class="selectpicker show-tick form-control" multiple data-size="15" data-selected-text-format="values" name="Parameter" id="Parameter">
							<option value=""></option>
						</select>
	                 </div>
				</div>
			</div>
			<p></p>
			<div class="row">
				<div class="col-xs-12 col-md-4">
					<div class="input-group">
						 <span class="input-group-addon" id="sizing-addon2" style="min-width:100px;">Machine:</span>
	                     <select class="selectpicker show-tick form-control" name="Machine" id="Machine">
							<option value=""></option>
						</select>
	                 </div>
				</div>
				<div class="col-xs-12 col-md-4">
					<div class="input-group">
	                     <span class="input-group-addon" id="sizing-addon2" style="min-width:100px;">Beam:</span>
	                     <select class="selectpicker show-tick form-control"  name="Beam" id="Beam">
							<option value=""></option>
						</select>
	                 </div>
				</div>
				<div class="col-xs-12 col-md-4">
					<div class="input-group">
	                     <span class="input-group-addon" id="sizing-addon2-phantom" style="min-width:100px;">Phantom:</span>
	                     <select class="selectpicker show-tick form-control" name="Phantom" id="Phantom">
							<option value=""></option>
						</select>
	                 </div>
				</div>
			</div>
			<p></p>
			<div class="row">
				<div class="col-xs-12 col-md-4">
					<div class="input-group">
	                     <span class="input-group-addon" id="sizing-addon2" style="min-width:100px;">Start date:</span>
	                     <input class="form-control" id="date1" name="date1" placeholder="DD/MM/YYYY" data-date-format="dd-mm-yyyy" type="text"> 
	                </div>
				</div>
				<div class="col-xs-12 col-md-4">
					<div class="input-group">
	                     <span class="input-group-addon" id="sizing-addon2" style="min-width:100px;">End date:</span>
	                     <input class="form-control" id="date2" name="date2" placeholder="DD/MM/YYYY" data-date-format="dd-mm-yyyy" type="text">  
	                </div>
				</div>
			</div>
			<br>
			<div class="row">
				<div class="col-xs-12 col-md-2">
					<div class="text-bottom">
	                	<button type="submit" class="btn btn-primary btn-block" id="get_data" name="get_data" onclick="fetch_data();">Fetch and show</button> 
	            	</div>
				</div>
				<div class="col-xs-12 col-md-2">
					<div class="text-bottom">
	                	<form method = "post" target="_self" id="download_csv_form">
							<input type="hidden" name="hidden_module" id="hidden_module" value="" />
							<input type="hidden" name="hidden_testtype" id="hidden_testtype" value="" />
							<input type="hidden" name="hidden_parameters" id="hidden_parameters" value="" />
							<input type="hidden" name="hidden_machine" id="hidden_machine" value="" />
							<input type="hidden" name="hidden_beam" id="hidden_beam" value="" />
							<input type="hidden" name="hidden_phantom" id="hidden_phantom" value="" />
							<input type="hidden" name="hidden_date1" id="hidden_date1" value="" />
							<input type="hidden" name="hidden_date2" id="hidden_date2" value="" />
							<button type="submit" class="btn btn-primary btn-block" name = "download_csv_button" id = "download_csv_button" onclick="download_csv_full();">Download CSV</button>
            			</form>
	            	</div>
				</div>
			</div>
		</div>
	</div>
	<div class="container">
		<div class="row">
	  		<div class="col-xs-12 col-md-12">
			    <div id="diagram" style="width:100%;height:500px;"></div>
			</div>
		</div>
		<br>
		<br>
		<div class="row">
	    	<div class="col-xs-12 col-md-12" >
	    		<div class="text-right">
				    <button class="btn btn-primary btn-sm" id="download-csv">Download CSV</button>
				    <button class="btn btn-primary btn-sm" id="download-json">Download JSON</button>
				    <button class="btn btn-primary btn-sm" id="download-xlsx">Download XLSX</button>
				    <button class="btn btn-primary btn-sm" id="download-pdf">Download PDF</button>
				    <button class="btn btn-primary btn-sm" id="download-html">Download HTML</button>
				</div>
				<div id="table_data" style="margin-top:5px">
				</div>
			</div>
		</div>
		% if is_admin:
			<br>
			<div class="row">
				<div class="panel panel-default">
				  <div class="panel-heading">Remove one measurement</div>
				  	<div class="panel-body">
						<div class="form-group">
							<label class="control-label">Remove row:</label>
							<div class="input-group">
								<span class="input-group-addon" id="sizing-addon" style="width:40%">Id:</span>
								<input type="text" class="form-control" id="remove_row_id">
							</div>
							<p></p>
							<button type="submit" class="btn btn-default" id="remove_row_btn" name="view_record_button" onclick="remove_measurement();">Remove measurement</button>
							<strong><p class="text-danger"><small id="user_remove_error"></small></p></strong>
						</div>
					</div>
				</div>
			</div>
		% end
	</div>

	<script>

		var tables = {{!tables}};
		var unique_names = {{!unique_names}};

		// Declare table
		const table = new Tabulator("#table_data", {
			layout:"fitColumns",
			columns: [],
			placeholder:"No Data Available", //display message to user on empty table
			pagination:"local",
		    paginationSize: 20,
		    paginationSizeSelector: [20, 50, 100, 1000],
		    clipboard:true
			});

		// Prepare functions for data download taken from tabular documentation!
		//trigger download of data.csv file
		document.getElementById("download-csv").addEventListener("click", function(){
		    table.download("csv", "data.csv");
		});

		//trigger download of data.json file
		document.getElementById("download-json").addEventListener("click", function(){
		    table.download("json", "data.json");
		});

		//trigger download of data.xlsx file
		document.getElementById("download-xlsx").addEventListener("click", function(){
		    table.download("xlsx", "data.xlsx", {sheetName:"My Data"});
		});

		//trigger download of data.pdf file
		document.getElementById("download-pdf").addEventListener("click", function(){
		    table.download("pdf", "data.pdf", {
		        orientation:"landscape", //set page orientation to portrait
		        title:"Trends", //add title to report
		    });
		});

		//trigger download of data.html file
		document.getElementById("download-html").addEventListener("click", function(){
		    table.download("html", "data.html", {style:true});
		});

		function populate_modules(){
            var modules = Object.keys(tables);
            var html = [];
            html.push("<option " + "value='" + modules[0] + "' selected>" + modules[0] + "");
            for (j = 1; j < modules.length; j++) {
                    html.push("<option " + "value='" + modules[j] + "'>" + modules[j] + "");
                }
            change_testtype(modules[0]);
            $('#Module').html(html);
            $('#Module').selectpicker('refresh');
        }

        function change_testtype(selected_module){
            var html = [];
            var available_testtypes = Object.keys(tables[selected_module]);
            html.push("<option " + "value='" + available_testtypes[0] + "' selected>" + available_testtypes[0] + "");
            for (j = 1; j < available_testtypes.length; j++) {
                 html.push("<option " + "value='" + available_testtypes[j] + "'>" + available_testtypes[j] + "");
                }
            change_parameters(selected_module, available_testtypes[0]);
            $('#TestType').html(html);
            $('#TestType').selectpicker('refresh');
        }

        function change_parameters(selected_module, selected_testtype){
            var html = [];
            var available_parameters = tables[selected_module][selected_testtype];

            html.push("<option " + "value='" + available_parameters[0] + "' selected>" + available_parameters[0] + "");
            for (j = 1; j < available_parameters.length; j++) {
                 html.push("<option " + "value='" + available_parameters[j] + "'>" + available_parameters[j] + "");
                }
            $('#Parameter').html(html);
            $('#Parameter').selectpicker('refresh');
        }

        function populate_machines(){
            var machines = unique_names[$("#Module").val()][0];
            if (machines.length!=0){
            	var html = [];
	            html.push("<option " + "value='" + machines[0] + "' selected>" + machines[0] + "");
	            for (j = 1; j < machines.length; j++) {
	                    html.push("<option " + "value='" + machines[j] + "'>" + machines[j] + "");
	                }
	            change_beam(machines[0]);
	            change_phantom(machines[0]);
	            $('#Machine').html(html);
	            $('#Machine').selectpicker('refresh');
            }
        }

        function change_machine(selected_module){
            var html = [];
            var available_machines = unique_names[$("#Module").val()][0];
            if (available_machines.length != 0){
            	html.push("<option " + "value='" + available_machines[0] + "' selected>" + available_machines[0] + "");
	            for (j = 1; j < available_machines.length; j++) {
	                 html.push("<option " + "value='" + available_machines[j] + "'>" + available_machines[j] + "");
	                }
	            $('#Machine').html(html);
	            $('#Machine').selectpicker('refresh');
	            change_beam($('#Machine').val());
	            change_phantom($('#Machine').val());
            }
            else{
            	$('#Machine').html("");
	            $('#Machine').selectpicker('refresh');
	            $('#Beam').html("");
	            $('#Beam').selectpicker('refresh');
	            $('#Phantom').html("");
	            $('#Phantom').selectpicker('refresh');
            }
            
        }

        function change_beam(selected_machine){
            var html = [];
            var available_beams = unique_names[$("#Module").val()][1][selected_machine];
            html.push("<option " + "value='" + available_beams[0] + "' selected>" + available_beams[0] + "");
            for (j = 1; j < available_beams.length; j++) {
                 html.push("<option " + "value='" + available_beams[j] + "'>" + available_beams[j] + "");
                }
            $('#Beam').html(html);
            $('#Beam').selectpicker('refresh');
        }

        function change_phantom(selected_machine){
            var html = [];
            var available_phantoms = unique_names[$("#Module").val()][2][selected_machine];
            html.push("<option " + "value='" + available_phantoms[0] + "' selected>" + available_phantoms[0] + "");
            for (j = 1; j < available_phantoms.length; j++) {
                 html.push("<option " + "value='" + available_phantoms[j] + "'>" + available_phantoms[j] + "");
                }
            $('#Phantom').html(html);
            $('#Phantom').selectpicker('refresh');
        }

        function fetch_data(){
			var formData = new FormData();
			var Module = $("#Module").val();
			var TestType = $("#TestType").val();
			var Parameters_array = $("#Parameter").val();
			var Parameters = JSON.stringify(Parameters_array);
			var Machine = $("#Machine").val();
			var Beam = $("#Beam").val();
			var Phantom = $("#Phantom").val();
			var Date1 = $('#date1').datepicker('getFormattedDate');
			var Date2 = $('#date2').datepicker('getFormattedDate');

			if (Parameters_array.length==0){
				alert("Pick at least one parameter.");
				return;
			}
			
			if (Date.parse(Date2) - Date.parse(Date1) < 0 ){
				alert("Start date must be before End date!");
				return;
			}

			formData.append("Module", Module);
			formData.append("TestType", TestType);

			formData.append("Parameters", Parameters);
			formData.append("Machine", Machine);

			formData.append("Beam", Beam);
			formData.append("Phantom", Phantom);

			formData.append("Date1", Date1);
			formData.append("Date2", Date2);
			
			if (window.XMLHttpRequest) {
					// code for IE7+, Firefox, Chrome, Opera, Safari
					xmlhttp = new XMLHttpRequest();
				} else {  // code for IE6, IE5
					xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
				}
			xmlhttp.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					temp = JSON.parse(this.responseText);
					plot_and_show(temp);
					create_table(temp);
					if (temp.length==0){
						alert("No data exists!");
					}

				}
			}
			xmlhttp.open("POST", "/fetch_trends", true);
			xmlhttp.send(formData);
		}

		function download_csv_full(){
			document.getElementById("hidden_module").value = $("#Module").val();
			document.getElementById("hidden_testtype").value = $("#TestType").val();
			document.getElementById("hidden_parameters").value = JSON.stringify($("#Parameter").val());
			document.getElementById("hidden_machine").value = $("#Machine").val();
			document.getElementById("hidden_beam").value = $("#Beam").val();
			document.getElementById("hidden_phantom").value = $("#Phantom").val();
			document.getElementById("hidden_date1").value = $('#date1').datepicker('getFormattedDate');
			document.getElementById("hidden_date2").value = $('#date2').datepicker('getFormattedDate');
			
			if (Date.parse($('#date2').datepicker('getFormattedDate')) - Date.parse($('#date1').datepicker('getFormattedDate')) < 0 ){
				alert("Start date must be before End date!");
				return;
			}
			document.getElementById("download_csv_form").action = "/download_csv";
			document.getElementById("download_csv_form").submit();

		}

		function plot_and_show(data){
			var diagram = document.getElementById("diagram");
			var all_traces = [];
			var Parameters = $("#Parameter").val();
			if (data.length == 0){
				return
			}
			
			for (j = 4; j < data[0].length; j++){
				var x = [];
				var y = [];
				var comment = [];

				for (i = 0; i < data.length; i++){
					x.push(data[i][1]);
					y.push(data[i][j]);
					comment.push("Comment: "+data[i][3]);
				}
				var trace = {
							  x: x,
							  y: y,
							  type: 'scattergl',
							  mode: 'lines+markers',
							  showlegend: true,
							  text: comment,
							  name: Parameters[j-4]
							};
				all_traces.push(trace);
			}
			//console.log(all_traces);
			var layout = {
						  autosize: true,
						  //width: 500,
						  //height: 500,
						  margin: {
						    l: 50,
						    r: 50,
						    b: 50,
						    t: 50,
						    pad: 0
						  },
						  paper_bgcolor: '#f5f5f5',
						  plot_bgcolor: '#ffffff',
						  yaxis: {
						  		autorange: true,
							    //rangemode: 'tozero',
							    type: 'linear'
							  },
					     hovermode: 'closest',
					     title: $("#Module").val()+", "+$("#Machine").val()+", "+$("#Beam").val()+", "+$("#Phantom").val()
						};
			Plotly.newPlot(diagram, all_traces, layout);
			}


		function create_table(data){
			var Parameters = $("#Parameter").val();

			column_names = ["rowid", "Datetime", "User", "Comment"];

			for (var i=0; i <Parameters.length; ++i ){
				column_names.push(Parameters[i]);
			}

			columns_declaration = [];
			for (var j=0; j<column_names.length; ++j){
				columns_declaration.push({title:column_names[j], field:column_names[j]});
			}

			table.setColumns(columns_declaration);
			table.setSort ("Datetime", "desc");

			data_declaration = [];
			for (var k=0; k<data.length; ++k){
				json = {};
				for (var m=0; m<column_names.length; ++m){
					json[column_names[m]] = data[k][m];
				}
				data_declaration.push(json);
				
			}
			table.replaceData(data_declaration);
			// Hide rowid column if the user is not admin
			% if not is_admin:
				table.hideColumn("rowid");
			% end
		}

		% if is_admin:
			function remove_measurement(){
				var formData = new FormData();
				var rowid = document.getElementById("remove_row_id").value;
				var module = $("#Module").val();
				formData.append("rowid", rowid);
				formData.append("module", module);
				
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
							fetch_data();
						}
					}
					xmlhttp.open("POST", "/remove_measurement", true);
					xmlhttp.send(formData);
			}
		% end

		$(document).ready(function () {
			var date_input1 = $('input[name="date1"]'); //our date input has the name "date"
			var date_input2 = $('input[name="date2"]'); // date (final) for histograms
			var container = "body";
			var options = {
				format: "yyyy-mm-dd",
				container: container,
				todayHighlight: true,
				autoclose: true,
				clearBtn: true,
			};
			date_input1.datepicker(options).on('changeDate', function (e) {
			});
			date_input2.datepicker(options).on('changeDate', function (e) {
			});

			$('#Module').on('change', function(){
				change_testtype($("#Module").val());
				change_machine($("#Module").val());
				
				if ($("#Module").val()=="Fieldsize"){
					$('#sizing-addon2-phantom').html("Size");
				}
				else if($("#Module").val()=="Fieldrot"){
					$('#sizing-addon2-phantom').html("Nominal angle");
				}
				else{
					$('#sizing-addon2-phantom').html("Phantom");
				}

				if ($("#Module").val()=="Starshot" | $("#Module").val()=="Picketfence" | $("#Module").val()=="Flatness/Symmetry" | $("#Module").val()=="Vmat"){
					$('#Phantom').parents('.input-group').hide();
				}
				else{
					$('#Phantom').parents('.input-group').show();
				}
			});
			$('#TestType').on('change', function(){
				change_parameters($("#Module").val(), $("#TestType").val());
			});
			$('#Machine').on('change', function(){
				change_beam($("#Machine").val());
				change_phantom($("#Machine").val());
			});
			populate_modules();
			populate_machines();

		});


	</script>


</body>


</html>