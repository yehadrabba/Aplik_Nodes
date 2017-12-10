#!/usr/bin/env python
# -*- coding: utf-8
from bokeh.plotting import figure, show
from bokeh import models
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models import HoverTool, widgets, ranges
import bokeh.layouts as layouts
from scipy import signal
import numpy as np
import sys, io
import os
import datetime
from dateutil import parser

fs = 6400*60
scale = 8.0 / 32768

# Parameters
#node_id = sys.argv[1]
#date_id = sys.argv[2] # '20170925'
#hour_id = sys.argv[3] # '0000'

node_id = str('6')
date_id = str('20171019')
hour_id = str('0000')


xlbl = "Frecuencia (CPM)"
aylbl = "Aceleración (G)"
vylbl = "Velocidad (mm/s)"


txlbl = 'Trend n6'
tylbl = 'Time'

#trends variables

xsum_list = []
ysum_list = []
zsum_list = []

txx_list = []
txy_list = []
txz_list = []
date_list= []
xsum = 0
txx  = 0 
ysum = 0
txy  = 0 
zsum = 0
txz  = 0 





# Faster version of loadtxt - about 8 times faster!!!
def iter_loadtxt(filename, delimiter=' ', skiprows=0, dtype=float):
    def iter_func():
        with open(filename, 'r') as infile:
            for _ in range(skiprows):
                next(infile)
            for line in infile:
                line = line.rstrip().split(delimiter)
                for item in line:
                    yield dtype(item)
        iter_loadtxt.rowlength = len(line)

    data = np.fromiter(iter_func(), dtype=dtype)
    data = data.reshape((-1, iter_loadtxt.rowlength))
    return data





asourcelist = []

#Variable para la ruta al directorio
path = ('/home/yehad/Escritorio/aplik/data/n-' + node_id +'/')
 
#Lista vacia para incluir (hora,trendX, trendY, trendZ)
dt_list = []
 
#Lista con todos los ficheros del directorio:
lstDir = os.listdir(path)  
for i in lstDir:

	#create time elements
	year = i[0:4]
	month = i[4:6]
	day =  i[6:8]
	hora = i[8:10]
	minutos = i[10:12]

	#time variable
	s = i[0:12]
	date =  parser.parse(s)
	#load data
	#data = np.loadtxt('/home/yehad/Escritorio/aplik/data/n-' + node_id + '/' + i)
	data = iter_loadtxt('/home/yehad/Escritorio/aplik/data/n-' + node_id + '/' + i)
	# Get PSD of X,Y and Z
	f, Pxx = signal.welch(data[:,0] * scale, fs, 'hanning', nperseg=16384, scaling='spectrum')
	f, Pxy = signal.welch(data[:,1] * scale, fs, 'hanning', nperseg=16384, scaling='spectrum')
	f, Pxz = signal.welch(data[:,2] * scale, fs, 'hanning', nperseg=16384, scaling='spectrum')



	#calcule summation by node
	if node_id == '6':
		for i in range(len(f)):
			if f[i]> 5000 and f[i]<6000:
				xsum = xsum + Pxx[i]
				ysum = ysum + Pxy[i]
				zsum = zsum + Pxz[i]

	if node_id == '7':
		for i in range(len(f)):
			if f[i]> 24000 and f[i]< 27000:
				xsum = xsum + Pxx[i]
				ysum = ysum + Pxy[i]
				zsum = zsum + Pxz[i]

	if node_id == '8':
		for i in range(len(f)):
			if f[i]> 37000 and f[i]<40000:
				xsum = xsum + Pxx[i]
				ysum = ysum + Pxy[i]
				zsum = zsum + Pxz[i]
	print type(Pxx).__name__
	#calcule trends
	txx  = np.sqrt(xsum)
	txy  = np.sqrt(ysum)
	txz  = np.sqrt(zsum)
	dt_list.append((date,txx,txy,txz))

	txx_list.append(txx)
	txy_list.append(txy)
	txz_list.append(txz)
	date_list.append(date)
	#dicsum = dict(f=f, x = np.array(xsum) , y = np.array(ysum), z = np.array(zsum))

#n6_source = models.ColumnDataSource(data=dict( xx=txx, yy=txy, zz=txz))



# Cut higher frequencies to reduce html sizes:
f = f[:4096]
Pxx = Pxx[:4096]
Pxy = Pxy[:4096]
Pxz = Pxz[:4096]



