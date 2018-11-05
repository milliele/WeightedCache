"""Implementations of all on-path strategies"""
from __future__ import division
import random

import collections
import numpy as np
# import logging

from icarus.registry import register_strategy
from icarus.util import inheritdoc, path_links

from .base import Strategy

__all__ = [
	   'QStrategy',
	'GreedyStrategy',
		   ]

class DefofQ(object):
	def __init__(self, alpha=1.0):
		self._dist = collections.defaultdict(int)
		self._maxdist = -1
		self.alpha = alpha

	def q(self,k):
		if self._maxdist == -1:
			return 0
		return self._dist[k]*1.0/self._dist[self._maxdist]

	# def remove(self, k):
	# 	if k==self._maxdist:
	# 		self._maxdist=max(self._dist.keys(), key=lambda x:self._dist[x])

	def update(self,k, d):
		self._dist[k]=(1-self.alpha)*self._dist[k]+self.alpha*d
		if self._dist[k]>self._dist[self._maxdist]:
			self._maxdist=k


@register_strategy('Q')
class QStrategy(Strategy):
	"""Leave Copy Everywhere (LCE) strategy.

	In this strategy a copy of a content is replicated at any cache on the
	path between serving node and receiver.
	"""

	@inheritdoc(Strategy)
	def __init__(self, view, controller, alpha=1.0, **kwargs):
		super(QStrategy, self).__init__(view, controller)
		# logger = logging.getLogger('strategy')
		# logger.info(alpha)
		self._qs = {v:DefofQ(alpha) for v in self.view.cache_nodes()}

	@inheritdoc(Strategy)
	def process_event(self, time, receiver, content, log):
		# get all required data
		source = self.view.content_source(content)
		path = self.view.shortest_path(receiver, source)
		record = collections.defaultdict(bool)
		# Route requests to original source and queries caches on the path
		self.controller.start_session(time, receiver, content, log)
		for u, v in path_links(path):
			self.controller.forward_request_hop(u, v)
			if self.view.has_cache(v):
				if random.random() < self._qs[v].q(content):
					record[v]=True
					if self.controller.get_content(v):
						serving_node = v
						break
				elif self.controller.has_content(v):
					serving_node = v
					break
		else:
			# No cache hits, get content from source
			self.controller.get_content(v)
			serving_node = v
		# Return content
		path = list(reversed(self.view.shortest_path(receiver, serving_node)))
		weight = 0
		for u, v in path_links(path):
			self.controller.forward_content_hop(u, v)
			weight += self.view.link_weight(u,v)
			if self.view.has_cache(v):
				# insert content
				self._qs[v].update(content, weight)
				if record[v]:
					content = self.controller.put_content(v)
					# if content!=None:
					# 	self._qs[v].remove(content)
		self.controller.end_session()

@register_strategy('GRD')
class GreedyStrategy(Strategy):
	"""Leave Copy Everywhere (LCE) strategy.

	In this strategy a copy of a content is replicated at any cache on the
	path between serving node and receiver.
	"""

	@inheritdoc(Strategy)
	def __init__(self, view, controller, **kwargs):
		super(GreedyStrategy, self).__init__(view, controller)
		# self._qs = {v:DefofQ() for v in self.view.cache_nodes()}

	@inheritdoc(Strategy)
	def process_event(self, time, receiver, content, log):
		# get all required data
		source = self.view.content_source(content)
		path = self.view.shortest_path(receiver, source)
		# Route requests to original source and queries caches on the path
		self.controller.start_session(time, receiver, content, log)
		for u, v in path_links(path):
			self.controller.forward_request_hop(u, v)
			if self.view.has_cache(v):
				if self.controller.get_content(v):
					serving_node = v
					break
		else:
			# No cache hits, get content from source
			self.controller.get_content(v)
			serving_node = v
		# Return content
		path = list(reversed(self.view.shortest_path(receiver, serving_node)))
		weight = 0
		for u, v in path_links(path):
			self.controller.forward_content_hop(u, v)
			weight += self.view.link_weight(u, v)
			if self.view.has_cache(v):
				# insert content
				self.controller.put_content(v, t=time, weight=weight)
		self.controller.end_session()
