"""Implementations of all on-path strategies"""
from __future__ import division
import random

import collections
import numpy as np
import copy
import logging

from icarus.registry import register_strategy
from icarus.util import inheritdoc, path_links

from .base import Strategy

__all__ = [
	   'PopularityDistance',
		   ]

@register_strategy('PD')
class PopularityDistance(object):
	def __init__(self, shortest_path, link_weight, cache_size, contents, content_source, popularity):
		self.shortest_path = shortest_path
		self.link_weight = link_weight
		self.cache_size = cache_size
		self.contents = contents
		self.content_source = content_source
		self.popularity = popularity
		self.receivers = self.popularity.keys()
		self.caches = self.cache_size.keys()
		self.cache_disc = {v: collections.defaultdict(bool) for v in self.cache_size.keys()}

		self.init_distance()
		self.init_popularity()

		self.logger = logging.getLogger('offline')

	def init_popularity(self):
		self.cache_pop = {v:collections.defaultdict(float) for v in self.caches}
		for r in self.receivers:
			for content in self.contents:
				popularity = self.popularity[r][content]
				path = self.shortest_path[r][self.content_source[content]]
				for u, v in path_links(path):
					if v in self.caches:
						self.cache_pop[v][content] += popularity
						if self.cache_disc[v][content]:
							break
	def init_distance(self):
		self.dist = {v:collections.defaultdict(float) for v in self.caches}
		self.rec_dist = {v:collections.defaultdict(float) for v in self.receivers}
		for content in self.contents:
			for receiver in self.receivers:
				weight = 0.0
				path = list(reversed(self.shortest_path[receiver][self.content_source[content]]))
				for u, v in path_links(path):
					weight += self.link_weight[(u, v)]
					if v in self.caches:
						if content not in self.dist[v]:
							self.dist[v][content] = weight
						if self.cache_disc[v][content]:
							weight = 0.0
				else:
					self.rec_dist[receiver][content] = weight


	def update(self, cache, content):
		path = self.shortest_path[cache][self.content_source[content]]
		for u, v in path_links(path):
			if v in self.caches:
				# print self.cache_pop[v][content], self.cache_pop[cache][content], old[content]
				# print self.cache_disc[cache][content]
				self.cache_pop[v][content] -= self.cache_pop[cache][content]
				if self.cache_disc[v][content]:
					break
		for receiver in self.receivers:
			weight = 0.0
			path = list(reversed(self.shortest_path[receiver][cache]))
			for u, v in path_links(path):
				weight += self.link_weight[(u, v)]
				if v in self.caches:
					if content not in self.dist[v]:
						self.dist[v][content] = weight
					if self.cache_disc[v][content]:
						break
			else:
				self.rec_dist[receiver][content] = weight

	def cal_res(self):
		res = 0.0
		for content in self.contents:
			for receiver in self.receivers:
				res += self.popularity[receiver][content] * self.rec_dist[receiver][content]
		return res


	def results(self, precision=0.1):
		choices = {i:[c for c in self.contents] for i in self.caches}
		while len(choices)>0:
			max_val = 0.0
			choice = None
			for i in choices:
				if sum(self.cache_disc[i].values())>=self.cache_size[i]:
					choices.pop(i)
				else:
					for c in choices[i]:
						val = self.cache_pop[i][c]*self.dist[i][c]
						if abs(val)<10e-6:
							choices[i].remove(c)
						elif val > max_val:
							choice = (i,c)
							max_val = val
			if abs(max_val)<10e-6:
				break
			self.cache_disc[choice[0]][choice[1]] = 1
			choices[choice[0]].remove(choice[1])
			if len(choices[choice[0]])<=0:
				choices.pop(choice[0])
			self.update(*choice)

			# self.logger.info(now)
		return {'WEIGHT':{
			'MEAN': self.cal_res()
		}}







