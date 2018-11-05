# -*- coding:utf-8 -*-

import random
from icarus.models.cache import *
from icarus.tools.stats import TruncatedZipfDist
import numpy as np
import pandas as pd
from icarus.registry import *
import collections
import json


N_CONTENT = 3*10**4
# CACHE_SIZE = [0.1,]
CACHE_SIZE = [0.001, 0.005, 0.01, 0.05, 0.1]
ALPHA = [0.6,0.7,0.8,0.9,1.0]
N_REPLICATION = 50
# variance
# STD = np.logspace(2, 4, 5)
# print STD
# AVG = max(STD)*3+1 # 3-sita policy
# AVG = 10**4

DISTANCES = [10, 100, 1000]


N_WARMUP = 3*10**5
N_MEASURE = 6*10**5
SEED = None
RATE = 12

SETTING = {
	'GRD': {
		'cache': {
			'cache_policy': 'GRD',
			'is_q': False,
		},
		'test':{
			'n_warmup': 3*10**4,
			'n_measure': 6*10**4,
		},
	},
	'WLRU': {
		'cache': {
			'cache_policy': 'LRU',
			'is_q': True,
		},
		'test': {
			'n_warmup': 3*10**6,
			'n_measure': 6*10**6,
		},
			 },
	'WLFU': {
		'cache': {
			'cache_policy': 'PERFECT_LFU',
			'is_q': True,
		},
		'test': {
			'n_warmup': 3*10**6,
			'n_measure': 6*10**6,
		},
			 },
	'LRU': {
		'cache': {
			'cache_policy': 'LRU',
			'is_q': False,
		},
		'test': {
			'n_warmup': 3*10**5,
			'n_measure': 3*10**5,
		},
			 },
}

class TruncatedNormal(object):
	def __init__(self, avg=0, std=1, seed=None):
		np.random.seed(seed)
		self._l = avg-3*std
		self._m = avg+3*std
		self._avg = avg
		self._std = std

	def rv(self):
		res = self._l-1
		while res <self._l or res>self._m:
			res = np.round(np.random.normal(self._avg, self._std, 1)[0])
		return res

class SingleCachePolicy(object):
	def __init__(self, cache_size, name, cache_policy, is_q, **kwargs):
		self._cache = CACHE_POLICY[cache_policy](cache_size, **kwargs)
		self.poli = name
		self._is_q = is_q

	def init_exp(self, weight, popularity, seed = None, n_warmup = N_WARMUP, n_measure = N_MEASURE):
		self.weight = weight
		self.max_weight = max(self.weight)
		self.q = np.array(self.weight)*1.0/self.max_weight
		# print "Q  = ", self.q
		self.popularity = popularity
		self.n_warmup = n_warmup
		self.n_measure = n_measure
		self.seed = seed

	def test(self):
		random.seed(SEED)
		np.random.seed(SEED)

		cnt = 0
		t = 0.0
		base = 0
		hit = 0
		# hit_rate = 0
		# prev = 0

		while cnt<=self.n_warmup + self.n_measure:
		# while base == 0 or hit ==0 or abs(hit * 1.0 / base-prev)>=0.01:
			cnt += 1
			t += (random.expovariate(RATE))
			content = int(self.popularity.rv())
			is_hit = self.__request(t, content)

			# prev = hit * 1.0 / base if base !=0 else 0
			if cnt >self.n_warmup:
				base += 1
				if is_hit:
					hit += self.weight[content-1]
				# hit_rate += 1

			# print "Policy:%s, Count: %d, Time:%f, HIT_RATIO: %f%%, SAVED_WEIGHT:%f" % (self.poli, cnt, t, hit_rate * 100.0 / base if base !=0 else 0, hit * 1.0 / base if base !=0 else 0)

		return hit * 1.0 / base

	def __request(self, t, content):
		is_hit = False
		q = self.q[content - 1]
		rand = random.random()
		# print rand, q
		if self._is_q and rand >= q:
			if self._cache.has(content):
				is_hit = True
		else:
			if self._cache.get(content):
				is_hit = True
			else:
				self._cache.put(content, t=t, weight=self.weight[content - 1])
		return is_hit

def run_scenario(alpha, cache_ratio):
	# print alpha, cache_ratio
	pop = TruncatedZipfDist(alpha, N_CONTENT)
	# print pop.pdf
	random.seed(SEED)
	weight = [random.choice(DISTANCES) for _ in range(N_CONTENT)]
	# print dis[:5]
	merge_dist = np.multiply(pop.pdf, weight)
	cache_size = int(N_CONTENT*cache_ratio)

	res = {}
	res['LFU'] = [sum(merge_dist[:cache_size])]
	res['Optimal'] = [sum(list(sorted(merge_dist, reverse=True))[:cache_size])]

	for policy in SETTING:
		instance = SingleCachePolicy(cache_size, policy, **SETTING[policy]['cache'])
		instance.init_exp(weight, pop, SEED, **SETTING[policy]['test'])
		res[policy] = [instance.test()]

	return res

def create_scenario():
	scenarios = []
	for alpha in ALPHA:
		scenarios.append((alpha, CACHE_SIZE[2]))
	for cache_ratio in CACHE_SIZE:
		scenarios.append((ALPHA[2], cache_ratio))
	# print len(scenarios)
	scenarios = list(set(scenarios))
	# print len(scenarios)
	for scenario in scenarios:
		scen = {'alpha':scenario[0], 'cache_ratio': scenario[1]}
		for _ in range(N_REPLICATION):
			yield  scen


if __name__ == '__main__':
	columns = ['alpha', 'cache_ratio', 'LFU', 'Optimal',
			   'WLFU', 'WLRU', 'GRD', 'LRU'
			   ]
	data = pd.DataFrame(columns=columns)
	for scenario in create_scenario():
		print scenario
		res = run_scenario(**scenario)
		res.update(dict(map(lambda x: (x[0],[x[1]]), scenario.items())))
		# print pd.DataFrame(res)
		data = data.append(pd.DataFrame(res))
		# print data.head()
		data.to_csv('single_data.csv',index=0)





