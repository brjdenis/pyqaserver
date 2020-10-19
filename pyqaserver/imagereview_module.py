import sys
import os
import json
from multiprocessing import Pool
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import gridplot 
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumberFormatter, BoxSelectTool, DataTable, TableColumn, LinearColorMapper
from bokeh.models.widgets import RangeSlider
from bokeh.events import SelectionGeometry
import matplotlib

from pylinac.core import image as pylinac_image

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    import general_functions
    import RestToolbox_modified as RestToolbox
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

#  Global filepaths for bokeh import
BOKEH_FILE_CSS = config.BOKEH_FILE_CSS
BOKEH_FILE_JS = config.BOKEH_FILE_JS
BOKEH_WIDGETS_CSS = config.BOKEH_WIDGETS_CSS
BOKEH_WIDGETS_JS = config.BOKEH_WIDGETS_JS
BOKEH_TABLES_CSS = config.BOKEH_TABLES_CSS
BOKEH_TABLES_JS = config.BOKEH_TABLES_JS

# Url to some mpld3 library
D3_URL = config.D3_URL
MPLD3_URL = config.MPLD3_URL

# Working directory
PLWEB_FOLDER = config.PLWEB_FOLDER

PI = np.pi

# Here starts the bottle server
imgreview_app = Bottle()

@imgreview_app.route(PLWEB_FOLDER + '/image_review', method="POST")
def image_review():

    colormaps = ["Greys", "gray", "brg", "prism"]
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect(PLWEB_FOLDER + "/login")
    try:
        variables = general_functions.Read_from_dcm_database()
        variables["colormaps"] = colormaps
        variables["displayname"] = displayname
        response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is refusing connection.",
                                           "plweb_folder": PLWEB_FOLDER})
    return template("image_review", variables)

def image_review_helperf_catch_error(args):
    try:
        return image_review_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e),
                                           "plweb_folder": PLWEB_FOLDER})
    
    
