import tango
import boundsutils
import cairoutils
import goocanvas
import gobject
import simple
import node
import edge

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
		goocanvas.Group.set_model(self, model)

gobject.type_register(GraphItem)

class GraphModel(goocanvas.GroupModel, goocanvas.ItemModel):
	''' A GraphModel holds a list of node models and edge models
		which collectively form a graph. '''

	#__gproperties__ = {
	#	'color-scheme':	(str, None, None, 'Plum',
	#		gobject.PARAM_READWRITE),
	#}

	def __init__(self, *args, **kwargs):
		goocanvas.GroupModel.__init__(self, *args, **kwargs)

		## add internal models for nodes and edges
		self._node_models = goocanvas.GroupModel(parent = self)
		self._edge_models = goocanvas.GroupModel(parent = self)
	
	def get_nodes(self):
		node_list = []
		for idx in range(self._node_models.get_n_children()):
			node_list.append(self._node_models.get_child(idx))
		return node_list
	
	def get_edges(self):
		edge_list = []
		for idx in range(self._edge_models.get_n_children()):
			edge_list.append(self._edge_models.get_child(idx))
		return edge_list
	
	## group methods
	def do_add_child(self, child, pos):
		## special cases for nodes and edges - essentially
		## we're creating a node and edge layer.
		if(isinstance(child, node.NodeModel)):
			self._node_models.add_child(child, pos)
			child.set_graph_model(self)
		elif(isinstance(child, edge.EdgeModel)):
			self._edge_models.add_child(child, pos)
			child.set_graph_model(self)
		else:
			goocanvas.GroupModel.do_add_child(self, child, pos)

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
		#item = goocanvas.Group()
		item.set_model(self)
		item.set_canvas(canvas)

		## for each child, create an item and add it
		for idx in range(self.get_n_children()):
			child = self.get_child(idx)

			## FIXME: Horrible hack
			try:
				item.add_child(child.do_create_item(canvas))
			except:
				item.add_child(child.do_create_item(child, canvas))

		return item

gobject.type_register(GraphModel)


# vim:sw=4:ts=4:autoindent
