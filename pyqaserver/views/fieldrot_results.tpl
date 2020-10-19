<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>Field rotation results</title>

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
        </a>
      </li>
      <li>
        <a data-toggle="pill" href="#menu2">
            Check and save
        </a>
      </li>
    </ul>


 <div class="tab-content">
    <div id="menu1" class="tab-pane fade in active">
    
    % if test_type == "Collimator absolute":
      <table class="table">
              <tr>
                  <td>
                  </td>
                  <td>
                      Blue edge angle
                  </td>
                  <td>
                      Yellow edge angle
                  </td>
                  <td>
                      BB angle
                  </td>
              </tr>
              <tr>
                  <td>
                      Image 1 (gantry 0)
                  </td>
                  <td>
                      {{round(left_edge_angle1, 2)}}
                  </td>
                  <td>
                      {{round(right_edge_angle1, 2)}}
                  </td>
                   <td>
                      {{round(bb_angle1, 2)}}
                  </td>
              </tr>
              <tr>
                  <td>
                      Image 2 (gantry 180)
                  </td>
                  <td>
                      {{round(left_edge_angle2, 2)}}
                  </td>
                  <td>
                      {{round(right_edge_angle2, 2)}}
                  </td>
                  <td>
                      {{round(bb_angle2, 2)}}
                  </td>
              </tr>
              %    epid_field_angle = 0
              % if abs(bb_angle1) > 80 and abs(bb_angle1) <= 90:
              %    left_edge_angle1 = left_edge_angle1 if left_edge_angle1 >= 0 else 180 + left_edge_angle1
              %    right_edge_angle1 = right_edge_angle1 if right_edge_angle1 >= 0 else 180 + right_edge_angle1
              %    bb_angle1 = bb_angle1 if bb_angle1 >= 0 else 180 + bb_angle1
              %    epid_field_angle = 90
              % end
              % if abs(bb_angle2) > 80 and abs(bb_angle2) <= 90:
              %    left_edge_angle2 = left_edge_angle2 if left_edge_angle2 >= 0 else 180 + left_edge_angle2
              %    right_edge_angle2 = right_edge_angle2 if right_edge_angle2 >= 0 else 180 + right_edge_angle2
              %    bb_angle2 = bb_angle2 if bb_angle2 >= 0 else 180 + bb_angle2
              % end
              <tr>
                  <td>
                      Collimator angle error
                  </td>
                    <td>
                        % ce1 = (left_edge_angle2 - bb_angle2 + left_edge_angle1 - bb_angle1)/2
                        {{round(ce1, 2)}}
                    </td>
                    <td>
                        % ce2 = (right_edge_angle2 - bb_angle2 + right_edge_angle1 - bb_angle1)/2
                        {{round(ce2, 2)}}
                    </td>
                  <td>
                      /
                  </td>
              </tr>
              <tr>
                <td>
                    EPID angle error
                </td>
                <td>
                      {{round(left_edge_angle1-ce1-epid_field_angle, 2)}}
                </td>
                <td>
                      {{round(right_edge_angle1-ce2-epid_field_angle, 2)}}
                </td>
                <td>
                      /
                </td>
              </tr>
              
              
          </table>
          <p>Angles are measured with respect to the image and have values between [-90, 90]. Collimator error is calculated with BB as the reference.</p>
      
      % elif test_type == "Collimator relative":
        <table class="table">
              <tr>
                  <td>
                  </td>
                  <td>
                      Blue edge angle
                  </td>
                  <td>
                      Yellow edge angle
                  </td>
              </tr>
              <tr>
                  <td>
                      Image 1
                  </td>
                  <td>
                      {{round(left_edge_angle1, 2)}}
                  </td>
                  <td>
                      {{round(right_edge_angle1, 2)}}
                  </td>
              </tr>
              <tr>
                  <td>
                      Image 2
                  </td>
                  <td>
                      {{round(left_edge_angle2, 2)}}
                  </td>
                  <td>
                      {{round(right_edge_angle2, 2)}}
                  </td>
              </tr>
              <tr>
                  <td>
                      Difference
                  </td>
                  <td>
                      {{round(left_edge_angle2  - left_edge_angle1 , 2)}}
                  </td>
                  <td>
                      {{round(right_edge_angle2  - right_edge_angle1 , 2)}}
                  </td>
              </tr>
          </table>
          <p>Field edge angles are measured with respect to the image and have values between [-90, 90].</p>
      % else:
        <table class="table">
              <tr>
                  <td>
                  </td>
                  <td>
                      BB angle
                  </td>
                  <td>
                      BB line center
                  </td>
              </tr>
              <tr>
                  <td>
                      Image 1
                  </td>
                  <td>
                      {{round(bb_angle1, 2)}}
                  </td>
                  <td>
                      [{{round(bb_line_center1[0], 2)}}, {{round(bb_line_center1[1], 2)}}]
                  </td>
              </tr>
              <tr>
                  <td>
                      Image 2
                  </td>
                  <td>
                      {{round(bb_angle2, 2)}}
                  </td>
                  <td>
                      [{{round(bb_line_center2[0], 2)}}, {{round(bb_line_center2[1], 2)}}]
                  </td>
              </tr>
              <tr>
                  <td>
                      Difference
                  </td>
                  <td>
                      {{round(bb_angle2  - bb_angle1 , 2)}}
                  </td>
                  <td>
                      [{{round(bb_line_center2[0]-bb_line_center1[0], 2)}}, {{round(bb_line_center2[1]-bb_line_center1[1], 2)}}]
                  </td>
              </tr>
          </table>
          <p>BB line angle is measured with respect to the image and has values between [-90, 90].</p>
      % end

        {{!script1}}
       {{!script2}}
        {{!script3}}
    </div>

    <div id="menu2" class="tab-pane fade">
      <div class="panel panel-default">
          <div class="panel-heading">
              <h3 class="panel-title">Check and save to database</h3>
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
                              <option value="{{test_type}}">{{test_type}}</option>
                           </select> 
                       </div>
                   </div>
                   <div class="col-sm-3 col-md-3">
                   </div>
              </div>
              <div class="row">
                <div class="col-sm-3 col-md-3">
                      <div class="form-group">
                           <label class="control-label" for="nominal_angle">Nominal angle:</label>
                           <select class="selectpicker show-tick form-control" data-size="15" name="nominal_angle" id="nominal_angle">
                            % for p in range(len(save_results["nominal_angle"])):
                                % if save_results["nominal_angle"][p]==0:
                                    <option value="{{save_results["nominal_angle"][p]}}" selected>{{save_results["nominal_angle"][p]}}</option>
                                % else:
                                  <option value="{{save_results["nominal_angle"][p]}}">{{save_results["nominal_angle"][p]}}</option>
                                % end
                            % end
                           </select> 
                       </div>
                   </div>
                   <div class="col-sm-3 col-md-3">
                       <div class="form-group">
                           <label class="control-label" for="measured_angle">Measured angle:</label>
                           <input type="text" class="form-control" id="measured_angle" name="measured_angle" autocomplete="off" onkeyup="this.value=this.value.replace(/,/,'.')">
                           </select> 
                       </div>
                   </div>
                   <div class="col-sm-3 col-md-3">
                       <div class="form-group">
                           <label class="control-label" for="status_passing">Status (tol. {{tolerance}} deg):</label>
                           <span class="label label-primary" style="display: inline-block;" id="status_passing" name="status_passing">Status</span>
                       </div>
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
            if ($('#measured_angle').val()==""){
                alert("Measured angle cannot be an empty string!");
                return;
            }
            var formData = new FormData();
            var json_data = {"User": "{{save_results["displayname"]}}",
                             "Machine": $('#machines').val(),
                             "Beam": $('#energies').val(),
                             "Phantom": $('#nominal_angle').val(),
                             "TestType": $('#testtype').val(),
                             "Datetime": "{{acquisition_datetime}}",
                             "Angle": $('#measured_angle').val(),
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
                xmlhttp.open("POST", "{{plweb_folder}}/save_fieldrotation", true);
                xmlhttp.send(formData);
                document.getElementById("save_button").disabled = true;
                document.getElementById("save_error").innerHTML = "Working on it ... ";
        }

    $(document).ready(function() {
        load_machines_energies();
            
        $('#machines').on('change', function(){
            change_energies($("#machines").prop('selectedIndex'));
        });

        $('#measured_angle').on('input', function(){
            change_status();
        });

        $('#nominal_angle').on('change', function(){
            change_status();
        });

        function change_status(){
          if ($("#measured_angle").val()==""){
            $('#status_passing').html("Status").removeClass("label-danger label-success").addClass("label-primary");
            return;
          }
          if (Math.abs($("#nominal_angle").val() - $("#measured_angle").val()) <= parseFloat("{{tolerance}}"))
            {
              $('#status_passing').html("Passed").removeClass("label-danger label-primary").addClass("label-success");
            }
          else{
              $('#status_passing').html("Failed").removeClass("label-success label-primary").addClass("label-danger");
            }
        }
        
    });
  </script>



</body>

</html>