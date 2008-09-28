import tango
import boundsutils
import cairoutils
import goocanvas
import gobject
import gtk
import tangocanvas
import cairo
import math
import random
import resizegadget
import simple
import pango
import padgadget

class NodeItem(goocanvas.Group, simple.SimpleItem, goocanvas.Item):
	def __init__(self, *args, **kwargs):
		goocanvas.Group.__init__(self, *args, **kwargs)

		self._node_data = {
			'node-title': 'Node',
			'x': 0.0, 'y': 0.0, 'width': 100.0, 'height': 100.0,
			'radius-x': 0.0, 'radius-y': 0.0,
			'color-scheme': 'Plum',
		}

		self._background_rect = NodeItemFrame( parent = self, x = 0.0, y = 0.0,
			width = 200.0, height = 30.0)

		# make the background item draggable
		self._dragging_frame = False
		self._background_rect.connect("motion_notify_event", 
			self._on_frame_motion_notify)
		self._background_rect.connect("button_press_event", 
			self._on_frame_button_press)
		self._background_rect.connect("button_release_event",
			self._on_frame_button_release)

		# Add a resize gadget item child
		self._dragging_resize_gadget = False
		self._resize_gadget = resizegadget.ResizeGadget( parent = self,
			orientation = resizegadget.SE, x = 0.0, y = 0.0 )
		self._resize_gadget.connect("motion_notify_event", 
			self._on_resize_gadget_motion_notify)
		self._resize_gadget.connect("button_press_event", 
			self._on_resize_gadget_button_press)
		self._resize_gadget.connect("button_release_event",
			self._on_resize_gadget_button_release)
		self._resize_gadget_size = 15

		self._pad_table = goocanvas.Table(parent = self,
			row_spacing = 4.0)
		self._pad_labels = []
		self._pad_gadgets = []
		self._default_pad_size = 13.0
		for i in range(4):
			pad_label = goocanvas.Text(parent=self._pad_table, 
				text='Very Long Pad Label %i' % i,
				alignment=pango.ALIGN_RIGHT,
				pointer_events=goocanvas.EVENTS_NONE,
				ellipsize=pango.ELLIPSIZE_START,
				font='Sans 12',
				fill_color = 'blue',
				x=0.0, y=0.0)
			self._pad_labels.append(pad_label)
			self._pad_table.set_child_properties(pad_label, \
				row = i, column = 0, x_expand = True, x_fill = True,
				left_padding = 4.0,
				x_shrink = True)
			pad_gadget = padgadget.PadGadget(parent=self._pad_table, 
				x=0.0, y=0.0, width=20.0, height=self._default_pad_size,
				pad_size=self._default_pad_size,
				fill_color = 'red', line_width = 0.0)
			self._pad_gadgets.append(pad_gadget)
			self._pad_table.set_child_properties(pad_gadget, \
				row = i, column = 1)

		foo = gtk.Button('Hello')
		foo_item = goocanvas.Widget(parent = self._pad_table, widget = foo)
		self._pad_table.set_child_properties(foo_item, row = 4, column = 0,
			columns = 2, x_fill = True)
	
	def do_update(self, entire_tree, cr):
		## find the minimum width and height for the node frame.
		minimum_bounds = self._background_rect. \
			get_bounds_for_desired_content_bounds(cr, goocanvas.Bounds(0,0,0,0))
		(minimum_width, minimum_height) = boundsutils.get_size(minimum_bounds)

		## update the requested width and height.
		self._node_data['width'] = max(self._node_data['width'], minimum_width)
		self._node_data['height'] = max(self._node_data['height'], minimum_height)

		## attempt to set the width and height of the pad table to automatic
		content_rect = self._background_rect.get_content_area_bounds()
		self._pad_table.set_property('width', -1)
		self._pad_table.set_property('height', -1)
		self._pad_table.update(entire_tree, cr, goocanvas.Bounds())

		## get the requested bounds of the pad table
		pad_req = goocanvas.Bounds()
		self._pad_table.get_requested_area(cr, pad_req)

		## update the minimum bounds
		minimum_bounds = self._background_rect. \
			get_bounds_for_desired_content_bounds(cr, pad_req)
		(minimum_width, minimum_height) = boundsutils.get_size(minimum_bounds)

		## add in the resize gadget and the vertical padding
		vertical_padding = 6.0
		minimum_height += self._resize_gadget_size + 2.0*vertical_padding

		## update the requested width and height ignoring the minimum width
		## because the pads ellipsize.
		# self._node_data['width'] = max(self._node_data['width'], minimum_width)
		self._node_data['height'] = max(self._node_data['height'], minimum_height)

		## update all the properties for the background.
		propnames = ('width', 'height', 'radius-x',
			'radius-y', 'color-scheme', 'node-title')
		for name in propnames:
			self._background_rect.set_property(name, self._node_data[name])

		## update the translation of each child
		for child_idx in range(self.get_n_children()):
			child = self.get_child(child_idx)
			child.set_simple_transform( self._node_data['x'],
				self._node_data['y'], 1.0, 0.0 )
			child.update(entire_tree, cr, goocanvas.Bounds())

		## get the bounds of the content area
		content_rect = self._background_rect.get_content_area_bounds()

		## update the position and size of the pad table. It extends
		## horizontally to the edge of the item.
		self._pad_table.translate(0.0, content_rect.y1 + vertical_padding)
		self._pad_table.set_property('width', self._node_data['width'])
		self._pad_table.set_property('height', content_rect.y2 - content_rect.y1)
		self._pad_table.update(entire_tree, cr, goocanvas.Bounds())

		## Put the resize gadget in the lower-right
		self._resize_gadget.translate(
			content_rect.x2 - self._resize_gadget_size - 1,
			content_rect.y2 - self._resize_gadget_size - 1)
		self._resize_gadget.set_property('width', self._resize_gadget_size)
		self._resize_gadget.set_property('height', self._resize_gadget_size)
		c = tango.get_color_float_rgb( self._node_data['color-scheme'],
			tango.LIGHT_CONTRAST)
		self._resize_gadget.set_color( ( c[0], c[1], c[2], 0.5 ) )

		## update the fill colour of each pad label
		label_color = tango.get_color_hex_string_rgb( self._node_data['color-scheme'],
			tango.MEDIUM_CONTRAST)
		for label in self._pad_labels:
			label.set_property('fill_color', label_color)

		for gadget in self._pad_gadgets:
			gadget.set_color_scheme( self._node_data['color-scheme'] )

		out_bounds = goocanvas.Bounds()
		goocanvas.Group.do_update(self, entire_tree, cr, out_bounds)
		return out_bounds

	## event handlers
	def _on_frame_motion_notify(self, item, target, event):
		if((self._dragging_frame == True) and 
		   (event.state & gtk.gdk.BUTTON1_MASK)):
		   	event_point = self.get_canvas().\
				convert_from_item_space(self._resize_gadget, event.x, event.y)
			delta_x = event_point[0] - self._drag_point[0]
			delta_y = event_point[1] - self._drag_point[1]
			new_x = self._old_loc[0] + delta_x
			new_y = self._old_loc[1] + delta_y
			self.get_model().set_property('x', new_x)
			self.get_model().set_property('y', new_y)
			self.ensure_updated()
		return True
	
	def _on_frame_button_press(self, item, target, event):
		if(event.button == 1): # left button
			self._drag_point = self.get_canvas().\
				convert_from_item_space(self._resize_gadget, event.x, event.y)
			self._old_loc = ( self._node_data['x'], self._node_data['y'] )
			fleur = gtk.gdk.Cursor (gtk.gdk.FLEUR)
			canvas = item.get_canvas ()
			canvas.pointer_grab(item,
				gtk.gdk.POINTER_MOTION_MASK | 
					gtk.gdk.BUTTON_RELEASE_MASK,
				fleur, event.time)
			self._dragging_frame = True
		elif event.button == 3: # right button
			if(self.get_model() != None):
				scheme = random.choice(tango.get_scheme_names())
				print('Switch to: %s' % scheme)
				self.get_model().set_property('color-scheme', scheme)

		return True

	def _on_frame_button_release(self, item, target, event):
		canvas = item.get_canvas ()
		canvas.pointer_ungrab(item, event.time)
		self._dragging_frame = False
	
	def _on_resize_gadget_motion_notify(self, item, target, event):
		if((self._dragging_resize_gadget == True) and 
		   (event.state & gtk.gdk.BUTTON1_MASK)):
		   	event_point = self.get_canvas().\
				convert_from_item_space(self._resize_gadget, event.x, event.y)
			delta_x = event_point[0] - self._drag_point[0]
			delta_y = event_point[1] - self._drag_point[1]
			new_width = max(self._resize_gadget_size,
				self._old_size[0] + delta_x)
			new_height = max(self._resize_gadget_size,
				self._old_size[1] + delta_y)
			self.get_model().set_property('width', new_width)
			self.get_model().set_property('height', new_height)
			self.ensure_updated()
		return True
	
	def _on_resize_gadget_button_press(self, item, target, event):
		if(event.button == 1): # left button
			self._drag_point = self.get_canvas().\
				convert_from_item_space(self._resize_gadget, event.x, event.y)
			self._old_size = ( self._node_data['width'], self._node_data['height'] )
			fleur = gtk.gdk.Cursor (gtk.gdk.BOTTOM_RIGHT_CORNER)
			canvas = item.get_canvas ()
			canvas.pointer_grab(item,
				gtk.gdk.POINTER_MOTION_MASK | 
					gtk.gdk.BUTTON_RELEASE_MASK,
				fleur, event.time)
			self._dragging_resize_gadget = True
		return True

	def _on_resize_gadget_button_release(self, item, target, event):
		canvas = item.get_canvas ()
		canvas.pointer_ungrab(item, event.time)
		self._dragging_resize_gadget = False

	def _on_model_changed(self, model, recompute_bounds):
		self.request_update()
	
	## simple item methods
	def set_model(self, model):
		goocanvas.Group.set_model(self, model)

		# so nefarious
		self._node_data = model._node_data

		model.connect('changed', self._on_model_changed)
		self.request_update()
	

