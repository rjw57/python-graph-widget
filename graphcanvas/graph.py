import tango
import boundsutils
import cairoutils
import goocanvas
import gobject
import simple

class GraphItem(goocanvas.Group, simple.SimpleItem, goocanvas.Item):
	#__gproperties__ = {
	#	'color-scheme':	(str, None, None, 'Plum',
	#		gobject.PARAM_READWRITE),
	#}

	def __init__(self, *args, **kwargs):
		goocanvas.Group.__init__(self, *args, **kwargs)
	
	## gobject methods
	#def do_get_property(self, pspec):
	#	if(pspec.name == 'color-scheme'):
	#		return self._data['color-scheme']
	#	else:
	#		return goocanvas.Group.do_get_property(self, pspec)
	
	#def do_set_property(self, pspec, value):
	#	if(pspec.name == 'color-scheme'):
	#		if(not value in tango.get_scheme_names()):
	#			raise ValueError( \
	#				'%s is not a valid Tango color scheme' % value)
	#		self._data['color-scheme'] = value
	#		self.request_update()
	#	else:
	#		goocanvas.Group.do_set_property(self, pspec, value)
	
	## simple item methods
	def set_model(self, model):
		goocanvas.Group.do_set_model(self, model)

gobject.type_register(GraphItem)

class GraphModel(goocanvas.GroupModel, goocanvas.ItemModel):
	#__gproperties__ = {
	#	'color-scheme':	(str, None, None, 'Plum',
	#		gobject.PARAM_READWRITE),
	#}

	def __init__(self, *args, **kwargs):
		goocanvas.GroupModel.__init__(self, *args, **kwargs)

	## gobject methods
#	def do_get_property(self, pspec):
#		if(pspec.name == 'color-scheme'):
#			return self._data['color-scheme']
#		else:
#			return goocanvas.GroupModel.do_get_property(self, pspec)
#	
#	def do_set_property(self, pspec, value):
#		if(pspec.name == 'color-scheme'):
#			if(not value in tango.get_scheme_names()):
#				raise ValueError( \
#					'%s is not a valid Tango color scheme' % value)
#			self._data['color-scheme'] = value
#			self.emit('changed', False)
#		else:
#			goocanvas.GroupModel.do_set_property(self, pspec, value)
	
	## item model methods
	def do_create_item(self, canvas):
		item = GraphItem()
		item.set_model(self)
		item.set_canvas(canvas)
		return item

gobject.type_register(GraphModel)


# vim:sw=4:ts=4:autoindent
