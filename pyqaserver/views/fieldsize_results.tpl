<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>Field size results</title>

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
      % if passed_mlc and passed_jaw and passed_iso:
        <span class="label label-success">Passed</span>
      % else:
        <span class="label label-danger">Failed</span>
      % end
      </a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu2">Images</a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu21">Mechanical center</a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu3">
            Save results
        </a>
    </li>
  </ul>

  <div class="tab-content">
    <div id="menu1" class="tab-pane fade in active">
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">
             Average field width
            </h3>
          </div>
            <div class="panel-body">
              <table class="table table-condensed">
                <tr>
                    <td></td>
                    <td>Side 1 [mm]</td>
                    <td>Side 2 [mm]</td>
                    <td>Exp. width [mm]</td>
                    <td>Width [mm]</td>
                    <td>Tol. [mm]</td>
                </tr>
                % if not passed_mlc:
                  <tr class="danger">
                % else:
                  <tr>
                % end
                  <td>Leaf direction</td>
                  <td>{{round(MLC_size_L, 2)}}</td>
                  <td>{{round(MLC_size_R, 2)}}</td>
                  <td>{{round(expected_mlc, 2)}}</td>
                  <td>{{round(MLC_size_full, 2)}}</td>
                  <td>{{round(tolerance_mlc, 2)}}</td>
                </tr>
                % if not passed_jaw:
                  <tr class="danger">
                % else:
                  <tr>
                % end
                <td>Jaw direction</td>
                <td>{{round(jaw_size_L, 2)}}</td>
                <td>{{round(jaw_size_R, 2)}}</td>
                <td>{{round(expected_jaw, 2)}}</td>
                <td>{{round(jaw_size_full, 2)}}</td>
                <td>{{round(tolerance_jaw, 2)}}</td>
              </tr>
              </table>
            </div>
        </div>

        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">Radiation center offset from mechanical center</h3>
          </div>
          <div class="panel-body">
            <table class="table table-condensed">
              <tr>
                  <td>&Delta; X [mm]</td>
                  <td>&Delta; Y [mm]</td>
                  <td>Tol. [mm]</td>
              </tr>
              % if not passed_iso:
                  <tr class="danger">
              % else:
                  <tr>
              % end
                  <td>{{round(center_offset_x, 2)}}</td>
                  <td>{{round(center_offset_y, 2)}}</td>
                  <td>r = {{tolerance_iso}}</td>
              </tr>
            </table>
          </div>
        </div>

        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">Field rotation</h3>
          </div>
          <div class="panel-body">
            <p>Edge points (leaves) are not included in the calculation of field rotation. Positive angle signifies a counter-clockwise rotation with respect to the horizontal or vertical line.</p>
            <table class="table table-condensed">
              <tr>
                  <td>MLC 1 [°]</td>
                  <td>MLC 2 [°]</td>
                  <td>Jaw 1 [°]</td>
                  <td>Jaw 2 [°]</td>
              </tr>
              <tr>
                  <td>{{round(angle_mlc_L, 2)}}</td>
                  <td>{{round(angle_mlc_R, 2)}}</td>
                  <td>{{round(angle_jaw_L, 2)}}</td>
                  <td>{{round(angle_jaw_R, 2)}}</td>
              </tr>
            </table>
          </div>
        </div>

        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">
              <a data-toggle="collapse" href="#collapse1">Leaf positions (expand...)</a></h3>
          </div>
          <div id="collapse1" class="panel-collapse collapse">
            <div class="panel-body">
              <table class="table table-condensed">
                <tr>
                    <td>Leaf index</td>
                    <td>Side 1 [mm]</td>
                    <td>Side 2 [mm]</td>
                    <td>Width [mm]</td>
                </tr>
                % for k in range(0, len(MLC_position_L), 1):
                    <tr>
                        <td>{{leaf_numbers[k]}}</td>
                        <td>{{round(MLC_position_L[k], 2)}}</td>
                        <td>{{round(MLC_position_R[k], 2)}}</td>
                        <td>{{round(MLC_width[k], 2)}}</td>
                    </tr>
                % end
              </table>
            </div>
          </div>
        </div>

        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">
              <a data-toggle="collapse" href="#collapse2">Jaw positions (expand...)</a></h3>
          </div>
          <div id="collapse2" class="panel-collapse collapse">
            <div class="panel-body">
              <table class="table table-condensed">
                <tr>
                    <td>Sample point</td>
                    <td>Side 1 [mm]</td>
                    <td>Side 2 [mm]</td>
                    <td>Width [mm]</td>
                </tr>
                % for k in range(0, len(jaw_position_L), 1):
                    <tr>
                        <td>{{k+1}}</td>
                        <td>{{round(jaw_position_L[k], 2)}}</td>
                        <td>{{round(jaw_position_R[k], 2)}}</td>
                        <td>{{round(jaw_width[k], 2)}}</td>
                    </tr>
                % end
              </table>
            </div>
          </div>
        </div>
    </div>

    <div id="menu2" class="tab-pane fade">

        {{!script2}}

        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">MLC</h3>
          </div>
          <div class="panel-body">
            {{!script3}}
          </div>
        </div>

        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">Jaws</h3>
          </div>
          <div class="panel-body">
            {{!script4}}
          </div>
        </div>
    </div>
    
    <div id="menu21" class="tab-pane fade">
      <h3>Pixel size and mechanical center</h3>
        <table class="table table-condensed">
          <tr>
              <td>Pixel size at isocenter [mm]</td>
              <td>Mechanical center [px]</td>
              <td>Radiation center [px]</td>
          </tr>
          <tr>
              <td>{{round(dpmm, 4)}}</td>
              <td>({{round(center[0], 1)}}, {{round(center[1], 1)}})</td>
              <td>({{round(center_rad[0], 1)}}, {{round(center_rad[1], 1)}})</td>
          </tr>
        </table>
      {{!script1}}

    </div>

    <div id="menu3" class="tab-pane fade">
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
                       <div class="form-group">
                           <label class="control-label" for="testtype">Test type:</label>
                           <select class="selectpicker show-tick form-control" data-size="15" name="testtype" id="testtype">
                              % for p in range(len(save_results["testtype"])):
                                  <option value="{{save_results["testtype"][p]}}">{{save_results["testtype"][p]}}</option>
                              % end
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
                             "Phantom": "{{!guessed_fieldsize}}",
                             "TestType": $('#testtype').val(),
                             "Datetime": "{{acquisition_datetime}}",
                             "LeafSide1": "{{round(MLC_size_L, 2)}}",
                             "LeafSide2": "{{round(MLC_size_R, 2)}}",
                             "JawSide1": "{{round(jaw_size_L, 2)}}",
                             "JawSide2": "{{round(jaw_size_R, 2)}}",
                             "LeafWidth": "{{round(MLC_size_full, 2)}}",
                             "JawWidth": "{{round(jaw_size_full, 2)}}",
                             "IsoOffsetX": "{{round(center_offset_x, 2)}}",
                             "IsoOffsetY": "{{round(center_offset_y, 2)}}",
                             "FieldRot": "{{round((angle_mlc_L+angle_mlc_R+angle_jaw_L+angle_jaw_R)/4.0, 2)}}",
                             "IsoMethod": "{{iso_method}}",
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
                xmlhttp.open("POST", "/save_fieldsize", true);
                xmlhttp.send(formData);
                document.getElementById("save_button").disabled = true;
                document.getElementById("save_error").innerHTML = "Working on it ... ";
        }

    $(document).ready(function() {
        load_machines_energies();
            
        $('#machines').on('change', function(){
            change_energies($("#machines").prop('selectedIndex'));
        })

        $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
          var iframe = parent.document.getElementById('receiver2');
          parent.resizeIFrameToFitContent(iframe);
        });
        $('#collapse1').on('shown.bs.collapse', function (e) {
          var iframe = parent.document.getElementById('receiver2');
          parent.resizeIFrameToFitContent(iframe);
        });
        $('#collapse2').on('shown.bs.collapse', function (e) {
          var iframe = parent.document.getElementById('receiver2');
          parent.resizeIFrameToFitContent(iframe);
        });
    });
  </script>

</body>

</html>