import tango
import boundsutils
import cairoutils
import goocanvas
import gobject
import simple
import math

# Various orientations of the widget.
NE, NW, SE, SW = range(4)

class ResizeGadget(goocanvas.Rect, simple.SimpleItem, goocanvas.Item):
	__gproperties__ = {
		'orientation': ( int, None, None, 0, 3, 0, gobject.PARAM_READWRITE ) ,
	}

	def __init__(self, *args, **kwargs):
		self._bounds = goocanvas.Bounds()
		self._color = (1.0, 1.0, 1.0, 0.33)
		self._orientation = SE

		goocanvas.Rect.__init__(self, *args, **kwargs)
	
	def _get_internal_bounds(self):
		internal_bounds = boundsutils.align_to_integer_boundary( \
			goocanvas.Bounds(
				self.get_property('x'),
				self.get_property('y'),
				self.get_property('x') + self.get_property('width'),
				self.get_property('y') + self.get_property('height')))
		return internal_bounds
	
	def get_color(self):
		return self._color
	
	def set_color(self, color):
		self._color = color
		self.request_update()
	
	def get_orientation(self):
		return self.get_property('orientation')
	
	def set_orientation(self, orientation):
		self.set_property('orientation', orientation)
	
	## gobject methods
	def do_get_property(self, pspec):
		if(pspec.name == 'orientation'):
			return self._orientation
		else:
			return goocanvas.Rect.do_get_property(self, pspec)
	
	def do_set_property(self, pspec, value):
		if(pspec.name == 'orientation'):
			self._orientation = value
		else:
			goocanvas.Rect.do_set_property(self, pspec, value)
	
	## simple item methods
	def set_model(self, model):
		goocanvas.Rect.do_set_model(self, model)

	def do_simple_is_item_at(self, x, y, cr, is_pointer_event):
		return simple.SimpleItem.do_simple_is_item_at(
			self, x, y, cr, is_pointer_event)

	def do_simple_create_path(self, cr):
		# For hit testing
		cairoutils.rounded_rect(cr, self._get_internal_bounds(), 0, 0)
	
	def do_simple_paint(self, cr, bounds):
		my_bounds = self._get_internal_bounds()
		if(not boundsutils.do_intersect(my_bounds, bounds)):
			return

		my_bounds = boundsutils.inset(my_bounds, 1.5, 1.5)

		width = my_bounds.x2 - my_bounds.x1
		height = my_bounds.y2 - my_bounds.y1
		size = int(math.floor(min(width, height)))

		if((self._orientation == SE) or (self._orientation == NE)):
			xsign = -1
			xstart = my_bounds.x2
		else:
			xsign = 1
			xstart = my_bounds.x2 - size

		if((self._orientation == NE) or (self._orientation == NW)):
			ysign = 1
			ystart = my_bounds.y2 - size
		else:
			ysign = -1
			ystart = my_bounds.y2

		cr.new_path()
		for offset in range(4, size, 3):
			cr.move_to(xstart + (xsign * offset), ystart)
			cr.line_to(xstart, ystart + (ysign * offset))

		cr.set_source_rgba(*self._color)
		cr.set_line_width(1.0)
		cr.stroke()

gobject.type_register(ResizeGadget)

# vim:sw=4:ts=4:autoindent
