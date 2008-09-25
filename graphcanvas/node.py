import tango
import boundsutils
import cairoutils
import goocanvas
import gobject
import gtk
import tangocanvas
import cairo
import math

class NodeItem(tangocanvas.TangoRectItem, goocanvas.Item):
	__gproperties__ = {
		'node-title':	(str, None, None, 'Node',
			gobject.PARAM_READWRITE),
	}

	def __init__(self, *args, **kwargs):
		self._dragging = False
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

		# make this item draggable
		self.connect("motion_notify_event", self._on_motion_notify)
		self.connect("button_press_event", self._on_button_press)
		self.connect("button_release_event", self._on_button_release)

	def do_simple_is_item_at(self, x, y, cr, is_pointer_event):
		return True

	def do_simple_update(self, cr):
		tangocanvas.TangoRectItem.do_simple_update(self, cr)

		# Calculate the content area bounds
		int_bounds = self.get_interior_bounds()
		cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_BOLD)
		cr.set_font_size(self._font_size)
		extents = cr.text_extents(self.get_node_title())
		font_height = math.ceil(extents[3])
		font_padding = math.ceil(0.62 * font_height) # golden ratio

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
		font_padding = math.ceil(0.62 * font_height) # golden ratio

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
		content_bounds = self.get_content_area_bounds()

		#cairoutils.rounded_rect(cr, content_bounds, 7, 7)
		#cr.set_source_rgba(1,1,1,0.25)
		#cr.fill()

		tango.paint_pad(cr, scheme, node_bounds.x2, 
			content_bounds.y1 + 20.5, tango.RIGHT, 15, True)

		tango.paint_pad(cr, scheme, node_bounds.x2, 
			content_bounds.y1 + 50.5, tango.RIGHT, 15)

		tango.paint_pad(cr, scheme, node_bounds.x2, 
			content_bounds.y1 + 80.5, tango.RIGHT, 15)


	## event handlers
	def _on_motion_notify(self, item, target, event):
		if((self._dragging == True) and 
		   (event.state & gtk.gdk.BUTTON1_MASK)):
			new_x = event.x
			new_y = event.y
			self.get_model().set_property('x',
				self._old_x + new_x - self._drag_x)
			self.get_model().set_property('y', 
				self._old_y + new_y - self._drag_y)
		return True
	
	def _on_button_press(self, item, target, event):
		if(event.button == 1):
			self._drag_x = event.x
			self._drag_y = event.y
			self._old_x = self.get_property('x')
			self._old_y = self.get_property('y')

			fleur = gtk.gdk.Cursor (gtk.gdk.FLEUR)
			canvas = item.get_canvas ()
			canvas.pointer_grab(item,
				gtk.gdk.POINTER_MOTION_MASK | 
					gtk.gdk.BUTTON_RELEASE_MASK,
				fleur, event.time)
			self._dragging = True
		elif event.button == 2:
			item.lower(None)
		elif event.button == 3:
			item.raise_(None)
		return True

	def _on_button_release(self, item, target, event):
		canvas = item.get_canvas ()
		canvas.pointer_ungrab(item, event.time)
		self._dragging = False

gobject.type_register(NodeItem)

class NodeModel(tangocanvas.TangoRectModel, goocanvas.ItemModel):
	__gproperties__ = {
		'node-title':	(str, None, None, 'Node',
			gobject.PARAM_READWRITE),
	}

	def __init__(self, *args, **kwargs):
		self._node_data = {
			'node-title': 'Node',
		}

		tangocanvas.TangoRectModel.__init__(self, *args, **kwargs)

	## gobject methods
	def do_get_property(self, pspec):
		if(pspec.name == 'node-title'):
			return self._node_data['node-title']
		else:
			return tangocanvas.TangoRectModel.do_get_property(self, pspec)	
	def do_set_property(self, pspec, value):
		if(pspec.name == 'node-title'):
			self._node_data['node-title'] = value
			self.emit('changed', False)
		else:
			tangocanvas.TangoRectModel.do_set_property(self, pspec, value)
	
	## item model methods
	def do_create_item(self, canvas):
		item = NodeItem()
		item.set_model(self)
		item.set_canvas(canvas)
		return item

gobject.type_register(NodeModel)

# vim:sw=4:ts=4:autoindent
