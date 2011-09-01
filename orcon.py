import re, urllib2

data = []

a = urllib2.urlopen('http://games.orcon.net.nz/index.php?page=steam_content').read()

start = """
<html>
<head>
<style type="text/css">
	table.table {
		width: 580px;
		background-color: #fafafa;
		border: 1px #000000 solid;
		border-collapse: collapse;
		border-spacing: 0px;
	}
	
	
	td.header {
	background-color: #99CCCC;
	border: 1px #000000 solid;
	font-family: Verdana;
	font-weight: bold;
	font-size: 12px;
	color: #404040;
	}
	
	td.game-table-cell {
		border-bottom: 1px #6699CC dotted;
		text-align: left;
		font-family: Verdana, sans-serif, Arial;
		font-weight: normal;
		font-size: .7em;
		color: #404040;
		background-color: #fafafa;
		padding-top: 4px;
		padding-bottom: 4px;
		padding-left: 8px;
		padding-right: 0px;
	}
</style>
</head>

<body>

<table class="table">

<tr>
<td class="header">App ID</td>
<td class="header">Game Name</td>
<td class="header">Size</td>
</tr>"""
end = """
</table>
</body>
</html>"""

t = a.find("\n<tr class='game-table-row'>")
a = a[t:]

t = a.find("\n\n</table>")
a = a[:t]

a = a.split('\n\n')

for i in a:
	x = re.findall("<td class='game-table-cell'>([0-9\.]+)(K|M|G)?\t?total</td>", i)
	if x[0][1] is "G":
		data.append((float(x[0][0])*1024*1024*1024,i))
	elif x[0][1] is "M":
		data.append((float(x[0][0])*1024*1024,i))
	elif x[0][1] is "K":
		data.append((float(x[0][0])*1024,i))
	elif x[0][1] is "":
		data.append((float(x[0][0]), i))
	else:
		print x

z = open('out.html', 'w')

z.write(start+'\n')
for i in sorted(data, key=lambda d: d[0], reverse=True):
	z.write(i[1]+'\n')
z.write(end+'\n')
