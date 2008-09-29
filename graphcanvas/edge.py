import tango
import boundsutils
import cairoutils
import cairo
import goocanvas
import gobject
import simple
import math
import padgadget

class EdgeItem(goocanvas.ItemSimple, simple.SimpleItem, goocanvas.Item):
	__gproperties__ = {
		'start-anchor-x': ( float, None, None, 
			-gobject.G_MAXFLOAT, gobject.G_MAXFLOAT, 0.0,
			gobject.PARAM_READWRITE ) ,
		'start-anchor-y': ( float, None, None, 
			-gobject.G_MAXFLOAT, gobject.G_MAXFLOAT, 0.0,
			gobject.PARAM_READWRITE ) ,
		'end-anchor-x': ( float, None, None, 
			-gobject.G_MAXFLOAT, gobject.G_MAXFLOAT, 0.0,
			gobject.PARAM_READWRITE ) ,
		'end-anchor-y': ( float, None, None, 
			-gobject.G_MAXFLOAT, gobject.G_MAXFLOAT, 0.0,
			gobject.PARAM_READWRITE ) ,
		'edge-width': ( float, None, None, 
			0.0, gobject.G_MAXFLOAT, 9.0,
			gobject.PARAM_READWRITE ) ,
		'color-scheme': ( str, None, None, 'Butter', 
			gobject.PARAM_READWRITE ) ,
		'invalid-color-scheme': ( str, None, None, 'Scarlet Red', 
			gobject.PARAM_READWRITE ) ,
	}

	def __init__(self, *args, **kwargs):
		self._bounds = goocanvas.Bounds()
		self._color = (1.0, 1.0, 1.0, 0.33)
		self._resize_data = {
			'start-anchor-x': 0.0,
			'start-anchor-y': 0.0,
			'end-anchor-x': 0.0,
			'end-anchor-y': 0.0,
			'color-scheme': 'Butter',
			'invalid-color-scheme': 'Scarlet Red',
			'edge-width': 9.0,
		}

		## the start and end pads
		self._start_pad = None
		self._end_pad = None

		goocanvas.ItemSimple.__init__(self, *args, **kwargs)
		
	def get_edge_width(self):
		return self.get_property('edge-width')
	
	def set_edge_width(self, edge_width):
		self.set_property('edge-width', edge_width)

	def get_color_scheme(self):
		return self.get_property('color-scheme')
	
	def set_color_scheme(self, color_scheme):
		self.set_property('color-scheme', color_scheme)

	def get_invalid_color_scheme(self):
		return self.get_property('invalid-color-scheme')
	
	def set_invalid_color_scheme(self, invalid_color_scheme):
		self.set_property('invalid-color-scheme', invalid_color_scheme)
	
	def get_start_anchor(self):
		return ( \
			self.get_property('start-anchor-x'),
			self.get_property('start-anchor-y') )
	
	def set_start_anchor(self, x, y):
		self.set_property('start-anchor-x', x)
		self.set_property('start-anchor-y', y)
	
	def get_end_anchor(self):
		return ( \
			self.get_property('end-anchor-x'),
			self.get_property('end-anchor-y') )
	
	def set_end_anchor(self, x, y):
		self.set_property('end-anchor-x', x)
		self.set_property('end-anchor-y', y)

	def is_valid(self):
		''' Work out if this edge is valid based on whether
		    there is a pad under the start and end anchor. '''
		
		return (self._start_pad != None) and (self._end_pad != None)

	## gobject methods
	def do_get_property(self, pspec):
		names = self._resize_data.keys()
		if(pspec.name in names):
			return self._resize_data[pspec.name]
		else:
			return goocanvas.ItemSimple.do_get_property(self, pspec)
	
	def do_set_property(self, pspec, value):
		names = self._resize_data.keys()
		if(pspec.name in names):
			self._resize_data[pspec.name] = value
			self.changed(True)
		else:
			goocanvas.ItemSimple.do_set_property(self, pspec, value)
	
	## simple item methods
	def set_model(self, model):
		# goocanvas.ItemSimple.do_set_model(self, model)
		pass
	
	def do_simple_update(self, cr):
		width = self.get_edge_width()
		bounds = boundsutils.inset(self._get_internal_bounds(),
			-0.5 * width, -0.5 * width)
		self.bounds_x1 = bounds.x1
		self.bounds_y1 = bounds.y1
		self.bounds_x2 = bounds.x2
		self.bounds_y2 = bounds.y2

		# Update the start and end pads
		start = self.get_start_anchor()
		end = self.get_end_anchor()
		self._start_pad = self._get_pad_at(*start)
		self._end_pad = self._get_pad_at(*end)
	
	def _get_pad_at(self, x, y):
		items = self.get_canvas().get_items_at(x,y,False)
		pad_item = None
		if(items != None):
			for item in items:
				if(isinstance(item, padgadget.PadGadget)):
					pad_item = item
		return pad_item

	def do_simple_is_item_at(self, x, y, cr, is_pointer_event):
		return simple.SimpleItem.do_simple_is_item_at(
			self, x, y, cr, is_pointer_event)
	
	def _get_internal_bounds(self):
		start = self.get_start_anchor()
		end = self.get_end_anchor()
		minx = min(start[0], end[0])
		miny = min(start[1], end[1])
		maxx = max(start[0], end[0])
		maxy = max(start[1], end[1])
		return goocanvas.Bounds(minx,miny,maxx,maxy)

	def do_simple_create_path(self, cr):
		# For hit testing
		cr.new_path()
		start = self.get_start_anchor()
		end = self.get_end_anchor()
		cr.set_line_cap(cairo.LINE_CAP_ROUND)
		cr.set_line_width(self.get_edge_width())
		cr.curve_to(0.5 * (start[0]+end[0]), start[1],
			0.5 * (start[0]+end[0]), end[1], end[0], end[1])
	
	def do_simple_paint(self, cr, bounds):
		my_bounds = self.get_bounds()
		if(not boundsutils.do_intersect(my_bounds, bounds)):
			return

		my_bounds = self._get_internal_bounds()

		start = self.get_start_anchor()
		end = self.get_end_anchor()
		width = self.get_edge_width()

		if(self.is_valid()):
			scheme = self.get_color_scheme()
		else:
			scheme = self.get_invalid_color_scheme()

		cr.new_path()
		cr.move_to(start[0], start[1])
		cr.curve_to(0.5 * (start[0]+end[0]), start[1],
			0.5 * (start[0]+end[0]), end[1], end[0], end[1])
		cr.set_line_cap(cairo.LINE_CAP_ROUND)
		cr.set_line_width(self.get_edge_width())
		tango.cairo_set_source(cr, scheme, tango.DARK)
		cr.stroke_preserve()
		cr.set_line_width(self.get_edge_width() - 2)
		tango.cairo_set_source(cr, scheme, tango.LIGHT)
		cr.stroke_preserve()

gobject.type_register(EdgeItem)

# vim:sw=4:ts=4:autoindent
