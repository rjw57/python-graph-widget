import tango
import boundsutils
import cairoutils
import goocanvas
import gobject
import simple

class ResizeGadget(goocanvas.Rect, simple.SimpleItem, goocanvas.Item):
	def __init__(self, *args, **kwargs):
		self._bounds = goocanvas.Bounds()
		goocanvas.Rect.__init__(self, *args, **kwargs)
	
	## gobject methods
	def do_get_property(self, pspec):
		return goocanvas.Rect.do_get_property(self, pspec)
	
	def do_set_property(self, pspec, value):
		goocanvas.Rect.do_set_property(self, pspec, value)
	
	## simple item methods
	def set_model(self, model):
		goocanvas.Rect.do_set_model(self, model)

	def do_simple_is_item_at(self, x, y, cr, is_pointer_event):
		return simple.SimpleItem.do_simple_is_item_at(
			self, x, y, cr, is_pointer_event)

	def do_simple_create_path(self, cr):
		# For hit testing
		cairoutils.rounded_rect(cr, self.get_bounds(), 0, 0)
	
	def do_simple_paint(self, cr, bounds):
		my_bounds = self.get_bounds()
		if(not boundsutils.do_intersect(my_bounds, bounds)):
			return

		my_bounds = boundsutils.inset(my_bounds, 1.5, 1.5)

		width = my_bounds.x2 - my_bounds.x1
		height = my_bounds.y2 - my_bounds.y1
		size = min(width, height)

		cr.new_path()
		for offset in range(4, size, 3):
			cr.move_to(my_bounds.x2 - offset, my_bounds.y2)
			cr.line_to(my_bounds.x2, my_bounds.y2 - offset)

		cr.set_source_rgba(1,1,1,0.33)
		cr.set_line_width(1.0)
		cr.stroke()

gobject.type_register(ResizeGadget)

# vim:sw=4:ts=4:autoindent