# Our tool bar
scrt = models.WheelZoomTool(dimensions='width')
drgt = models.PanTool()
tools = [ drgt, scrt,
          models.ZoomInTool(dimensions='height'), models.ZoomOutTool(dimensions='height'),
          models.BoxZoomTool(dimensions='width'),
          models.HoverTool(
            tooltips = [ ( aylbl, '(@x, @y, @z)' ), ( xlbl, '@f{0,0.}' ) ],
            mode='mouse'
            ),
          models.ResetTool(), models.SaveTool()
        ]

# create acceleration plots
px = figure(
   width=1200, height=250,
   tools=tools, active_scroll=scrt, active_drag=drgt,
   title="Nodo " + node_id + " - X",
   x_axis_label=xlbl, y_axis_label=aylbl
)

py = figure(
   width=1200, height=250,
   x_range=px.x_range, y_range=px.y_range,
   tools=tools,
   title="Nodo " + node_id + " - Y",
   x_axis_label=xlbl, y_axis_label=aylbl
)
pz = figure(
   width=1200, height=250,
   x_range=px.x_range, y_range=px.y_range,
   tools=tools,
   title="Nodo " + node_id + " - Z",
   x_axis_label=xlbl, y_axis_label=aylbl
)

# Axis formatting
px.xaxis.formatter = models.NumeralTickFormatter(format="00")
py.xaxis.formatter = models.NumeralTickFormatter(format="00")
pz.xaxis.formatter = models.NumeralTickFormatter(format="00")

# Keeps zoom range always visible
px.y_range.callback = models.CustomJS( code='cb_obj.start = 0;' )


#-------------------------------TRENDS NODO 6---------------------

tx6 = figure(
   width=1200, height=250,
   tools=tools, active_scroll=scrt, active_drag=drgt,
   title="Nodo " + node_id + " - X",
   x_axis_label=txlbl, y_axis_label=tylbl,y_axis_type="datetime"
)

ty6 = figure(
   width=1200, height=250,
   x_range=tx6.x_range, y_range=tx6.y_range,
   tools=tools,
   title="Nodo " + node_id + " - Y",
   x_axis_label=txlbl, y_axis_label=tylbl, y_axis_type="datetime"
)
tz6 = figure(
   width=1200, height=250,
   x_range=tx6.x_range, y_range=tx6.y_range,
   tools=tools,
   title="Nodo " + node_id + " - Z",
   x_axis_label=txlbl, y_axis_label=tylbl, y_axis_type="datetime"
)

# Axis formatting
tx6.xaxis.formatter = models.NumeralTickFormatter(format="00")
ty6.xaxis.formatter = models.NumeralTickFormatter(format="00")
tz6.xaxis.formatter = models.NumeralTickFormatter(format="00")


# Keeps zoom range always visible
tx6.y_range.callback = models.CustomJS( code='cb_obj.start = 0;' )
trends6 = layouts.gridplot([[tx6],[ty6],[tz6]])



print txx_list

print txy_list

print txz_list

# Plots
asource = models.ColumnDataSource(data=dict(f=f, x=np.sqrt(Pxx), y=np.sqrt(Pxy), z=np.sqrt(Pxz)))

#ssource = models.ColumnDataSource(dicsum)


px.line('f', 'x', source=asource)
py.line('f', 'y', source=asource)
pz.line('f', 'z', source=asource)

"""for i in dt_list:
	(date2,txx2,txy2,txz2 )= i
	tx6.line(txx2,'f' , source=asource)
	ty6.line(txy2, 'f', source=asource)
	tz6.line(txz2, 'f', source=asource)
	"""
tx6.line(txx_list, date_list)
ty6.line(txy_list, date_list)
tz6.line(txz_list, date_list)
# Plots



paccel = layouts.gridplot([[px],[py],[pz]])

scrt = models.WheelZoomTool(dimensions='width')
drgt = models.PanTool()
tools = [ drgt, scrt,
          models.ZoomInTool(dimensions='width'), models.ZoomOutTool(dimensions='width'),
          models.BoxZoomTool(dimensions='width'),
          models.HoverTool(
            tooltips = [ ( vylbl, '@x, @y, @z' ), ( xlbl, '@f{0,0.}' ) ],
            mode='mouse'
            ),
          models.ResetTool(), models.SaveTool()
        ]

