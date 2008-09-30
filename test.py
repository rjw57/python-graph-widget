#!/usr/bin/env python

import gtk			# Calls gtk module
import gtk.glade		# Calls gtk.glade module
import gtk.gtkgl		# Calls gtk.gtkgl module
import gobject

import goocanvas

import sys
import os
import math

import graphcanvas

class MyNode(graphcanvas.NodeModel, goocanvas.ItemModel):
	def __init__(self, *args, **kwargs):
		self._input_pads = [
			graphcanvas.PadModel(type = graphcanvas.INPUT, 
				label = 'Input A'), 
			graphcanvas.PadModel(type = graphcanvas.INPUT, 
				label = 'Input B'), 
			graphcanvas.PadModel(type = graphcanvas.INPUT,
				label = 'Input C'), 
		]
		self._output_pads = [
			graphcanvas.PadModel(type = graphcanvas.OUTPUT, 
				label = 'Output A'), 
			graphcanvas.PadModel(type = graphcanvas.OUTPUT,
				label = 'Output B'), 
		]

		graphcanvas.NodeModel.__init__(self, *args, **kwargs)
	
	## pad query methods
	def get_n_output_pads(self):
		return len(self._output_pads)
	
	def get_output_pad(self, idx):
		return self._output_pads[idx]

	def get_n_input_pads(self):
		return len(self._input_pads)
	
	def get_input_pad(self, idx):
		return self._input_pads[idx]

class App:
	def clearup(self):
		pass

	def _button_press(self, target, event):
		if(event.button == 2): ## middle
			self.new_node(event.x, event.y)
	
	def _scroll_event(self, canvas, event):
		mult = 1.0
		if(event.direction == gtk.gdk.SCROLL_UP):
			mult = 1.1
		elif(event.direction == gtk.gdk.SCROLL_DOWN):
			mult = 0.9
		scale = canvas.get_scale()
		canvas.set_scale(scale * mult)

	def new_node(self, x, y):
		new_node = MyNode(
			node_title = 'Filter',
			color_scheme = 'Sky Blue',
			parent = self._model,
			x = x, y = y,
			radius_x = 9, radius_y = 9,
			width = -1, height = -1)

	def new_canvas(self, graph_model):
		bg_color = 0xBABDB6
		graph_widget = goocanvas.Canvas()
		graph_widget.set_property('background-color-rgb', bg_color)
		graph_widget.set_property('automatic-bounds', True)
		graph_widget.set_property('integer-layout', True)
		# graph_widget.set_property('anchor', gtk.ANCHOR_CENTER)
		graph_widget.set_root_item_model(graph_model)

		graph_widget.connect('button-press-event', self._button_press)
		graph_widget.connect('scroll-event', self._scroll_event)

		return graph_widget

	def __init__(self, glade):
		graph_model = graphcanvas.GraphModel()
		#graph_model = goocanvas.GroupModel()
		self._model = graph_model
	
		self.new_node(10, 10)

		scrolled_win = gtk.ScrolledWindow()
		graph_widget = self.new_canvas(graph_model)
		scrolled_win.add(graph_widget)
		box = glade.get_widget('lbox')
		box.pack_start(scrolled_win, True, True)

		scrolled_win = gtk.ScrolledWindow()
		graph_widget = self.new_canvas(graph_model)
		scrolled_win.add(graph_widget)
		box = glade.get_widget('rbox')
		box.pack_start(scrolled_win, True, True)
	
	def on_main_window_delete_event(self, widget, event):
		gtk.main_quit()


if(__name__ == '__main__'):
	print '(C) 2008 Rich Wareham <richwareham@gmail.com>'
	print 'See LICENSE file for distribution rights'

	script_dir = os.path.dirname(__file__)

	# Load the UI
	ui = gtk.glade.XML(os.path.join(script_dir, 'ui.glade'))

	# Load the main widget
	main_window = ui.get_widget('main_window')

	# Create the app
	App = App(ui)
	ui.signal_autoconnect(App)

	main_window.show_all()
	gtk.main()

	print('Exiting and clearing up...')
	App.clearup()

# vim:sw=4:ts=4:autoindent
