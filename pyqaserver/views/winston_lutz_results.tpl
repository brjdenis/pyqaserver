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
% if len(result) == 8:
%   results_coll = []
%   results_coll_diff = []
%   radius_coll_diff = []
%   for kk in [0, 2, 4, 6]:
%       results_coll.append([(result[kk][0]+result[kk+1][0])/2, (result[kk][1]+result[kk+1][1])/2])
%       results_coll_diff.append([abs(result[kk][0]-result[kk+1][0])/2, abs(result[kk][1]-result[kk+1][1])/2])
%   end
%   radius_coll = []
%   import numpy
%   for kk in range(0, len(results_coll), 1):
%       radius_coll.append(numpy.sqrt(results_coll[kk][0]*results_coll[kk][0]+results_coll[kk][1]*results_coll[kk][1]))
%       radius_coll_diff.append(numpy.sqrt(results_coll_diff[kk][0]*results_coll_diff[kk][0]+results_coll_diff[kk][1]*results_coll_diff[kk][1]))
%   end
%   CollAsymX = numpy.average(numpy.asarray(results_coll_diff)[:, 0])
%   CollAsymY = numpy.average(numpy.asarray(results_coll_diff)[:, 1])
%   if apply_tolerance_to_coll_asym == "True":
%       max_deviation = round(max(numpy.max(numpy.abs(results_coll)), numpy.max(radius_coll)), 2)
%   end
% end

% if max_deviation > pass_rate:
%   image_pass = "Failed"
% elif (max_deviation <= pass_rate) and (max_deviation> success_rate):
%   image_pass = "Borderline"
% else:
%   image_pass = "Passed"
% end

% coll_asym_pass = "Passed"
% if len(result) == 8:
%   if (CollAsymX < coll_asym_tol) and (CollAsymY < coll_asym_tol):
%       coll_asym_pass = "Passed"
%   else:
%       coll_asym_pass = "Failed"
%   end
% end

% beam_dev_pass = "Passed"
% if len(result) == 8:
%   deviation1 = (result[0][0]+result[1][0]+result[2][0]+result[3][0] +result[4][0]+result[5][0]+result[6][0]+result[7][0])/8.0
%   deviation2 = (result[0][0]+result[1][0]+result[4][0]+result[5][0])/4.0
%   if abs(deviation1) < beam_dev_tol:
%       beam_dev_pass = "Passed"
%   else:
%       beam_dev_pass = "Failed"
%   end
% elif len(result) == 4:
%   deviation1 = (result[0][0]+result[1][0]+result[2][0]+result[3][0])/4
%   deviation2 = (result[0][0] + result[2][0])/2
%   if abs(deviation1) < beam_dev_tol:
%       beam_dev_pass = "Passed"
%   else:
%       beam_dev_pass = "Failed"
%   end
% end



<ul class="nav nav-tabs nav-justified">
    <li class="active">
        <a data-toggle="pill" href="#menu1">Images</a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu2">
            Analysis
            % if image_pass=="Failed" or coll_asym_pass=="Failed" or beam_dev_pass=="Failed":
                <span class="label label-danger">Failed</span>
            % elif ("Failed" not in [image_pass, coll_asym_pass, beam_dev_pass]) and ("Borderline" in [image_pass, coll_asym_pass, beam_dev_pass]):
                <span class="label label-warning">Borderline</span>
            % else:
                <span class="label label-success">Passed</span>
            % end
        </a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu21">Diagrams</a>
    </li>
    <li>
        <a data-toggle="pill" href="#menu3">Save result</a>
    </li>
</ul>

