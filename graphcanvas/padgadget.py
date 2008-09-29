import tango
import boundsutils
import cairoutils
import goocanvas
import gobject
import simple
import math

class PadGadget(goocanvas.Rect, simple.SimpleItem, goocanvas.Item):
	__gproperties__ = {
		'orientation': ( int, None, None, 0, 3, tango.RIGHT, 
			gobject.PARAM_READWRITE ) ,
		'color-scheme': ( str, None, None, 'Plum', gobject.PARAM_READWRITE ) ,
		'pad-size': (float, None, None, 0.0, gobject.G_MAXFLOAT, 15.0,
			gobject.PARAM_READWRITE ) ,
	}

	def __init__(self, *args, **kwargs):
		self._bounds = goocanvas.Bounds()
		self._highlight_flag = False
		self._pad_data = {
			'orientation': tango.RIGHT,
			'color-scheme': 'Plum',
			'pad-size': 15.0,
		}
		goocanvas.Rect.__init__(self, *args, **kwargs)
	
	def _get_internal_bounds(self):
		internal_bounds = boundsutils.align_to_integer_boundary( \
			goocanvas.Bounds(
				self.get_property('x'),
				self.get_property('y'),
				self.get_property('x') + self.get_property('width'),
				self.get_property('y') + self.get_property('height')))
		return internal_bounds
	
	def get_pad_size(self):
		return self.get_property('pad-size')
	
	def set_pad_size(self, value):
		self.set_property('pad-size', value)
	
	def get_color_scheme(self):
		return self.get_property('color-scheme')
	
	def set_color_scheme(self, color_scheme):
		self.set_property('color-scheme', color_scheme)
	
	def get_orientation(self):
		return self.get_property('orientation')
	
	def set_orientation(self, orientation):
		self.set_property('orientation', orientation)
	
	## gobject methods
	def do_get_property(self, pspec):
		names = self._pad_data.keys()
		if(pspec.name in names):
			return self._pad_data[pspec.name]
		else:
			return goocanvas.Rect.do_get_property(self, pspec)
	
	def do_set_property(self, pspec, value):
		names = self._pad_data.keys()
		if(pspec.name in names):
			self._pad_data[pspec.name] = value
			self.request_update()
		else:
			goocanvas.Rect.do_set_property(self, pspec, value)
	
	## simple item methods
	def set_model(self, model):
		goocanvas.Rect.do_set_model(self, model)
	
	def do_simple_is_item_at(self, x, y, cr, is_pointer_event):
		return simple.SimpleItem.do_simple_is_item_at(
			self, x, y, cr, is_pointer_event)

	def do_simple_create_path(self, cr):
		(x, y) = self._get_pad_location()
		tango.pad_boundary_curve(cr, x, y, self.get_orientation(),
			self.get_pad_size())
	
	def do_simple_paint(self, cr, bounds):
		my_bounds = self.get_bounds()
		if(not boundsutils.do_intersect(my_bounds, bounds)):
			return

		(x, y) = self._get_pad_location()

		tango.paint_pad(cr, self.get_color_scheme(), x, y,
			self.get_orientation(), self.get_pad_size(),
			self._highlight_flag)

		#cairoutils.rounded_rect(cr, self._get_internal_bounds(), 0, 0)
		#cr.set_source_rgb(1,0,0)
		#cr.fill()
	
	def _get_pad_location(self):
		int_bounds = self._get_internal_bounds()
		
		## default x and y is to be in centre
		x = math.floor(0.5 * (int_bounds.x2 + int_bounds.x1)) + 0.5
		y = math.floor(0.5 * (int_bounds.y2 + int_bounds.y1)) + 0.5

		orientation = self.get_orientation()
		if(orientation == tango.RIGHT):
			x = int_bounds.x2
		elif(orientation == tango.LEFT):
			x = int_bounds.x1
		elif(orientation == tango.TOP):
			y = int_bounds.y1
		elif(orientation == tango.BOTTOM):
			y = int_bounds.y2

		return (x,y)
	
	## event handlers
	def do_enter_notify_event(self, target, event):
		self._highlight_flag = True
		self.changed(False)
	
	def do_leave_notify_event(self, target, event):
		self._highlight_flag = False
		self.changed(False)

gobject.type_register(PadGadget)

# vim:sw=4:ts=4:autoindent
