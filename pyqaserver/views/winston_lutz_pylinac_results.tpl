<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>Winston-Lutz analysis</title>

  <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
  <script src="/bootstrap/js/jquery.min.js"></script>
  <script src="/bootstrap/js/bootstrap.min.js"></script>
  <link href="/css/module_result.css" rel="stylesheet">
  <script src="/bootstrap/js/bootstrap-select.min.js"></script>
  <link href="/bootstrap/css/bootstrap-select.min.css" rel="stylesheet">
  

</head>

<body>
  <ul class="nav nav-tabs nav-justified">
    <li class="active">
      <a data-toggle="pill" href="#menu1">Images</a>
    </li>
    <li>
        <a data-toggle="pill" id="bs-tab2" href="#menu2">
            Analysis
            % if max_deviation > pass_rate:
                <span class="label label-danger">Failed</span>
            % elif (max_deviation <= pass_rate) and (max_deviation> success_rate):
                <span class="label label-warning">Borderline</span>
            % else:
                <span class="label label-success">Passed</span>
            % end
        </a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu21">Scatter diagram</a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu3">Save result</a>
    </li>
  </ul>

  <div class="tab-content">
    <div id="menu1" class="tab-pane fade in active">
      
      % if axis_images[0] != None:
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">Gantry images</h3>
          </div>
          <div class="panel-body">
              {{!axis_images[0]}}
          </div>
        </div>
      % end
      % if axis_images[1] != None:
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">Collimator images</h3>
          </div>
          <div class="panel-body">
            {{!axis_images[1]}}
          </div>
        </div>
      % end
      % if axis_images[2] != None:
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">Couch images</h3>
          </div>
          <div class="panel-body">
            {{!axis_images[2]}}
          </div>
        </div>
      % end
      % if axis_images[3] != None:
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">GB Combo images</h3>
          </div>
          <div class="panel-body">
            {{!axis_images[3]}}
          </div>
        </div>
      % end
      % if axis_images[4] != None:
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">GBP Combo images</h3>
          </div>
          <div class="panel-body">
            {{!axis_images[4]}}
          </div>
        </div>
      % end
      % if axis_images[5] != None:
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">All images</h3>
          </div>
          <div class="panel-body">
            {{!axis_images[5]}}
          </div>
        </div>
      % end
    </div>

    <div id="menu2" class="tab-pane fade">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Image analysis</h3>
        </div>
        <div class="panel-body">
          Deviations are measured with respect to the EPID center.
          &Delta; x and &Delta; y are calculated with BB as the origin.
        </div>
        <table class="table">
          <tr>
            <td>
              Image
            </td>
            <td>
              G
            </td>
            <td>
              B
            </td>
            <td>
              P
            </td>
            <td>
              Axis
            </td>
            <td>
              CAX x [mm]
            </td>
            <td>
              CAX y [mm]
            </td>
            <td>
              BB x [mm]
            </td>
            <td>
              BB y [mm]
            </td>
            <td style="border-left:1px solid #CCCCCC;">
              &Delta;x [mm]
            </td>
            <td>
              &Delta;y [mm]
            </td>
            <td>
              R [mm]
            </td>
    
          </tr>
    
          % for k in range(0, len(result), 1):
            % if abs(round(radius[k], 2)) > pass_rate:
              <tr class="danger">
                % elif abs((round(radius[k], 2)) <= pass_rate) and (abs(round(radius[k], 2))> success_rate):
                  <tr class="warning">
                % else:
              <tr>
            % end
            <td>{{image_num[k]}}</td>
            <td>{{gantries[k]}}</td>
            <td>{{collimators[k]}}</td>
            <td>{{couches[k]}}</td>

            <td>{{image_type[k]}}</td>
    
            <td>{{round(cax_position[k][0], 2)}}</td>
            <td>{{round(cax_position[k][1], 2)}}</td>
    
            <td>{{round(bb_position[k][0], 2)}}</td>
            <td>{{round(bb_position[k][1], 2)}}</td>
    
            <td style="border-left:1px solid #CCCCCC;">{{round(result[k][0], 2)}}</td>
            <td>{{round(result[k][1], 2)}}</td>
    
            <td>{{round(radius[k], 2)}}</td>
    
          </tr>
          % end
        </table>
      </div>
      
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Quick results</h3>
        </div>
          <ul class="list-group">
            % for q in quickresults:
              <li class="list-group-item">{{q}}</li>
            % end
          </ul>
      </div>

        % if script_wobble != None:
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="panel-title">Axis wobble</h3>
          </div>
          <div class="panel-body">
            {{!script_wobble}}
          </div>
        </div>
      % end
      
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Relative displacement</h3>
        </div>
        <div class="panel-body">
          {{!script_gantry_epid_sag}}
        </div>
      </div>

      <div class="alert alert-info" role="alert">
        The following SIDs were detected [mm]:
        % for t in range(0, len(SIDs), 1):
          {{round(SIDs[t], 2)}},&#32;
        % end
      </div>
      <form method="post" target="_self">
        <input type="hidden" name="hidden_wl_pdf_report" id="hidden_wl_pdf_report" value="{{pdf_report_filename}}" />
        <button type="submit" class="btn btn-default" name="wl_pdf_export" formaction="{{plweb_folder}}/winstonlutz_pdf_export" onclick="this.form.submit()" />Get pylinac report</button>
      </form>

    </div>
    
    <div id="menu21" class="tab-pane fade">
      {{!script_focal}}
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
                             <label class="control-label" for="phantom">Phantom:</label>
                             <select class="selectpicker show-tick form-control" data-size="15" name="phantom" id="phantom">
                                % for p in range(len(save_results["phantoms"])):
                                    <option value="{{save_results["phantoms"][p][1]}}">{{save_results["phantoms"][p][1]}}</option>
                                % end
                             </select> 
                         </div>
                     </div>
                     <div class="col-sm-3 col-md-3">
                     </div>
                </div>
                <div class="row">
                    <div class="col-sm-6 col-md-6">
                        <div class="form-group">
                             <label class="control-label" for="phantom">Pylinac test type:</label>
                             <select class="selectpicker show-tick form-control" data-size="15" name="pylinac_test_type" id="pylinac_test_type">
                                    <option value="Pylinac Gantry only">Pylinac Gantry only</option>
                                    <option value="Pylinac Collimator only">Pylinac Collimator only</option>
                                    <option value="Pylinac Couch only">Pylinac Couch only</option>
                                    <option value="Pylinac Mixed">Pylinac Mixed</option>
                             </select> 
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
  </div>


  <script>
      $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
        var iframe = parent.document.getElementById('receiver2');
        parent.resizeIFrameToFitContent(iframe);
      });
  </script>

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
                             "Phantom": $('#phantom').val(),
                             "Datetime": "{{acquisition_datetime}}",
                             "TestType": $('#pylinac_test_type').val(),
                             "Max2DbbCAX": "{{round(Max2DbbCAX, 2)}}",
                             "Median2DbbCAX": "{{round(Median2DbbCAX, 2)}}",
                             "BBshiftX": "{{round(BBshiftX, 2)}}",
                             "BBshiftY": "{{round(BBshiftY, 2)}}",
                             "BBshiftZ": "{{round(BBshiftZ, 2)}}",
                             "GntIsoSize": "{{round(GntIsoSize, 2)}}",
                             "MaxGntRMS": "{{round(MaxGntRMS, 2)}}",
                             "MaxEpidRMS": "{{round(MaxEpidRMS, 2)}}",
                             "GntColl3DisoSize": "{{round(GntColl3DisoSize, 2)}}",
                             "Coll2DisoSize": "{{round(Coll2DisoSize, 2)}}",
                             "MaxCollRMS": "{{round(MaxCollRMS, 2)}}",
                             "Couch2DisoDia": "{{round(Couch2DisoDia, 2)}}",
                             "MaxCouchRMS": "{{round(MaxCouchRMS, 2)}}",
                             "RadiusMax": "{{round(max(radius), 2)}}",
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
                xmlhttp.open("POST", "{{plweb_folder}}/save_winstonlutz", true);
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