def image_review_helperf(args):
    converthu = args["converthu"]
    invert = args["invert"]
    calculate_histogram = args["calculate_histogram"]
    colormap = args["colormap"]
    w = args["w"]
    general_functions.set_configuration(args["config"])
    
    temp_folder, file_path = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w)
    try:
        img = pylinac_image.DicomImage(file_path)
        if invert:
            img.invert()
        if converthu:  # Convert back to pixel values if needed.
            img.array = (img.array - int(img.metadata.RescaleIntercept)) / int(img.metadata.RescaleSlope)
        img_array = np.flipud(img.array)
    except:
        return template("error_template", {"error_message": "Cannot read image.",
                                           "plweb_folder": PLWEB_FOLDER})
    size_x = img_array.shape[1]
    size_y = img_array.shape[0]
    img_min = np.min(img_array)
    img_max = np.max(img_array)

    x1 = np.arange(0, size_x, 1).tolist()
    y1 = img_array[int(size_y//2), :].tolist()
    y2 = np.arange(0, size_y, 1).tolist()
    x2 = img_array[:, int(size_x//2)].tolist()
    
    source = ColumnDataSource(data=dict(x1=x1, y1=y1))  # Bottom plot
    source2 = ColumnDataSource(data=dict(x2=x2, y2=y2))  # Right plot
    sourcebp = ColumnDataSource(data=dict(xbp=[], ybp=[]))
    sourcerp = ColumnDataSource(data=dict(xrp=[], yrp=[]))

    # Add table for pixel position and pixel value
    hfmt = NumberFormatter(format="0.00")
    source6 = ColumnDataSource(dict(
                                x=[],
                                y=[],
                                value=[]
                                ))
    columns2 = [TableColumn(field="x", title="x", formatter=hfmt),
               TableColumn(field="y", title="y", formatter=hfmt),
               TableColumn(field="value", title="value", formatter=hfmt)]
    table2 = DataTable(source=source6, columns=columns2, editable=False, height=50, width = 220)


    # Plotting profiles
    callback = CustomJS(args=dict(source=source, source2=source2, sourcebp=sourcebp,
                                  sourcerp=sourcerp, source6=source6), code="""
        var geometry = cb_data['geometry'];
        var x_data = parseInt(geometry.x); // current mouse x position in plot coordinates
        var y_data = parseInt(geometry.y); // current mouse y position in plot coordinates
        var data = source.data;
        var data2 = source2.data;
        var array = """+json.dumps(img_array.tolist())+""";
        data['y1'] = array[y_data];
        var column = [];
        for(var i=0; i < array.length; i++){
          column.push(array[i][x_data]);
        }
        data2['x2'] = column;
        
        source.change.emit();
        source2.change.emit();
        
        var length_x = array[0].length;
        var length_y = array.length;

        if ((x_data<=length_x && x_data>=0)  && (y_data<=length_y && y_data>=0)){
            
            // Add points to plot:
            sourcebp.data['xbp'] = [x_data];
            sourcebp.data['ybp'] = [array[y_data][x_data]];
            sourcerp.data['xrp'] = [array[y_data][x_data]];
            sourcerp.data['yrp'] = [y_data];
            
            // Get position and pixel value for table
            source6.data["x"] = [geometry.x];
            source6.data["y"] = [geometry.y];
            source6.data["value"] = [array[y_data][x_data]];

            sourcebp.change.emit();
            sourcerp.change.emit();
            source6.change.emit();
            }
    """)

    # Add callback for calculating average value inside Rectangular ROI
    x3 = np.arange(0, size_x, 1).tolist()
    y3 = np.arange(0, size_y, 1).tolist()
    source3 = ColumnDataSource(data=dict(x3=x3, y3=y3))
    source4 = ColumnDataSource(data=dict(x4=[], y4=[], width4=[], height4=[]))
    # Add table for mean and std
    source5 = ColumnDataSource(dict(
                                mean=[],
                                median=[],
                                std=[],
                                minn=[],
                                maxx=[]
                                ))

    columns = [TableColumn(field="mean", title="mean", formatter=hfmt),
               TableColumn(field="median", title="median", formatter=hfmt),
               TableColumn(field="std", title="std", formatter=hfmt),
               TableColumn(field="minn", title="min", formatter=hfmt),
               TableColumn(field="maxx", title="max", formatter=hfmt)]
    table = DataTable(source=source5, columns=columns, editable=False, height=50, width = 480)

    # Calculate things within ROI
    callback2 = CustomJS(args=dict(source3=source3, source4=source4, source5=source5), code="""
        var geometry = cb_obj['geometry'];
        var data3 = source3.data;
        var data4 = source4.data;
        var data5 = source5.data;

        // Get data
        var x0 = parseInt(geometry['x0']);
        var x1 = parseInt(geometry['x1']);
        var y0 = parseInt(geometry['y0']);
        var y1 = parseInt(geometry['y1']);

        // calculate Rect attributes
        var width = x1 - x0;
        var height = y1 - y0;
        var x = x0 + width/2;
        var y = y0 + height/2;

        // update data source with new Rect attributes
        data4['x4'] = [x];
        data4['y4'] = [y];
        data4['width4'] = [width];
        data4['height4'] = [height];

        // Get average value inside ROI
        var array = """+json.dumps(img_array.tolist())+""";

        var length_x = array[0].length;
        var length_y = array.length;

        if ((x0<=length_x && x0>=0) && (x1<=length_x && x1>=0) && (y0<=length_y && y0>=0) && (y1<=length_y && y1>=0)){
            var avg_ROI = [];

            for (var i=y0; i< y1; i++){
                for (var j=x0; j<x1; j++){
                    avg_ROI.push(array[i][j]);
                }
            }
    
            if (avg_ROI == undefined || avg_ROI.length==0){
                data5["mean"] = [0];
                data5["median"] = [0];
                data5["std"] = [0];
                }
            else{
                data5["mean"] = [math.mean(avg_ROI)];
                data5["median"] = [math.median(avg_ROI)];
                data5["std"] = [math.std(avg_ROI, 'uncorrected')];
                data5["maxx"] = [math.max(avg_ROI)];
                data5["minn"] = [math.min(avg_ROI)];
                }
            
            source4.change.emit();
            source5.change.emit();
            }
    """)

    plot_width = 500
    plot_height = int((plot_width-20)*size_y/size_x)
    
    fig = figure(x_range=[0, size_x], y_range=[0, size_y],
                 plot_width=plot_width, plot_height=plot_height, title="",
                 toolbar_location="right",
                 tools=["crosshair, wheel_zoom, pan, reset"])
    fig_r = figure(x_range=[img_min, img_max], y_range=fig.y_range,
                 plot_width=250, plot_height=plot_height, title="",
                 toolbar_location="right",
                 tools=[])
    fig_b = figure(x_range=fig.x_range, y_range=[img_min, img_max],
                 plot_width=plot_width, plot_height=200, title="",
                 toolbar_location="right",
                 tools=[])

    # Define matplotlib palette and make it possible to be used dynamically.
    cmap = matplotlib.cm.get_cmap(colormap) #chose any matplotlib colormap here
    bokehpalette = [matplotlib.colors.rgb2hex(m) for m in cmap(np.arange(cmap.N)[::-1])]  # Reversed direction of colormap
    mapper = LinearColorMapper(palette=bokehpalette, low=np.min(img_array), high=np.max(img_array))

    callback3 = CustomJS(args=dict(mapper=mapper, x_range=fig_r.x_range, y_range=fig_b.y_range), code="""
           mapper.palette = """+json.dumps(bokehpalette)+""";
           var start = cb_obj.value[0];
           var end = cb_obj.value[1];
           mapper.low = start;
           mapper.high = end;
           x_range.setv({"start": start, "end": end});
           y_range.setv({"start": start, "end": end});
           //mapper.change.emit();
    """)

    range_slider = RangeSlider(start=np.min(img_array), end=np.max(img_array), value=(np.min(img_array), np.max(img_array)), step=10, title="Level")
    range_slider.js_on_change('value', callback3)

    fig.image([img_array], x=0, y=0, dw=size_x, dh=size_y, color_mapper=mapper)

    fig_b.line(x='x1', y='y1', source=source)
    fig_r.line(x='x2', y='y2', source=source2)
    fig_b.circle(x='xbp', y='ybp', source=sourcebp, size=7, fill_color="red", fill_alpha=0.5, line_color=None) # For point connected to crosshair
    fig_r.circle(x='xrp', y='yrp', source=sourcerp, size=7, fill_color="red", fill_alpha=0.5, line_color=None) # For point connected to crosshair
    fig.rect(x='x4', y='y4', width='width4', height='height4', source=source4, fill_alpha=0.3, fill_color='#009933')
    
    fig.add_tools(HoverTool(tooltips=None, callback=callback))
    fig.add_tools(BoxSelectTool())
    fig.js_on_event(SelectionGeometry, callback2)  # Add event_callback to Boxselecttool

    grid = gridplot([[table, range_slider],  [fig, fig_r], [fig_b, table2]])
    script, div = components(grid)
    
    # Calculate pixel value histogram
    if calculate_histogram:
        try:
            bitsstored = int(img.metadata.BitsStored)
        except:
            bitsstored = 16
        max_pixelvalue = 2**bitsstored-1
        counts, bins = np.histogram(img_array.flatten(), density=False, range=(0, max_pixelvalue), bins=max_pixelvalue+1)
    
        fig_hist = figure(x_range = [-100, max_pixelvalue*1.05], y_range=[0.5, np.max(counts)],
                         plot_width=750, plot_height=400, title="Pixel value histogram", y_axis_type="log",
                         toolbar_location="right", tools=["box_zoom, pan, reset"])
    
        fig_hist.quad(top=counts, bottom=0.5, left=bins[:-1], right=bins[1:], alpha=0.5)
        fig_hist.grid.visible = False
        fig_hist.yaxis.axis_label = "Pixel Count"
        fig_hist.xaxis.axis_label = "Pixel Value"
        script_hist, div_hist = components(fig_hist)
    else:
        script_hist, div_hist = ["", ""]
    
    variables = {"script": script,
                 "div": div,
                 "bokeh_file_css": BOKEH_FILE_CSS,
                 "bokeh_file_js": BOKEH_FILE_JS,
                 "bokeh_widgets_js": BOKEH_WIDGETS_JS,
                 "bokeh_tables_js": BOKEH_TABLES_JS,
                 "script_hist": script_hist,
                 "div_hist": div_hist
                 }
    #gc.collect()

    general_functions.delete_files_in_subfolders([temp_folder]) # Delete image
    return template("image_review_results", variables)

@imgreview_app.route(PLWEB_FOLDER + '/image_review_calculate/<w>', method="POST")
def image_review_calculate(w):
    #Function that returns the profiles of the image
    # w is the image
    converthu = True if request.forms.hidden_converthu=="true" else False
    invert = True if request.forms.hidden_invert=="true" else False
    calculate_histogram = True if request.forms.hidden_histogram=="true" else False
    colormap = request.forms.hidden_colormap
    
    args = {"converthu": converthu, "invert": invert, "calculate_histogram": calculate_histogram,
            "colormap":colormap, "w":w, "config": general_functions.get_configuration()}
    p = Pool(1)
    data = p.map(image_review_helperf_catch_error, [args])
    p.close()
    p.join()
    return data