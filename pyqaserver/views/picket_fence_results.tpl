<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Picket fence results</title>
    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <script src="/bootstrap/js/jquery.min.js"></script>
    <script src="/bootstrap/js/bootstrap.min.js"></script>
    <link href="/css/module_result.css" rel="stylesheet">
    <script src="/bootstrap/js/bootstrap-select.min.js"></script>
    <link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
</head>

<body>

    <ul class="nav nav-tabs nav-justified">
        <li class="active"><a data-toggle="pill" href="#menu1">Image</a></li>
        <li><a data-toggle="pill" href="#menu2">
            Results
            % if passed == "Failed":
                <span class='label label-danger'>Failed</span>
            % else:
                <span class='label label-success'>Passed</span>
            % end
        </a></li>
        <li>
         <a data-toggle="pill" href="#menu4">Save result</a>
        </li>
    </ul>
<div class="tab-content">

	<div id="menu1" class="tab-pane fade in active">

	{{!script}}
	
    </div>
	
	
	<div id="menu2" class="tab-pane fade">

    <p>
    <table  class="table">
        <tr>
            <td>
                Nr of pickets
            </td>
            <td>
                Pass prct
            </td>
            <td>
                Max error
            </td>
            <td>
                Max error picket
            </td>
            <td>
                Max error leaf
            </td>
			<td>
				Median error
			</td>
            <td>
                Mean picket spacing
            </td>
			<td>
                Mean FWHM
            </td>
        </tr>
        <tr>
            <td>{{picket_nr}}</td>
            <td>{{round(perc_passing, 2)}} %</td>
            <td>{{round(max_error_all, 2)}} mm</td>
            <td>{{max_error_picket_all}}</td>
            <td>{{max_error_leaf_all}}</td>
			<td>{{round(median_error, 2)}} mm</td>
            <td>{{round(spacing, 2)}} mm</td>
			<td>{{round(fwhm_mean, 2)}} mm</td>
        </tr>
    </table>
    </p>
    <br>

    <h3>Errors per picket</h3>
    <p>
    
    <table class="table">
        <tr>
            <td>
                Picket
            </td>
            <td>
                Max error [mm]
            </td>
            <td>
                Max error leaf
            </td>
			<td>
				Offset from CAX [mm]
			</td>
			<td>
				FWHM [mm]
			</td>
            <td>
                Passed (tol. {{tolerance}} mm)
            </td>
        </tr>
    % for m in range(0, picket_nr, 1):
        <tr>
            <td>
                {{m}}
            </td>
            <td>
                {{round(max_error[m], 2)}}
            </td>
            <td>
                {{max_error_leaf[m]}}
            </td>
			<td>
				{{round(picket_offsets[m], 2)}}
			</td>
			<td>
				{{round(picket_fwhm[m], 2)}}
			</td>
            <td>
                {{passed_tol[m]}}
            </td>
    % end
        </tr>
    </table>
    </p>
    <br>
    
	{{!script2}}
	</div>
	
    <div id="menu4" class="tab-pane fade">
          <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Save to database</h3>
            </div>
            <div class="panel-body">
                <div class="row">
                    <div class="col-sm-3 col-md-3">
                        <div class="form-group">
                             <label class="control-label" for="machines">Machine:</label>
                             <select class="selectpicker show-tick form-control" data-size="15" name="machines" id="machines">
                             </select> 
                         </div>
                     </div>
                     <div class="col-sm-3 col-md-3">
                         <div class="form-group">
                             <label class="control-label" for="energies">Energy:</label>
                             <select class="selectpicker show-tick form-control" data-size="15" name="energies" id="energies">
                             </select> 
                         </div>
                     </div>
                     <div class="col-sm-3 col-md-3">
                         
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
                 % if pdf_report_enable == "True":
                    <br>
                        <form method = "post" target="_self">
                            <input type="hidden" name="hidden_wl_pdf_report" id="hidden_wl_pdf_report" value="{{pdf_report_filename}}"/>
                            <input type="submit" value = "Export PDF" name = "pdf_export" formaction="/winstonlutz_pdf_export" onchange="this.form.submit()"/></p>
                        </form>
                % end
            </div>
        </div>


</div>

<script>
    var machines_and_energies =  {{!save_results["machines_and_energies"]}};
        
        function load_machines_energies(){
            if (machines_and_energies.length != 0){
                var selected_machine = 0;
                var html = [];
                for (j = 0; j < machines_and_energies.length; j++) {
                    if (machines_and_energies[j][0]=='{{save_results["user_machine"]}}'){
                        html.push("<option " + "value='" + machines_and_energies[j][0] + "' selected>" + machines_and_energies[j][0] + "");
                        selected_machine = j;
                    }
                    else{
                        html.push("<option " + "value='" + machines_and_energies[j][0] + "'>" + machines_and_energies[j][0] + "");
                    }
                }

                change_energies(selected_machine);
                $('#machines').html(html);
                $('#machines').selectpicker('refresh');
            }
        }

        function change_energies(selected_machine){
            if (machines_and_energies.length != 0){
                var html = [];
                for (j = 0; j < machines_and_energies[selected_machine][1].length; j++) {
                    if (machines_and_energies[selected_machine][1][j]=='{{save_results["user_energy"]}}'){
                        html.push("<option " + "value='" + machines_and_energies[selected_machine][1][j] + "' selected>" + machines_and_energies[selected_machine][1][j] + "");
                    }
                    else{
                        html.push("<option " + "value='" + machines_and_energies[selected_machine][1][j] + "'>" + machines_and_energies[selected_machine][1][j] + "");
                    }
                }
                $('#energies').html(html);
                $('#energies').selectpicker('refresh');
            }
        }

        function save_to_database(){
            var formData = new FormData();
            var json_data = {"User": "{{save_results["displayname"]}}",
                             "Machine": $('#machines').val(),
                             "Beam": $('#energies').val(),
                             "Datetime": "{{acquisition_datetime}}",
                             "Comment": $('#comment').val(),
                             "PassPrcnt": "{{round(perc_passing, 2)}}",
                             "MaxError": "{{round(max_error_all, 2)}}",
                             "MaxErrorPckt": "{{max_error_picket_all}}",
                             "MaxErrorLeaf": "{{max_error_leaf_all}}",
                             "MedianError": "{{round(median_error, 2)}}",
                             "MeanPicketSpacing": "{{round(spacing, 2)}}",
                             "MeanFWHM": "{{round(fwhm_mean, 2)}}"
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
                xmlhttp.open("POST", "/save_picketfence", true);
                xmlhttp.send(formData);
                document.getElementById("save_button").disabled = true;
                document.getElementById("save_error").innerHTML = "Working on it ... ";
        }
        
        $(document).ready(function() {
            load_machines_energies();
            
            $('#machines').on('change', function(){
                change_energies($("#machines").prop('selectedIndex'));
            })
        });
</script>



</body>
</html>