"""This module implements the simulation engine.

The simulation engine, given the parameters according to which a single
experiments needs to be run, instantiates all the required classes and executes
the experiment by iterating through the event provided by an event generator
and providing them to a strategy instance.
"""
from icarus.execution import NetworkModel, NetworkView, NetworkController, CollectorProxy
from icarus.registry import DATA_COLLECTOR, STRATEGY

import networkx as nx
import fnss


__all__ = ['exec_experiment',
		   'exec_offline_experiment',
		   ]

def symmetrify_paths(shortest_paths):
	"""Make paths symmetric

	Given a dictionary of all-pair shortest paths, it edits shortest paths to
	ensure that all path are symmetric, e.g., path(u,v) = path(v,u)

	Parameters
	----------
	shortest_paths : dict of dict
		All pairs shortest paths

	Returns
	-------
	shortest_paths : dict of dict
		All pairs shortest paths, with all paths symmetric

	Notes
	-----
	This function modifies the shortest paths dictionary provided
	"""
	for u in shortest_paths:
		for v in shortest_paths[u]:
			shortest_paths[u][v] = list(reversed(shortest_paths[v][u]))
	return shortest_paths

def exec_experiment(topology, workload, netconf, strategy, cache_policy, collectors):
	"""Execute the simulation of a specific scenario.

	Parameters
	----------
	topology : Topology
		The FNSS Topology object modelling the network topology on which
		experiments are run.
	workload : iterable
		An iterable object whose elements are (time, event) tuples, where time
		is a float type indicating the timestamp of the event to be executed
		and event is a dictionary storing all the attributes of the event to
		execute
	netconf : dict
		Dictionary of attributes to inizialize the network model
	strategy : tree
		Strategy definition. It is tree describing the name of the strategy
		to use and a list of initialization attributes
	cache_policy : tree
		Cache policy definition. It is tree describing the name of the cache
		policy to use and a list of initialization attributes
	collectors: dict
		The collectors to be used. It is a dictionary in which keys are the
		names of collectors to use and values are dictionaries of attributes
		for the collector they refer to.

	Returns
	-------
	results : Tree
		A tree with the aggregated simulation results from all collectors
	"""
	model = NetworkModel(topology, cache_policy, **netconf)
	view = NetworkView(model)
	controller = NetworkController(model)

	collectors_inst = [DATA_COLLECTOR[name](view, **params)
					   for name, params in collectors.items()]
	collector = CollectorProxy(view, collectors_inst)
	controller.attach_collector(collector)

	strategy_name = strategy['name']
	strategy_args = {k: v for k, v in strategy.items() if k != 'name'}
	strategy_inst = STRATEGY[strategy_name](view, controller, **strategy_args)

	for time, event in workload:
		strategy_inst.process_event(time, **event)
	return collector.results()

def exec_offline_experiment(topology, workload, netconf, strategy, ):
	# Filter inputs
	if not isinstance(topology, fnss.Topology):
		raise ValueError('The topology argument must be an instance of '
						 'fnss.Topology or any of its subclasses.')

	# Shortest paths of the network
	shortest_path = symmetrify_paths(nx.all_pairs_dijkstra_path(topology))
	content_source = {}
	# Dictionary mapping the reverse, i.e. nodes to set of contents stored
	source_node = {}

	# Dictionary of link weights
	link_weight = nx.get_edge_attributes(topology, 'util')
	if not topology.is_directed():
		for (u, v), lw in list(link_weight.items()):
			link_weight[(v, u)] = lw

	cache_size = {}
	for node in topology.nodes_iter():
		stack_name, stack_props = fnss.get_stack(topology, node)
		if stack_name == 'router':
			if 'cache_size' in stack_props:
				cache_size[node] = stack_props['cache_size']
		elif stack_name == 'source':
			contents = stack_props['contents']
			source_node[node] = contents
			for content in contents:
				content_source[content] = node
	if any(c < 1 for c in cache_size.values()):
		for node in cache_size:
			if cache_size[node] < 1:
				cache_size[node] = 1

	popularity = workload.get_popularity_all()

	strategy_name = strategy['name']
	strategy_inst = STRATEGY[strategy_name](shortest_path, link_weight, cache_size, workload.contents, content_source, popularity)
	return strategy_inst.results()