# create speed plots
spx = figure(
   width=1200, height=250,
   x_range=px.x_range,
   tools=tools, active_scroll=scrt, active_drag=drgt,
   title="Nodo " + node_id + " - X",
   x_axis_label=xlbl, y_axis_label=vylbl
)
spy = figure(
   width=1200, height=250,
   x_range=px.x_range, y_range=spx.y_range,
   tools=tools,
   title="Nodo " + node_id + " - Y",
   x_axis_label=xlbl, y_axis_label=vylbl
)
spz = figure(
   width=1200, height=250,
   x_range=px.x_range, y_range=spx.y_range,
   tools=tools,
   title="Nodo " + node_id + " - Z",
   x_axis_label=xlbl, y_axis_label=vylbl
)

# Axis formatting
spx.xaxis.formatter = models.NumeralTickFormatter(format="00")
spy.xaxis.formatter = models.NumeralTickFormatter(format="00")
spz.xaxis.formatter = models.NumeralTickFormatter(format="00")

# Keeps zoom range always visible
spx.y_range.callback = models.CustomJS( code='cb_obj.start = 0;' )

# Plots
vsource = models.ColumnDataSource( data = dict(
    f=f[4:],
    x=9800 * np.sqrt(Pxx[4:]) / (f[4:]+10),
    y=9800 * np.sqrt(Pxy[4:]) / (f[4:]+10),
    z=9800 * np.sqrt(Pxz[4:]) / (f[4:]+10) ))
spx.line('f', 'x', source=vsource)
spy.line('f', 'y', source=vsource)
spz.line('f', 'z', source=vsource)

pspd = layouts.gridplot([[spx], [spy], [spz]])

# Create the tabs
tab1 = widgets.Panel(child=paccel, title="Aceleración (G)")
tab2 = widgets.Panel(child=pspd, title="Velocidad (mm/s)")
tab3 = widgets.Panel(child=trends6, title="Trends node 6")

tabs = widgets.Tabs(tabs=[ tab2, tab1 ,tab3])

# output to static HTML file

node_list = [ '5', '2' ]
date_list = [ '20170920', '20170921', '20170922', '20170923', '20170924', '20170925' ]
time_list = [ '0000', '0400', '0800', '1200', '1600', '2000' ]

# This is a selection box to change the node:
sel = '<select onchange="if (this.value) window.location.href=this.value">'
for nid in node_list:
    if nid == node_id:
        opt = 'selected '
    else:
        opt = ''
    sel = sel + '<option ' + opt + 'value="psd-' + nid + '-' + date_id + hour_id + '.html">Nodo #' + nid +'</option>'
sel = sel + '</select>'

# This is a selection box to change the date:
sel = sel + '<select onchange="if (this.value) window.location.href=this.value">'
for did in date_list:
    if did == date_id:
        opt = 'selected '
    else:
        opt = ''
    sel = sel + '<option ' + opt + 'value="psd-' + node_id + '-' + did + hour_id + '.html">' + did +'</option>'
sel = sel + '</select>'

# This is a selection box to change the time:
sel = sel + '<select onchange="if (this.value) window.location.href=this.value">'
for hid in time_list:
    if hid == hour_id:
        opt = 'selected '
    else:
        opt = ''
    sel = sel + '<option ' + opt + 'value="psd-' + node_id + '-' + date_id + hid + '.html">' + hid +'</option>'
sel = sel + '</select>'


# Our HTML template:
htemp = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{{ title|e }}</title>
        {{ bokeh_css }}
        {{ bokeh_js }}
        <style>
          html {
            width: 100%;
            height: 100%;
          }
          body {
            width: 90%;
            height: 100%;
            margin: auto;
          }
        </style>
    </head>
    <body>
        <h1>{{ title|e }}</h1>""" + sel + """
        {{ plot_div|indent(8) }}
        {{ plot_script|indent(8) }}
    </body>
</html>
"""

from jinja2 import Template
htemp = Template(htemp)

# show the results
ofile = "psd-" + node_id + "-" + date_id + hour_id + ".html"
html = file_html(tabs, CDN, title="Mediciones Nodo #" + node_id + ", " + date_id + ", " + hour_id,
                 template=htemp)
with io.open(ofile, mode="w", encoding="utf-8") as f:
    f.write(unicode(html))
