<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Planar imaging results</title>
    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <script src="/bootstrap/js/jquery.min.js"></script>
    <script src="/bootstrap/js/bootstrap.min.js"></script>
    <link href="/css/module_result.css" rel="stylesheet">
</head>

<body>
		<ul class="nav nav-tabs nav-justified">
		    <li class="active">
		        <a data-toggle="pill" href="#menu1">Results</a>
		    </li>
		    <li>
		        <a data-toggle="pill" id="bs-tab2" href="#menu2">Save results</a>
		    </li>
		</ul>

		<div class="tab-content">
    		<div id="menu1" class="tab-pane fade in active">

				{{!script}}
				<br>
				{{!script2}}
				<br>
				<table class="table">
					<tr>
						<td></td><td>Reference</td><td>Current</td>
					</tr>
					<tr>
						<td>f<sub>30</sub></td><td>{{round(f30[0], 3)}}</td><td>{{round(f30[1], 3)}}</td>
					</tr>
					<tr>
						<td>f<sub>40</sub></td><td>{{round(f40[0], 3)}}</td><td>{{round(f40[1], 3)}}</td>
					</tr>
					<tr>
						<td>f<sub>50</sub></td><td>{{round(f50[0], 3)}}</td><td>{{round(f50[1], 3)}}</td>
					</tr>
					<tr>
						<td>f<sub>80</sub></td><td>{{round(f80[0], 3)}}</td><td>{{round(f80[1], 3)}}</td>
					</tr>
					<tr>
						<td>Median Contrast</td><td>{{round(median_contrast[0], 3)}}</td><td>{{round(median_contrast[1], 3)}}</td>
					</tr>
					<tr>
						<td>Median CNR</td><td>{{round(median_CNR[0], 2)}}</td><td>{{round(median_CNR[1], 2)}}</td>
					</tr>
					<tr>
						<td>Phantom angle</td><td>{{round(phantom_angle[0], 2)}}</td><td>{{round(phantom_angle[1], 2)}}</td>
					</tr>
					
				</table>

			</div>
		    <div id="menu2" class="tab-pane fade">
		        <div class="panel panel-default">
		            <div class="panel-heading">
		                <h3 class="panel-title">Save to database</h3>
		            </div>
		            <div class="panel-body">
		                <div class="row">
		                    <div class="col-sm-3 col-md-3">
		                        <div class="form-group">
		                             <label class="control-label" for="machines">Machine:</label>
		                             <select class="selectpicker show-tick form-control" name="machines" id="machines">
		                             	<option value="{{save_results["machine"]}}">{{save_results["machine"]}}</option>
		                             </select> 
		                         </div>
		                     </div>
		                     <div class="col-sm-3 col-md-3">
		                         <div class="form-group">
		                             <label class="control-label" for="energies">Beam:</label>
		                             <select class="selectpicker show-tick form-control"  name="energies" id="energies">
		                             	<option value="{{save_results["beam"]}}">{{save_results["beam"]}}</option>
		                             </select> 
		                         </div>
		                     </div>
		                     <div class="col-sm-3 col-md-3">
		                         <div class="form-group">
		                             <label class="control-label" for="phantom">Phantom:</label>
		                             <select class="selectpicker show-tick form-control"  name="phantom" id="phantom">
		                             	<option value="{{save_results["phantom"]}}">{{save_results["phantom"]}}</option>
		                             </select> 
		                         </div>
		                     </div>
		                     <div class="col-sm-3 col-md-3">
		                     </div>
		                </div>
		                <div class="row">
		                    <div class="col-sm-6 col-md-6">
		                        <div class="form-group purple-border">
		                            <label for="comment">Comment:</label>
		                            <textarea type="text" class="form-control" id="comment" rows="3"></textarea>
		                        </div>
		                    </div>
		                </div>
		                <div class="row">
		                    <div class="col-sm-6 col-md-6">
		                        <button type="submit" class="btn btn-default" name="save_button" id="save_button" onclick="save_to_database();">Save</button>
		                        <strong><p class="text-danger"><small id="save_error"></small></p></strong>
		                    </div>
		                </div>
		                <p>
				            % if pdf_report_enable == "True":
								<br>
								<form method = "post" target="_self">
									<input type="hidden" name="hidden_wl_pdf_report" id="hidden_wl_pdf_report" value="{{pdf_report_filename}}"/>
									<input type="submit" value = "Export PDF" name = "pdf_export" formaction="/winstonlutz_pdf_export" onchange="this.form.submit()"/></p>
								</form>
							% end
						</p>
		            </div>
		        </div>
	    	</div>
	    </div>

    <script>
	    $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
	        var iframe = parent.document.getElementById('receiver2');
	        parent.resizeIFrameToFitContent(iframe);
	    });

        function save_to_database(){
            var formData = new FormData();
            var json_data = {"User": "{{save_results["displayname"]}}",
                             "Machine": $('#machines').val(),
                             "Beam": $('#energies').val(),
                             "Phantom": $('#phantom').val(),
                             "Datetime": "{{acquisition_datetime}}",
                             "f30": "{{round(f30[1], 3)}}",
                             "f40": "{{round(f40[1], 3)}}",
                             "f50": "{{round(f50[1], 3)}}",
                             "f80": "{{round(f80[1], 3)}}",
                             "MedianContrast": "{{round(median_contrast[1], 3)}}",
                             "MedianCNR": "{{round(median_CNR[1], 2)}}",
                             "Comment": $('#comment').val()
                            };
        
            formData.append("json_data", JSON.stringify(json_data));
            
            if (window.XMLHttpRequest) {
                    // code for IE7+, Firefox, Chrome, Opera, Safari
                    xmlhttp = new XMLHttpRequest();
                } else {  // code for IE6, IE5
                    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                }
                xmlhttp.onreadystatechange = function () {
                    if (this.readyState == 4 && this.status == 200) {
                        temp = this.responseText;
                        document.getElementById("save_error").innerHTML += temp;
                        if (temp="Done!"){
                            document.getElementById("save_error").class = "text-success";
                        }
                        
                    }
                }
                xmlhttp.open("POST", "/save_planarimaging", true);
                xmlhttp.send(formData);
                document.getElementById("save_button").disabled = true;
                document.getElementById("save_error").innerHTML = "Working on it ... ";
        }

	</script>

</body>
</html>