<div class="tab-content">
    <div id="menu1" class="tab-pane fade in active">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">All images</h3>
            </div>
            <div class="panel-body">
                {{!script}}
            </div>
        </div>
    </div>
    <div id="menu2" class="tab-pane fade">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">
                    Image analysis
                    % if image_pass == "Failed":
                        <span class="label label-danger">Failed</span>
                    % elif image_pass == "Borderline":
                        <span class="label label-warning">Borderline</span>
                    % else:
                        <span class="label label-success">Passed</span>
                    % end
                </h3>
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
                    <td>{{image_numbers[k]}}</td>

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

        <br>

        % if len(result) == 8:
            <div class="panel panel-default">
                <div class="panel-heading">
                        <h3 class="panel-title">Moving the BB into the isocenter</h3>
                </div>
                    <div class="panel-body">
                            To move the BB into the isocenter the following shifts must be applied. Looking at the gantry from the foot of the couch:
                    </div>

                % lat = (-result[0][0]-result[1][0]+result[4][0]+result[5][0])/4
                % long = (result[0][1]+result[1][1]+result[2][1]+result[3][1] +result[4][1]+result[5][1]+result[6][1]+result[7][1])/8
                % vrt = (result[2][0]+result[3][0]-result[6][0]-result[7][0])/4
               
                <table class="table table-borderless">
                    <tr>
                        <td>
                            LAT
                        </td>
                        <td>
                            LONG
                        </td>
                        <td>
                            VRT
                        </td>
                    </tr>
                    
                    <tr>
                        <td>
                            {{abs(round(lat, 2))}} mm
                            % if lat > 0:
                                &rarr; RIGHT
                            % else:
                                &rarr; LEFT
                            % end
                        </td>
                        <td>
                            {{abs(round(long, 2))}} mm
                            % if long > 0:
                                &rarr; IN
                            % else:
                                &rarr; OUT
                            % end
                        </td>
                        <td>
                            {{abs(round(vrt, 2))}} mm
                            % if vrt > 0:
                                &rarr; UP
                            % else:
                                &rarr; DOWN
                            % end
                        </td>

                    </tr>
                </table>
            </div>
           
            <br>
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Beam deviation
                        % if beam_dev_pass == "Failed":
                            <span class="label label-danger">Failed</span>
                        % else:
                            <span class="label label-success">Passed</span>
                        % end
                    </h3>
                </div>
                <div class="panel-body">
                    Crossplane deviation of the beam from the ideal position. In beam's eye view:
                </div>

                
                
                <table class="table table-borderless">
                    <tr>
                        <td>
                            Average over all images
                        </td>
                        <td>
                            Average over images at gantry 0 and 180
                        </td>
                    </tr>
                    <tr>
                        <td>
                            {{abs(round(deviation1, 2))}} mm
                            % if deviation1 > 0:
                                &rarr; RIGHT
                            % else:
                                &rarr; LEFT
                            % end
                        </td>
                        <td>
                            {{abs(round(deviation2, 2))}} mm
                            % if deviation2 > 0:
                                &rarr; RIGHT
                            % else:
                                &rarr; LEFT
                            % end
                        </td>
                    </tr>
                </table>
            </div>

            <br>

            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Collimator asymmetry
                        % if coll_asym_pass == "Failed":
                            <span class='label label-danger'>Failed</span>
                        % elif coll_asym_pass == "Passed":
                            <span class='label label-success'>Passed</span>
                        % end
                    </h3>
                </div>
                <div class="panel-body">
                    &Delta;x and &Delta;y are averaged over the image pair with the same gantry angle and opposite collimator angles. 
                </div>

                <table class="table">
                    <tr>
                        <td>
                            Image
                        </td>
                        <td>
                            Average &Delta;x [mm]
                        </td>
                        <td>
                            &plusmn;&Delta;x [mm]
                        </td>

                        <td style="border-left:1px solid #CCCCCC;">
                            Average &Delta;y [mm]
                        </td>
                        <td>
                            &plusmn;&Delta;y [mm]
                        </td>

                        <td style="border-left:1px solid #CCCCCC;">
                            Average R [mm]
                        </td>

                    </tr>
                    % img = [str(image_numbers[0])+"+"+str(image_numbers[1]), str(image_numbers[2])+"+"+str(image_numbers[3]), str(image_numbers[4])+"+"+str(image_numbers[5]), str(image_numbers[6])+"+"+str(image_numbers[7])]
                    % for k in range(0, len(results_coll), 1):
                        % if abs(round(radius_coll[k], 2)) > pass_rate:
                            <tr class="danger">
                        % elif abs((round(radius_coll[k], 2)) <= pass_rate) and (abs(round(radius_coll[k], 2))> success_rate):
                            <tr class="warning">
                        % else:
                            <tr>
                        % end
                        <td>{{img[k]}}</td>
                        
                        <td>{{round(results_coll[k][0], 2)}}</td>
                        <td>{{round(results_coll_diff[k][0], 2)}}</td>

                        <td style="border-left:1px solid #CCCCCC;">{{round(results_coll[k][1], 2)}}</td>
                        <td>{{round(results_coll_diff[k][1], 2)}}</td>

                        <td style="border-left:1px solid #CCCCCC;">{{round(radius_coll[k], 2)}}</td>
                    </tr>
                    % end

                </table>
            </div>

            <br>

            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Estimated wobble</h3>
                </div>
                <div class="panel-body">
                    Max deviation:
                </div>
                <table class="table  table-borderless">
                    <tr>
                        <td>
                            Collimator
                        </td>
                        <td>
                            Gantry
                        </td>
                    </tr>
                    <tr>
                        <td>
                            {{round(max(radius_coll_diff), 2)}} mm
                        </td>
                        <td>
                            {{round(cax_wobble_max, 2)}} mm
                        </td>
                    </tr>

                </table>
            </div>

        % elif len(result) == 4:

            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Moving the BB into the isocenter</h3>
                </div>
                <div class="panel-body">
                    To move the BB into the isocenter the following shifts must be applied. Looking at the gantry from the foot of the couch:
                </div>

                % lat = (-result[0][0]+result[2][0])/2
                % long = (result[0][1]+result[1][1]+result[2][1]+result[3][1])/4
                % vrt = (result[1][0]-result[3][0])/2
            
                <table class="table table-borderless">
                    <tr>
                        <td>
                            LAT
                        </td>
                        <td>
                            LONG
                        </td>
                        <td>
                            VRT
                        </td>
                    </tr>
                    
                    <tr>
                        <td>
                            {{abs(round(lat, 2))}} mm
                            % if lat > 0:
                                &rarr; RIGHT
                            % else:
                                &rarr; LEFT
                            % end
                        </td>
                        <td>
                            {{abs(round(long, 2))}} mm
                            % if long > 0:
                                &rarr; IN
                            % else:
                                &rarr; OUT
                            % end
                        </td>
                        <td>
                            {{abs(round(vrt, 2))}} mm
                            % if vrt > 0:
                                &rarr; UP
                            % else:
                                &rarr; DOWN
                            % end
                        </td>
                    </tr>
                </table>
            </div>

            <br>

            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Beam deviation
                        % if beam_dev_pass == "Failed":
                            <span class="label label-danger">Failed</span>
                        % else:
                            <span class="label label-success">Passed</span>
                        % end
                    </h3>
                </div>
                <div class="panel-body">
                    Crossplane deviation of the beam from the ideal position. In beam's eye view:
                </div>

                <table class="table table-borderless">
                    <tr>
                        <td>
                            Average over all images
                        </td>
                        <td>
                            Average over images at gantry 0 and 180
                        </td>
                    </tr>
                    <tr>
                        <td>
                            {{abs(round(deviation1, 2))}} mm
                            % if deviation1 > 0:
                                &rarr; RIGHT
                            % else:
                                &rarr; LEFT
                            % end
                        </td>
                        <td>
                            {{abs(round(deviation2, 2))}} mm
                            % if deviation2 > 0:
                                &rarr; RIGHT
                            % else:
                                &rarr; LEFT
                            % end
                        </td>
                    </tr>
                </table>
            </div>

            <br>

            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Estimated wobble</h3>
                </div>
                <div class="panel-body">
                    Max deviation:
                </div>
                <table class="table  table-borderless">
                    <tr>
                        <td>
                            Gantry
                        </td>
                    </tr>
                    <tr>
                        <td>
                            {{round(cax_wobble_max, 2)}} mm
                        </td>
                    </tr>

                </table>
            </div>
        % end
        
        <br>

        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">EPID center</h3>
            </div>
            <div class="panel-body">
                Average position with respect to CAX:
            </div>
            <table class="table table-borderless">
                <tr>
                    <td>
                        X
                    </td>
                    <td>
                        Y
                    </td>
                </tr>
                <tr>
                    <td>
                        {{round(epid2cax_dev_avg[0], 2)}} mm
                    </td>
                    <td>
                        {{round(epid2cax_dev_avg[1], 2)}} mm
                    </td>
                </tr>
            </table>
        </div>

        <br>

        <div class="alert alert-info" role="alert">
            The following SIDs were detected [mm]:
            % for t in range(0, len(SIDs), 1):
                {{round(SIDs[t], 2)}},&#32;
            % end
        </div>

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
            % if len(result)==8:
                var json_data = {"User": "{{save_results["displayname"]}}",
                                 "Machine": $('#machines').val(),
                                 "Beam": $('#energies').val(),
                                 "Phantom": $('#phantom').val(),
                                 "Datetime": "{{acquisition_datetime}}",
                                 "TestType": "Default",
                                 "BBshiftX": "{{round(lat, 2)}}",
                                 "BBshiftY": "{{round(long, 2)}}",
                                 "BBshiftZ": "{{round(vrt, 2)}}",
                                 "BeamDeviation": "{{round(deviation1, 2)}}",
                                 "CollAsymX": "{{round(CollAsymX, 2)}}",
                                 "CollAsymY": "{{round(CollAsymY, 2)}}",
                                 "WobbleColl": "{{round(max(radius_coll_diff), 2)}}",
                                 "WobbleGnt": "{{round(cax_wobble_max, 2)}}",
                                 "EpidDevX": "{{round(epid2cax_dev_avg[0], 2)}}",
                                 "EpidDevY": "{{round(epid2cax_dev_avg[1], 2)}}",
                                 "RadiusMax": "{{round(max(radius), 2)}}",
                                 "Comment": $('#comment').val()
                                };
            % elif len(result)==4:
                var json_data = {"User": "{{save_results["displayname"]}}",
                                 "Machine": $('#machines').val(),
                                 "Beam": $('#energies').val(),
                                 "Phantom": $('#phantom').val(),
                                 "Datetime": "{{acquisition_datetime}}",
                                 "TestType": "Default",
                                 "BBshiftX": "{{round(lat, 2)}}",
                                 "BBshiftY": "{{round(long, 2)}}",
                                 "BBshiftZ": "{{round(vrt, 2)}}",
                                 "BeamDeviation": "{{round(deviation1, 2)}}",
                                 "WobbleGnt": "{{round(cax_wobble_max, 2)}}",
                                 "EpidDevX": "{{round(epid2cax_dev_avg[0], 2)}}",
                                 "EpidDevY": "{{round(epid2cax_dev_avg[1], 2)}}",
                                 "RadiusMax": "{{round(max(radius), 2)}}",
                                 "Comment": $('#comment').val()
                                };
            % else:
                var json_data = {};
            % end
            
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