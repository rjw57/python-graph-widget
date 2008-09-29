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
from graphcanvas import tangocanvas

class App:
	def clearup(self):
		pass

	def _button_press(self, target, event):
		if(event.button == 2): ## middle
			self.new_node(event.x, event.y)

	def new_node(self, x, y):
		new_node = graphcanvas.NodeModel(
		#new_node = tangocanvas.TangoRectModel(
			node_title = 'Filter',
			color_scheme = 'Dark Aluminium',
			parent = self._model,
			x = x, y = y,
			radius_x = 9, radius_y = 9,
			width = 300, height = 200)

		graphcanvas.Pad(parent = new_node,
			name = 'Input node 1', id = 'foo',
			type = graphcanvas.PadType.INPUT)
		graphcanvas.Pad(parent = new_node,
			name = 'Input node 2', id = 'foobas',
			type = graphcanvas.PadType.INPUT)
		graphcanvas.Pad(parent = new_node,
			name = 'Output node 1', id = 'out',
			type = graphcanvas.PadType.OUTPUT)
	
	def new_canvas(self, graph_model):
		bg_color = 0xBABDB6
		graph_widget = goocanvas.Canvas()
		graph_widget.set_property('background-color-rgb', bg_color)
		graph_widget.set_property('automatic-bounds', True)
		graph_widget.set_property('integer-layout', True)
		graph_widget.set_root_item_model(graph_model)

		graph_widget.connect('button-release-event', self._button_press)

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
