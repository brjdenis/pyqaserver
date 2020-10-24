<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">

    <title>Flatness/Symmetry</title>

    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/module_result.css" rel="stylesheet">
    <script src="/bootstrap/js/jquery.min.js"></script>
    <script src="/bootstrap/js/bootstrap.min.js"></script>
    <script src="/bootstrap/js/bootstrap-select.min.js"></script>
    <link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">

</head>

<body>

        <ul class="nav nav-tabs nav-justified">
            <li class="active">
              <a data-toggle="pill" href="#menu1">
                Results 
                 % if passed:
                    <span class="label label-success">Passed</span>
                 % else:
                    <span class="label label-danger">Failed</span>
                 % end
             </a>
            </li>
            <li>
                <a data-toggle="pill" href="#menu2">
                    Save results
                </a>
            </li>
          </ul>

          <div class="tab-content">
            <div id="menu1" class="tab-pane fade in active">
                <table class="table">
                    <tr>
                        <td>
                        </td>
                        <td>
                            Horizontal
                        </td>
                        <td>
                            Vertical
                        </td>
                    </tr>
                    <tr>
                        <td>
                            Flatness
                        </td>
                        <td>
                            {{flatness_hor}}
                        </td>
                        <td>
                            {{flatness_vrt}}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            Symmetry
                        </td>
                        <td>
                            {{symmetry_hor}}
                        </td>
                        <td>
                            {{symmetry_vrt}}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            Field width
                        </td>
                        <td>
                            {{horizontal_width}} mm
                        </td>
                        <td>
                            {{vertical_width}} mm
                        </td>
                    </tr>
                    <tr>
                        <td>
                            Penumbra width
                        </td>
                        <td>
                            {{horizontal_penumbra_width}} mm 
                        </td>
                        <td>
                            {{vertical_penumbra_width}} mm
                        </td>
                    </tr>

                </table>

                {{!script}}
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
                                         
                                     </select> 
                                 </div>
                             </div>
                             <div class="col-sm-3 col-md-3">
                                 <div class="form-group">
                                     <label class="control-label" for="energies">Beam:</label>
                                     <select class="selectpicker show-tick form-control"  name="energies" id="energies">
                                        
                                     </select> 
                                 </div>
                             </div>
                             <div class="col-sm-3 col-md-3">
                                <div class="form-group">
                                     <label class="control-label" for="energies">Test type:</label>
                                     <select class="selectpicker show-tick form-control">
                                        <option value="{{calc_definition}}">{{calc_definition}}</option>
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
            
            var json_data = {"User": "{{save_results['displayname']}}",
                             "Machine": $('#machines').val(),
                             "Beam": $('#energies').val(),
                             "Datetime": "{{acquisition_datetime}}",
                             "Comment": $('#comment').val(),
                             "TestType": "{{calc_definition}}",
                             "Symmetry_hor": "{{symmetry_hor}}",
                             "Symmetry_vrt": "{{symmetry_vrt}}",
                             "Flatness_hor": "{{flatness_hor}}",
                             "Flatness_vrt": "{{flatness_vrt}}",
                             "Horizontal_width": "{{horizontal_width}}",
                             "Vertical_width": "{{vertical_width}}",
                             "Horizontal_penumbra_width": "{{horizontal_penumbra_width}}",
                             "Vertical_penumbra_width": "{{vertical_penumbra_width}}"
                         }

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
                xmlhttp.open("POST", "/save_flatsym", true);
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