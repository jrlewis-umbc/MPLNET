#!/usr/bin/env python3

from . import julian
from PIL import Image
import io
import numpy as np

__version__ = '0.0.2'


# mpl_plot
# Handles quick scatter/line and contour plots, based on V3 IDL functions: mpl_plot for scatter/line and set_plot + oplot2d for contour
#
#	Utilizes plotly scatter and heatmap graph objects
#		Plotly byte output and PIL for returning image as bytes or non-interactive image display (requires default image viewer to be installed)
#		Interactive display uses plotly HTML object opened in default browser
#
#	Required Inputs:
#			x					1D numpy array or list			x axis data, if x is list it is internally converted to numpy array
#			y					1D numpy array or list			y axis data, if y is list it is internally converted to numpy array
#																	Note: for MPLNET, if y is 2D (e.g. altitude from MPLNET product file), it will convert to 1D using first time profile
#								Note: if z is not provided, then a scatter plot is returned
#
#	Optional Inputs:
#			z					2D numpy array or list			z axis data for 2D plotting, if z is a 2D list it is converted to numpy array
#																	If z is input, then a 2D plot is returned
#			(x)(y)(z)range		list or numpy array				specifies the x, y, or z axis min and max values:  [min,max]
#																	If not set, uses the min and max values from the x,y,z arrays
#			time				string							set to 'x' or 'y' to indicate that the data provided are date/time. Will convert axis to date time string values.
#			title				string							plot title, will be centered over plot
#			(x)(y)(z)title		string							the x, y, or z axis titles. Z axis title is along the colorbar
#			colorbar			string							name of desired colorbar (from plotly options)
#			width				integer							pixel width for plot (default is 1000 if not set)
#			height				integer							pixel height for plot (default is 500 if not set)
#			interactive			dictionary						plotly figure.show config dict, default is None. To use interactive with default plotly settings interactive={} (use to control interactive aspects of the plot)
#			mode				string							plotly scatter plot mode, e.g. linear, etc... default is None
#			output				string							if set, will do one of the following instead of displaying plot. Available options are:
#																	'html': will return plotly HTML string object (suitable for insertion in div or iframe)
#																	'bytes': will return a png image as a byte string
#																	output_file_path: full path to desired output file, will save plot as image based on extension (e.g. .png)
#			verbose				boolean					if set (True), prints error and warning messages
#
# 	Returns one of the following based on file availability and option selection
#		True			success displaying plot
#		HTML string		if html=True
#		bytes			if bytes=True
#		None			function failed or error
#
#	Examples:
#
#		from mplnet import plot as mpl_plot
#
#		plot x-y scatter plot, display image:
#		p = mpl_plot(x=x,y=y)
#		p = mpl_plot(x=x,y=y,xrange=[0,10],yrange=[0,20],xtitle='x axis',ytitle='y axis') # set x and y axis ranges and titles
#
#		plot x-y scatter plot, display interactive image in default browser (using default plotly settings):
#		p = mpl_plot(x=x,y=y,xrange=[0,10],yrange=[0,20],xtitle='x axis',ytitle='y axis',interactive={})
#
#		plot 2D plot, display interactive image in default browser (using default plotly settings):
#		p = mpl_plot(x=x,y=y,z=z,xrange=[0,10],yrange=[0,20],zrange=[0,4],xtitle='x axis',ytitle='y axis',ztitle='z data',interactive={}) # uses default rainbow colorbar
#
#		plot 2D plot, save to output file:
#		p = mpl_plot(x=x,y=y,z=z,xrange=[0,10],yrange=[0,20],zrange=[0,4],xtitle='x axis',ytitle='y axis',ztitle='z data',output='/path/file.png') # uses default rainbow colorbar
#
#	
#	History:
#				2025-06-11 EJW	created
#				2025-06-30 EJW 	removed Kaledio from imports, no longer used
#
def	mpl_plot(x=None,y=None,z=None,xrange=None,yrange=None,zrange=None,time=None,title='',xtitle='',ytitle='',ztitle='',colorbar='rainbow',width=1000,height=500,interactive=None,mode=None,output=None,verbose=False):
	
	import plotly.graph_objects as go
	import plotly.io as pio
	import plotly.express as px
	
	if (x is not None and not isinstance(x, np.ndarray)):
		x = np.array(x)
	elif (x is None):
		if (verbose):
			print('ERROR: mpl_plot: must input x list/array')
		return None
	
	if (y is not None and not isinstance(y, np.ndarray)):
		y = np.array(y)
	elif (y is None):
		if (verbose):
			print('ERROR: mpl_plot: must input y list/array')
		return None
	
	if (z is not None and not isinstance(z, np.ndarray)):
		z = np.array(z)
	
	if (xrange == None):
		xrange = [np.min(x),np.max(x)]
	
	if (yrange == None):
		yrange = [np.min(y),np.max(y)]
	
	if (y.ndim == 2):
		y = y[:,0]
	
	if (time != None):
		if (time.casefold() == 'x'):
			x = [julian.isodate(xx,iso=True) for xx in x]
			xrange = [julian.isodate(xrange[0],iso=True),julian.isodate(xrange[1],iso=True)]
		if (time.casefold() == 'y'):
			# transform y array to time
			y = [julian.isodate(yy,iso=True) for yy in y]
			yrange = [julian.isodate(yrange[0],iso=True),julian.isodate(yrange[1],iso=True)]
		
	if (z is not None and isinstance(z, np.ndarray)):
		
		if (zrange == None):
			zrange = [np.min(z),np.max(z)]
		fig = go.Figure(
			data =
				go.Heatmap(
					z=z,
					x=x,
					y=y,
					dy=5,
					y0=0,
					zmin=zrange[0],
					zmax=zrange[1],
					connectgaps=False,
					colorscale=colorbar,
					colorbar={
						"title": {
							"text": ztitle,
							"side": "right"
						},
						"ticks": "outside"
					}
				)
			)
	else:
		fig = go.Figure(data =
		go.Scatter(
			x=x,
			y=y,
			mode=mode
		))
	
	fig.update_layout(
		autosize=False,
		width=width,
		height=height,
		title={
			"text": title,
			"x": 0.5,
			"y": 0.85,
			"xanchor": "center",
			"yanchor": "top"
		},
		xaxis = {
			"title_text": xtitle,
			"ticks": "outside",
			#"nticks": 6,
			#"tickformat" : '%H:%M:%S',
			"range": xrange
		},
		yaxis = {
			"title_text": ytitle,
			"ticks": "outside",
			"range": yrange
		}
	)
	
	if (output != None):
		if (output.casefold() == 'html'):
			return fig.to_html(full_html=False)
		elif (output.casefold() == 'bytes'):
			data = pio.to_image(fig, format='png')
			return io.BytesIO(data)
		else:
			fig.write_image(output)
			return True
	
	if (interactive != None):
		if (interactive == {}):
			fig.show()
		else:
			fig.show(config=interactive)
	else:
		data = pio.to_image(fig, format='png')
		image_stream = io.BytesIO(data)
		image = Image.open(image_stream)
		image.show()



