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

class App:
	def clearup(self):
		pass

	def __init__(self, glade):
		graph_model = goocanvas.GroupModel()

		bg_color = 0xBABDB6

		scrolled_win = gtk.ScrolledWindow()
		graph_widget = goocanvas.Canvas()
		graph_widget.set_property('background-color-rgb', bg_color)
		graph_widget.set_property('automatic-bounds', True)
		graph_widget.set_property('integer-layout', True)
		graph_widget.set_root_item_model(graph_model)
		scrolled_win.add(graph_widget)
		box = glade.get_widget('lbox')
		box.pack_start(scrolled_win, True, True)

		scrolled_win = gtk.ScrolledWindow()
		graph_widget = goocanvas.Canvas()
		graph_widget.set_property('background-color-rgb', bg_color)
		graph_widget.set_property('automatic-bounds', True)
		graph_widget.set_property('integer-layout', True)
		graph_widget.set_root_item_model(graph_model)
		scrolled_win.add(graph_widget)
		box = glade.get_widget('rbox')
		box.pack_start(scrolled_win, True, True)

		new_node = graphcanvas.NodeModel(
			color_scheme = 'Dark Aluminium',
			node_title = 'Filter Element',
			parent = graph_model,
			x = 20, y = 50,
			radius_x = 9, radius_y = 9,
			width = 300, height = 200)
	
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