gobject.type_register(NodeItem)

class NodeItemFrame(tangocanvas.TangoRectItem, goocanvas.Item):
	__gproperties__ = {
		'node-title':	(str, None, None, 'Node',
			gobject.PARAM_READWRITE),
	}

	def __init__(self, *args, **kwargs):
		self._node_data = {
			'node-title': 'Node',
		}
		self._font_size = 18
		self._content_bounds = goocanvas.Bounds()

		# Initialise the remaining parts of the item
		tangocanvas.TangoRectItem.__init__(self, *args, **kwargs)
	
	def get_node_title(self):
		return self.get_property('node-title')

	def set_node_title(self, title):
		self.set_property('node-title', title)

	def get_content_area_bounds(self):
		return self._content_bounds

	## item methods
	def get_bounds_for_desired_content_bounds(self, cr, content_bounds):
		cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_BOLD)
		cr.set_font_size(self._font_size)
		extents = cr.text_extents(self.get_node_title())
		font_width = math.ceil(extents[2])
		font_height = math.ceil(extents[3])
		font_padding = math.ceil(0.5 * font_height)
		y = font_height + font_padding
		y += font_padding + 1.5
		y = math.ceil(y)
		bounds = goocanvas.Bounds()
		bounds.x1 = content_bounds.x1 - 3.0
		bounds.y1 = content_bounds.y1 - 3.0 - y
		width = max(content_bounds.x2-content_bounds.x1, font_width + 20.0)
		bounds.x2 = bounds.x1 + width + 6.0
		bounds.y2 = content_bounds.y2 + 3.0
		return bounds
	
	## gobject methods
	def do_get_property(self, pspec):
		if(pspec.name == 'node-title'):
			return self._node_data['node-title']
		else:
			return tangocanvas.TangoRectItem.do_get_property(self, pspec)	

	def do_set_property(self, pspec, value):
		if(pspec.name == 'node-title'):
			self._node_data['node-title'] = value
			self.request_update()
		else:
			tangocanvas.TangoRectItem.do_set_property(self, pspec, value)
	
	## simple item methods
	def set_model(self, model):
		tangocanvas.TangoRectItem.set_model(self, model)

		# so nefarious
		self._node_data = model._node_data

	def do_simple_is_item_at(self, x, y, cr, is_pointer_event):
		return tangocanvas.TangoRectItem.do_simple_is_item_at(self, x, y,
			cr, is_pointer_event)

	def do_simple_update(self, cr):
		tangocanvas.TangoRectItem.do_simple_update(self, cr)

		# Calculate the content area bounds
		int_bounds = self.get_interior_bounds()
		ext_bounds = self.get_bounds()
		cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_BOLD)
		cr.set_font_size(self._font_size)
		extents = cr.text_extents(self.get_node_title())
		font_height = math.ceil(extents[3])
		font_padding = math.ceil(0.5 * font_height)

		y = int_bounds.y1 + font_height + font_padding
		y += font_padding + 1.5
		y = math.ceil(y)

		self._content_bounds = goocanvas.Bounds(
			int_bounds.x1, y,
			int_bounds.x2, int_bounds.y2)

	def do_simple_create_path(self, cr):
		tangocanvas.TangoRectItem.do_simple_create_path(self, cr)
	
	def do_simple_paint(self, cr, bounds):
		tangocanvas.TangoRectItem.do_simple_paint(self, cr, bounds)

		scheme = self.get_color_scheme()

		# Add our own decoration
		int_bounds = self.get_interior_bounds()

		cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_BOLD)
		cr.set_font_size(self._font_size)

		# Draw the node title
		extents = cr.text_extents(self.get_node_title())
		font_height = math.ceil(extents[3])
		font_padding = math.ceil(0.5 * font_height)

		y = int_bounds.y1 + font_height + font_padding
		cr.move_to( \
			math.floor(0.5*(int_bounds.x1+int_bounds.x2-extents[2])),
			y)
		tango.cairo_set_source(cr, scheme, tango.DARK_CONTRAST)
		cr.show_text(self.get_node_title())

		# Draw a separator
		y += font_padding + 0.5
		cr.set_line_width(1.0)
		cr.move_to( int_bounds.x1 + 5.5, y )
		cr.line_to( int_bounds.x2 - 5.5, y )
		tango.cairo_set_source(cr, scheme, tango.DARK)
		cr.stroke()

		y += 1.0
		cr.move_to( int_bounds.x1 + 5.5, y )
		cr.line_to( int_bounds.x2 - 5.5, y )
		tango.cairo_set_source(cr, scheme, tango.LIGHT)
		cr.stroke()

		node_bounds = boundsutils.align_to_integer_boundary( \
			self.get_bounds())

		content_bounds = boundsutils.inset( \
			self.get_content_area_bounds(), 2.0, 2.0)

