<!DOCTYPE html>
<html lang="en">

<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Dynalog histograms</title>
	<style>
		body {

			background-color: #f5f5f5;
		}
		td {
			text-align: center;
		}
		table {
			border-spacing: 15px 2px;

		}
	</style>
	
	<link rel="stylesheet" href="{{bokeh_file_css}}" type="text/css" />
	<script type="text/javascript" src="{{bokeh_file_js}}"></script>
	<link rel="stylesheet" href="{{bokeh_widgets_css}}" type="text/css" />
	<script type="text/javascript" src="{{bokeh_widgets_js}}"></script>
	<script type="text/javascript">Bokeh.set_log_level("info");</script>

	{{!script}}

</head>
<h2>Histograms for dates between {{date}} and {{date2}} (inclusive)</h2>
<body>
	{{!div}}
	<br>
</body>
</html>