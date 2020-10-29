<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Catphan results</title>
    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <script src="/bootstrap/js/jquery.min.js"></script>
    <script src="/bootstrap/js/bootstrap.min.js"></script>
    <link href="/css/module_result.css" rel="stylesheet">
</head>

<body>

    <ul class="nav nav-tabs nav-justified">
        <li class="active"><a data-toggle="pill" href="#menu1">
            CTP404
            % if passed_404 == False:
                <span class='label label-danger'>Failed</span>
            % else:
                <span class='label label-success'>Passed</span>
            % end
        </a></li>
        <li ><a data-toggle="pill" href="#menu2">
            CTP528
            % if mtf_passing == False:
                <span class='label label-danger'>Failed</span>
            % elif mtf_passing == True:
                <span class='label label-success'>Passed</span>
            % end
        </a></li>
        <li><a data-toggle="pill" href="#menu3">
            CTP486
            % if passed_uniformity == False or passed_uniformity_index == False:
                <span class='label label-danger'>Failed</span>
            % else:
                <span class='label label-success'>Passed</span>
            % end
        </a></li>
        % if show_ctp515 == True:
            <li><a data-toggle="pill" href="#menu4">
                CTP515
            % if ctp515_passed == False:
                <span class='label label-danger'>Failed</span>
            % else:
                <span class='label label-success'>Passed</span>
            % end
            </a></li>
        % end
        <li>
            <a data-toggle="pill" href="#menu5">Save results</a>
        </li>
    </ul>
    <div class="tab-content">

        <div id="menu1" class="tab-pane fade in active">
            {{!script_404}}
            {{!script_404_HU}}

            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        HU values
                        % if passed_HU == False:
                            <span class='label label-danger'>Failed</span>
                        % elif passed_HU == True:
                            <span class='label label-success'>Passed</span>
                        % end

                    </h3>
                </div>
                <div class="panel-body">
                    Collection of measured HU values.
                </div>
                <table class="table">
                    <tr>
                        <td colspan="2" style="border-left:1px solid #CCCCCC;"></td>
                        <td colspan="4" style="border-left:1px solid #CCCCCC;">Reference</td>
                        <td colspan="4" style="border-left:1px solid #CCCCCC;">Current</td>
                    </tr>
                    <tr>
                        <td>
                            <strong>Material</strong>
                        </td>
                        <td>
                            <strong>HU nom.</strong>
                        </td>
                        <td style="border-left:1px solid #CCCCCC;">
                            <strong>HU median</strong>
                        </td>
                        <td>
                            <strong>HU diff.</strong>
                        </td>
                        <td>
                            <strong>HU std</strong>
                        </td>
                        <td>
                            <strong>CNR</strong>
                        </td>
                        <td style="border-left:1px solid #CCCCCC;">
                            <strong>HU median</strong>
                        </td>
                        <td>
                            <strong>HU diff.</strong>
                        </td>
                        <td>
                            <strong>HU std</strong>
                        </td>
                        <td>
                            <strong>CNR</strong>
                        </td>

                    </tr>
                    % for row in range(len(HU_values_ref)):
                        <tr>
                            <td>{{HU_names[row]}}</td>
                            <td>{{HU_nominal[row]}}</td>
                            <td style="border-left:1px solid #CCCCCC;">{{HU_values_ref[row]}}</td>
                            <td>{{HU_diff_ref[row]}}</td>
                            <td>{{HU_std_ref[row]}}</td>
                            <td>{{cnrs404_ref[row]}}</td>
                            <td style="border-left:1px solid #CCCCCC;">{{HU_values[row]}}</td>
                            <td>{{HU_diff[row]}}</td>
                            <td>{{HU_std[row]}}</td>
                            <td>{{cnrs404[row]}}</td>
                        </tr>
                    % end
                </table>
            </div>
            <div class="panel panel-default">
                <div class="panel-heading">
                  <h3 class="panel-title">

                        Low contrast visibility
                        % if passed_lcv == False:
                            <span class='label label-danger'>Failed</span>
                        % elif passed_lcv == True:
                            <span class='label label-success'>Passed</span>
                        % end
                    </h3>
                </div>
                <div class="panel-body">

                    <table class="table">
                        <tr>
                            <td>
                            </td>
                            <td>
                                Reference
                            </td>
                            <td>
                                Current
                            </td>
                        </tr>
                        <tr>
                            <td>
                                LCV
                            </td>
                            <td>
                                {{lcv_ref}}
                            </td>
                            <td>
                                {{lcv}}
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <div class="panel panel-default">
                <div class="panel-heading">
                  <h3 class="panel-title">
                        Slice thickness
                        % if passed_thickness == False:
                            <span class='label label-danger'>Failed</span>
                        % elif passed_thickness == True:
                            <span class='label label-success'>Passed</span>
                        % end
                </h3>
                </div>
                <div class="panel-body">

                    <table class="table">
                        <tr>
                            <td>
                            </td>
                            <td>
                                Reference
                            </td>
                            <td>
                                Current
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Measured slice thickness [mm]
                            </td>
                            <td>
                                {{slice_thickness_ref}}
                            </td>
                            <td>
                                {{slice_thickness}}
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Nominal slice thickness [mm]
                            </td>
                            <td>
                                {{dicom_slice_thickness_ref}}
                            </td>
                            <td>
                                {{dicom_slice_thickness}}
                            </td>
                        </tr>
                    </table>
                </div>
            </div>    
            <div class="panel panel-default">
                <div class="panel-heading">
                  <h3 class="panel-title">
                        Scaling
                        % if passed_geometry == False:
                            <span class='label label-danger'>Failed</span>
                        % elif passed_geometry == True:
                            <span class='label label-success'>Passed</span>
                        % end
                    </h3>
                </div>
                <div class="panel-body">

                    <table class="table">
                        <tr>
                            <td>
                            </td>
                            <td>
                                Reference
                            </td>
                            <td>
                                Current
                            </td>
                        </tr>
                        % for row in range(len(lines)):
                            <tr>
                                <td>Line {{row+1}} length [mm]</td>
                                <td>{{lines_ref[row]}}</td>
                                <td>{{lines[row]}}</td>
                            </tr>
                        % end
                        <tr>
                            <td>
                                Average line length [mm]
                            </td>
                            <td>
                                {{lines_avg_ref}}
                            </td>
                            <td>
                                {{lines_avg}}
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <div class="panel panel-default">
                <div class="panel-heading">
                  <h3 class="panel-title">
                    Geometry
                </h3>
                </div>
                <div class="panel-body">

                    <table class="table">
                        <tr>
                            <td>
                            </td>
                            <td>
                                Reference
                            </td>
                            <td>
                                Current
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Phantom roll [degrees]
                            </td>
                            <td>
                                {{phantom_roll_ref}}
                            </td>
                            <td>
                                {{phantom_roll}}
                            </td>
                        </tr>
                        <tr>
                            <td>
                                CTP404 center [px]
                            </td>
                            <td>
                                {{phantom_center_ref}}
                            </td>
                            <td>
                                {{phantom_center}}
                            </td>
                        </tr>
                        <tr>
                            <td>
                                CTP404 (origin) slice
                            </td>
                            <td>
                                {{origin_slice_ref}}
                            </td>
                            <td>
                                {{origin_slice}}
                            </td>
                        </tr>
                        <tr>
                            <td>
                                CTP528 slice
                            </td>
                            <td>
                                {{ctp528_slice_ref}}
                            </td>
                            <td>
                                {{ctp528_slice}}
                            </td>
                        </tr>
                        <tr>
                            <td>
                                CTP486 slice
                            </td>
                            <td>
                                {{ctp486_slice_ref}}
                            </td>
                            <td>
                                {{ctp486_slice}}
                            </td>
                        </tr>
                        % if save_results["phantom"] != "Catphan 503":
                            <tr>
                                <td>
                                    CTP515 slice
                                </td>
                                <td>
                                    {{ctp515_slice_ref}}
                                </td>
                                <td>
                                    {{ctp515_slice}}
                                </td>
                            </tr>
                        % end
                        <tr>
                            <td>
                                mm per pixel
                            </td>
                            <td>
                                {{mm_per_pixel_ref}}
                            </td>
                            <td>
                                {{mm_per_pixel}}
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        <div id="menu2" class="tab-pane fade">

            {{!script_ctp528}}

            {{!script_ctp528mtf}}

            <p>
                <table class="table">
                    <tr>
                        <td>
                        </td>
                        <td>
                           Reference [lp/mm]
                        </td>
                        <td>
                           Current [lp/mm]
                        </td>
                        <td>
                           Difference [%]
                        </td>
                    </tr>
                    <tr>
                        <td>
                            MTF 30%
                        </td>
                        <td>
                            {{mtf30_ref}}
                        </td>
                        <td>
                            {{mtf30}}
                        </td>
                        <td>
                            {{round(100*(mtf30-mtf30_ref)/mtf30_ref, 1)}}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            MTF 50%
                        </td>
                        <td>
                            {{mtf50_ref}}
                        </td>
                        <td>
                            {{mtf50}}
                        </td>
                        <td>
                            {{round(100*(mtf50-mtf50_ref)/mtf50_ref, 1)}}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            MTF 80%
                        </td>
                        <td>
                            {{mtf80_ref}}
                        </td>
                        <td>
                            {{mtf80}}
                        </td>
                        <td>
                            {{round(100*(mtf80-mtf80_ref)/mtf80_ref, 1)}}
                        </td>
                    </tr>

                </table>
            </p>

        </div>
        <div id="menu3" class="tab-pane fade">
            <p>
                {{!script_486}}
                {{!script_486_profile}}
            </p>

            <div class="panel panel-default">
                <div class="panel-heading">
                  <h3 class="panel-title">
                        Uniformity index
                        % if passed_uniformity_index == False:
                            <span class='label label-danger'>Failed</span>
                        % elif passed_uniformity_index == True:
                            <span class='label label-success'>Passed</span>
                        % end
                    </h3>
                </div>
                <div class="panel-body">
                    <table class="table">
                        <tr>
                            <td>
                            </td>
                            <td>
                                Reference
                            </td>
                            <td>
                                Current
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Uniformity index [%]
                            </td>
                            <td>
                                {{uidx_ref}}
                            </td>
                            <td>
                                {{uidx}}
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <div class="panel panel-default">
                <div class="panel-heading">
                  <h3 class="panel-title">
                        Absolute values
                        % if passed_uniformity == False:
                            <span class='label label-danger'>Failed</span>
                        % elif passed_uniformity == True:
                            <span class='label label-success'>Passed</span>
                        % end
                    </h3>
                </div>
                <div class="panel-body">
                    <table class="table">
                        <tr>
                            <td>
                            </td>
                            <td>
                                Reference
                            </td>
                            <td>
                                Current
                            </td>
                        </tr>
                        % for row in range(len(hvalues)):
                            <tr>
                                <td>
                                    ROI {{row}} [HU]
                                </td>
                                <td>
                                    {{hvalues_ref[row]}}
                                </td>
                                <td>
                                    {{hvalues[row]}}
                                </td>
                            </tr>
                        % end
                    </table>
                </div>
            </div>
        </div>
        % if show_ctp515 == True:
            <div id="menu4" class="tab-pane fade">
                <p>
                    {{!script_515}}
                    {{!script_515_contrast}}
                </p>
                <table class = "table">
                    <tr>
                        <td></td>
                        <td>Reference</td>
                        <td>Current</td>
                    </tr>
                    <tr>
                        <td>Num of visible ROIs</td>
                        <td>{{ctp515_visible_ref}}</td>
                        <td>{{ctp515_visible}}</td>
                    </tr>
                </table>

                <div class="panel panel-default">
                    <div class="panel-heading">
                      <h3 class="panel-title">
                        CNR constant (CNR * diameter)
                    </h3>
                    </div>
                    <div class="panel-body">
                        <table class="table">
                            <tr>
                                <td>
                                    ROI [mm]
                                </td>
                                <td>
                                    Reference CNR constant
                                </td>
                                <td>
                                    Current CNR constant
                                </td>
                            </tr>
                            % for rr in range(len(cnrs515)):
                            <tr>
                                <td>
                                    {{cnrs_names[rr]}}
                                </td>
                                <td>
                                    {{cnrs515_ref[rr]}}
                                </td>
                                <td>
                                    {{cnrs515[rr]}}
                                </td>
                            </tr>
                            % end
                            <tr>
                                <td>Average</td>
                                <td>{{round(sum(cnrs515_ref)/len(cnrs515_ref), 2)}}</td>
                                <td>{{round(sum(cnrs515)/len(cnrs515), 2)}}</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        % end

        <div id="menu5" class="tab-pane fade">
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
        $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
            var iframe = parent.document.getElementById('receiver2');
            parent.resizeIFrameToFitContent(iframe);
        });

        function save_to_database(){
            var formData = new FormData();
            var phantom = $('#phantom').val();
            var HU_CNR_values_dict = {{!save_results["HU_CNR_values_dict"]}};

            var json_data = {"User": "{{save_results['displayname']}}",
                             "Machine": $('#machines').val(),
                             "Beam": $('#energies').val(),
                             "Phantom": phantom,
                             "Datetime": "{{acquisition_datetime}}",
                             "Comment": $('#comment').val(),
                             
                             "Air_HU": HU_CNR_values_dict['Air'][0],
                             "PMP_HU": HU_CNR_values_dict['PMP'][0],
                             "LDPE_HU": HU_CNR_values_dict['LDPE'][0],
                             "Poly_HU": HU_CNR_values_dict['Poly'][0],
                             "Acrylic_HU": HU_CNR_values_dict['Acrylic'][0],
                             "Delrin_HU": HU_CNR_values_dict['Delrin'][0],
                             "Teflon_HU": HU_CNR_values_dict['Teflon'][0],

                             "Air_CNR": HU_CNR_values_dict['Air'][1],
                             "PMP_CNR": HU_CNR_values_dict['PMP'][1],
                             "LDPE_CNR": HU_CNR_values_dict['LDPE'][1],
                             "Poly_CNR": HU_CNR_values_dict['Poly'][1],
                             "Acrylic_CNR": HU_CNR_values_dict['Acrylic'][1],
                             "Delrin_CNR": HU_CNR_values_dict['Delrin'][1],
                             "Teflon_CNR": HU_CNR_values_dict['Teflon'][1],

                             "MTF30": "{{mtf30}}",
                             "MTF50": "{{mtf50}}",
                             "MTF80": "{{mtf80}}",
                             "LCV": "{{lcv}}",
                             "SliceThickness": "{{slice_thickness}}",
                             "Scaling": "{{lines_avg}}",
                             "PhantomRoll": "{{phantom_roll}}",
                             "PhantomCenterX": "{{phantom_center[0]}}",
                             "PhantomCenterY": "{{phantom_center[1]}}",
                             "OriginSlice": "{{origin_slice}}",
                             "mm_per_pixel": "{{mm_per_pixel}}",
                             "UniformityIndex": "{{uidx}}",
                             "UniformityAbsoluteValue": "{{sum(hvalues)/len(hvalues)}}"
                            };

            % if save_results["phantom"] == "Catphan 604":
                json_data["Bone50_HU"] = HU_CNR_values_dict['50% Bone'][0];
                json_data["Bone20_HU"] = HU_CNR_values_dict['20% Bone'][0];
                json_data["Bone50_CNR"] = HU_CNR_values_dict['50% Bone'][1];
                json_data["Bone20_CNR"] = HU_CNR_values_dict['20% Bone'][1];
            % end

            % if save_results["phantom"] != "Catphan 503":
                json_data["LowContrastROIsSeen"] = "{{ctp515_visible}}";
                json_data["LowContrastCNR"] = "{{round(sum(cnrs515)/len(cnrs515), 2)}}";
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
            xmlhttp.open("POST", "/save_catphan", true);
            xmlhttp.send(formData);
            document.getElementById("save_button").disabled = true;
            document.getElementById("save_error").innerHTML = "Working on it ... ";
        }


    </script>
</body>
</html>