#		tango.paint_pad(cr, scheme, node_bounds.x2, 
#			content_bounds.y1 + 20.5, tango.RIGHT, 15, True)
#
#		tango.paint_pad(cr, scheme, node_bounds.x2, 
#			content_bounds.y1 + 50.5, tango.RIGHT, 15)
#
#		tango.paint_pad(cr, scheme, node_bounds.x2, 
#			content_bounds.y1 + 80.5, tango.RIGHT, 15)

gobject.type_register(NodeItemFrame)

class NodeModel(goocanvas.GroupModel, goocanvas.ItemModel):
	__gproperties__ = {
		'node-title':	(str, None, None, 'Node',
			gobject.PARAM_READWRITE),
		'x': (gobject.TYPE_DOUBLE, None, None, 
			-gobject.G_MAXDOUBLE, gobject.G_MAXFLOAT,
			0.0, gobject.PARAM_READWRITE),
		'y': (gobject.TYPE_DOUBLE, None, None,
			-gobject.G_MAXDOUBLE, gobject.G_MAXFLOAT,
			0.0, gobject.PARAM_READWRITE),
		'width': (gobject.TYPE_DOUBLE, None, None, 
			0.0, gobject.G_MAXDOUBLE,
			100.0, gobject.PARAM_READWRITE),
		'height': (gobject.TYPE_DOUBLE, None, None,
			0.0, gobject.G_MAXDOUBLE,
			100.0, gobject.PARAM_READWRITE),
		'radius-x': (gobject.TYPE_DOUBLE, None, None, 
			0.0, gobject.G_MAXDOUBLE,
			0.0, gobject.PARAM_READWRITE),
		'radius-y': (gobject.TYPE_DOUBLE, None, None,
			0.0, gobject.G_MAXDOUBLE,
			0.0, gobject.PARAM_READWRITE),
		'color-scheme':	(str, None, None, 'Plum',
			gobject.PARAM_READWRITE),
	}

	def __init__(self, *args, **kwargs):
		self._node_data = {
			'node-title': 'Node',
			'x': 0.0, 'y': 0.0, 'width': 100.0, 'height': 100.0,
			'radius-x': 0.0, 'radius-y': 0.0,
			'color-scheme': 'Plum',
		}

		goocanvas.GroupModel.__init__(self, *args, **kwargs)

	## gobject methods
	def do_get_property(self, pspec):
		propnames = self._node_data.keys()
		if(pspec.name in propnames):
			return self._node_data[pspec.name]
		else:
			raise AttributeError('No such property: %s' % pspec.name)

	def do_set_property(self, pspec, value):
		propnames = self._node_data.keys()
		if(pspec.name in propnames):
			self._node_data[pspec.name] = value
			self.emit('changed', False)
		else:
			raise AttributeError('No such property: %s' % pspec.name)
	
	## item model methods
	def do_create_item(self, canvas):
		item = NodeItem()
		item.set_model(self)
		item.set_canvas(canvas)
		return item

gobject.type_register(NodeModel)

# vim:sw=4:ts=4:autoindent
