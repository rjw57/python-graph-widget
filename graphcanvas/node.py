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

class NodeItem(goocanvas.Group, simple.SimpleItem, goocanvas.Item):
	def __init__(self, *args, **kwargs):
		goocanvas.Group.__init__(self, *args, **kwargs)

		self._node_data = {
			'node-title': 'Node',
			'x': 0.0, 'y': 0.0, 'width': 100.0, 'height': 100.0,
			'radius-x': 0.0, 'radius-y': 0.0,
			'color-scheme': 'Plum',
		}

		self._background_rect = NodeItemFrame( parent = self )

		# make the background item draggable
		self._dragging = False
		self._background_rect.connect("motion_notify_event", 
			self._on_frame_motion_notify)
		self._background_rect.connect("button_press_event", 
			self._on_frame_button_press)
		self._background_rect.connect("button_release_event",
			self._on_frame_button_release)

		# Add a resize gadget item child
		self._resize_gadget = resizegadget.ResizeGadget( parent = self,
			orientation = resizegadget.SE)
		self._resize_gadget.connect('button-press-event', self.foo)
	
	def _update_children(self):
		propnames = ('x', 'y', 'width', 'height', 'radius-x', 
			'radius-y', 'color-scheme')
		for name in propnames:
			self._background_rect.set_property(name, self._node_data[name])
		self._background_rect.ensure_updated()

		content_rect = self._background_rect.get_content_area_bounds()

		# Put the resize gadget in the lower-right
		resize_size = 15
		self._resize_gadget.set_property('x', content_rect.x2 - resize_size - 1)
		self._resize_gadget.set_property('y', content_rect.y2 - resize_size - 1)
		self._resize_gadget.set_property('width', resize_size)
		self._resize_gadget.set_property('height', resize_size)
		c = tango.get_color_float_rgb( self._node_data['color-scheme'],
			tango.LIGHT_CONTRAST)
		self._resize_gadget.set_color( ( c[0], c[1], c[2], 0.5 ) )

		self._resize_gadget.ensure_updated()

	## event handlers
	def _on_frame_motion_notify(self, item, target, event):
		if((self._dragging == True) and 
		   (event.state & gtk.gdk.BUTTON1_MASK)):
			new_x = event.x
			new_y = event.y
			self.get_model().set_property('x', self._old_x + new_x - self._drag_x)
			self.get_model().set_property('y', self._old_y + new_y - self._drag_y)
		return True
	
	def _on_frame_button_press(self, item, target, event):
		if(event.button == 1): # left button
			self._drag_x = event.x
			self._drag_y = event.y
			self._old_x = self._node_data['x']
			self._old_y = self._node_data['y']
			self.ensure_updated()

			fleur = gtk.gdk.Cursor (gtk.gdk.FLEUR)
			canvas = item.get_canvas ()
			canvas.pointer_grab(item,
				gtk.gdk.POINTER_MOTION_MASK | 
					gtk.gdk.BUTTON_RELEASE_MASK,
				fleur, event.time)
			self._dragging = True
		elif event.button == 3: # right button
			if(self.get_model() != None):
				scheme = random.choice(tango.get_scheme_names())
				print('Switch to: %s' % scheme)
				self.get_model().set_property('color-scheme', scheme)

		return True

	def _on_frame_button_release(self, item, target, event):
		canvas = item.get_canvas ()
		canvas.pointer_ungrab(item, event.time)
		self._dragging = False
	
	def _on_model_changed(self, model, recompute_bounds):
		self._update_children()
	
	def foo(self, item, target, event):
		print('hello: %s, %s, %s' % (item, target, event))
	
	## simple item methods
	def set_model(self, model):
		goocanvas.Group.set_model(self, model)

		# so nefarious
		self._node_data = model._node_data

		self._update_children()

		model.connect('changed', self._on_model_changed)

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

		tango.paint_pad(cr, scheme, node_bounds.x2, 
			content_bounds.y1 + 20.5, tango.RIGHT, 15, True)

		tango.paint_pad(cr, scheme, node_bounds.x2, 
			content_bounds.y1 + 50.5, tango.RIGHT, 15)

		tango.paint_pad(cr, scheme, node_bounds.x2, 
			content_bounds.y1 + 80.5, tango.RIGHT, 15)

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
