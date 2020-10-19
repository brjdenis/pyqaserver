<!DOCTYPE html>
<html lang="en">

<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Dynalog report</title>
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
	<h2>Records between {{date}} and {{date2}}</h2>
	<p>
		<ul>
			<li>
				Snaps - number of snapshots (taken at 50 ms interval),
			</li>
			<li>
				Holds - number of beam holds,
			</li>
			<li>
				RMSmax2 [mm]-  maximum RMS of the difference between planned and actual positions of leaves evaluated for those snapshots when beam was ON and there was no beam hold,
			</li>
			<li>
				DIFFmax2 [mm] - maximum absolute difference between planned and actual positions of leaves evaluated for those snapshots when beam was ON and there was no beam hold.
			</li>
		</ul>
		
	</p>
	<table>
		<tr>
			<td style="border-bottom:1px solid black">Patient</td>
			<td style="border-bottom:1px solid black">Folder</td>
			<td style="border-bottom:1px solid black">Beam</td>
			<td style="border-bottom:1px solid black">Gantry</td>
			<td style="border-bottom:1px solid black">Date</td>
			<td style="border-bottom:1px solid black">Time</td>
			<td style="border-bottom:1px solid black">Snaps</td>
			<td style="border-bottom:1px solid black">Holds</td>
			<td style="border-bottom:1px solid black">RMSmax2</td>
			<td style="border-bottom:1px solid black">DIFFmax2</td>
			<td style="border-bottom:1px solid black">GammaAvg</td>
			<td style="border-bottom:1px solid black">GammaIndex</td>
		</tr>
		% current_patient="" if len(data)==0 else data[0][0]
		% for k in data:
			% if k[0] != current_patient:
				<tr>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
					<td style="border-bottom:1px solid black"></td>
				</tr>
				<tr>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
					<td></td>
				</tr>
			% current_patient = k[0]
			% end
		% if k[9] >=0.21:
			<tr style="background-color:#ffcc99">
		% else:
			<tr>
		% end
			<td>{{k[0]}}</td>
			<td>{{k[1]}}</td>
			<td>{{k[2]}}</td>
			<td>{{k[3]}}</td>
			<td>{{k[4]}}</td>
			<td>{{k[5]}}</td>
			<td>{{k[6]}}</td>
			<td>{{k[7]}}</td>
			<td>{{k[8]}}</td>
			<td>{{k[9]}}</td>
			<td>{{k[10]}}</td>
			<td>{{k[11]}}</td>
		</tr>
		% end
	</table>

</body>



</html>