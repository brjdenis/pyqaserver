<!DOCTYPE html>
<html lang="en">

<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Dynalog uploads</title>
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
</head>


<body>
	<h2>Records uploaded</h2>
	<table>
		<tr>
			<td>Date uploaded</td>
		</tr>
		% for k in data:
			<tr>
				<td>{{k[0]}}</td>
			</tr>
		% end
	</table>

</body>



</html>