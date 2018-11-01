# -*- coding:utf-8 -*-

import random
from icarus.models.cache import *
from icarus.tools.stats import TruncatedZipfDist
import numpy as np
from icarus.registry import *
import collections


N_CONTENT = 3*10**4
# CACHE_SIZE = [0.1,]
CACHE_SIZE = [0.001, 0.005, 0.01, 0.05, 0.1]
ALPHA = [0.6,0.7,0.8,0.9,1.0]
# variance
STD = np.logspace(2, 4, 5)
# print STD
AVG = max(STD)*3+1 # 3-sita policy
# AVG = 10**4


N_WARMUP = 3*10**5
N_MEASURE = 3*10**5
SEED = 0
RATE = 12

SETTING = {
	'GRD': {
		'policy': 'GRD',
		'is_q': False,
	},
	'qLRU': {
		'policy': 'LRU',
		'is_q': True,
			 },
	'qLFU': {
		'policy': 'PERFECT_LFU',
		'is_q': True,
			 },
	'LRU': {
		'policy': 'LRU',
		'is_q': False,
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

class TestPolicy(object):
	def __init__(self, cache_size, policy, is_q, **kwargs):
		self._cache = CACHE_POLICY[policy](cache_size, **kwargs)
		self.poli = policy
		self._is_q = is_q
		self._hit = 0
		self._base = 0

	def request(self, t, content, log):
		self.is_hit = False
		if self._is_q:
			q = qs[content-1]
			if random.random()<q:
				if self._cache.get(content):
					self.is_hit = True
				else:
					self._cache.put(content, t=t, weight=dis[content-1])
			else:
				if self._cache.has(content):
					self.is_hit = True
		else:
			if self._cache.get(content):
				self.is_hit = True
			else:
				self._cache.put(content, t=t, weight=dis[content - 1])
		if log:
			self._base += 1
			if self.is_hit:
				self._hit += dis[content-1]

	def result(self):
		return self._hit*1.0/self._base

def change_cache_size(filename, setting):
	fobj = open("single_%s.csv" %filename, "w+")
	fobj.write("%s,max_gain,LFU" % filename)
	for k in setting:
		fobj.write(",%s" % k)
	fobj.write('\n')
	fobj.close()
	for ratio in CACHE_SIZE:
		print "%s = %f" %(filename, ratio)
		cache_size = int(N_CONTENT * ratio)
		testcases = {k: TestPolicy(cache_size, **v) for k, v in setting.iteritems()}

		global dist, dis, merge_dist, qs
		random.seed(SEED)
		np.random.seed(SEED)
		dist = TruncatedZipfDist(ALPHA[2], N_CONTENT)
		weight_dis = range(N_CONTENT)
		np.random.shuffle(weight_dis)
		dis = [dist.pdf[weight_dis[_]] * 10 ** 8 for _ in range(N_CONTENT)]
		# print dis[:5]
		merge_dist = np.multiply(dist.pdf, dis)
		# sort_list = merge_dist.argsort()
		max_dis = max(dis)
		qs = np.array(dis) * 1.0 / max_dis

		cnt = 0
		t = 0.0

		while cnt < N_WARMUP + N_MEASURE:
			t += (random.expovariate(RATE))
			content = int(dist.rv())
			log = (cnt >= N_WARMUP)
			event = {'t': t, 'content': content, 'log': log}
			for poli, testcase in testcases.iteritems():
				# print cnt, ratio, poli
				testcase.request(**event)
			cnt += 1

		fobj = open("single_%s.csv" %filename, "a+")
		LFU = sum(merge_dist[:cache_size])
		max_gain = sum(sorted(merge_dist, reverse=True)[:cache_size])
		fobj.write("%f,%.2f,%.2f" % (ratio, max_gain, LFU))
		for k in setting:
			fobj.write(",%.2f" % testcases[k].result())
		fobj.write('\n')
		fobj.close()

def change_alpha(filename, setting):
	fobj = open("single_%s.csv" %filename, "w+")
	fobj.write("%s,max_gain,LFU" % filename)
	for k in setting:
		fobj.write(",%s" % k)
	fobj.write('\n')
	fobj.close()
	for alpha in ALPHA:
		print "%s = %f" %(filename, alpha)
		cache_size = int(N_CONTENT * CACHE_SIZE[2])
		testcases = {k: TestPolicy(cache_size, **v) for k, v in setting.iteritems()}

		global dist, dis, merge_dist, qs
		random.seed(SEED)
		np.random.seed(SEED)
		dist = TruncatedZipfDist(alpha, N_CONTENT)
		weight_dis = range(N_CONTENT)
		np.random.shuffle(weight_dis)
		dis = [dist.pdf[weight_dis[_]]*10**8 for _ in range(N_CONTENT)]
		# print dis[:5]
		merge_dist = np.multiply(dist.pdf, dis)
		# print merge_dist[:5], dist.pdf[:5]
		# sort_list = merge_dist.argsort()
		max_dis = max(dis)
		qs = np.array(dis) * 1.0 / max_dis

		cnt = 0
		t = 0.0

		while cnt < N_WARMUP + N_MEASURE:
			t += (random.expovariate(RATE))
			content = int(dist.rv())
			log = (cnt >= N_WARMUP)
			event = {'t': t, 'content': content, 'log': log}
			for poli, testcase in testcases.iteritems():
				# print cnt, ratio, poli
				testcase.request(**event)
			cnt += 1

		fobj = open("single_%s.csv" %filename, "a+")
		LFU = sum(merge_dist[:cache_size])
		max_gain = sum(sorted(merge_dist, reverse=True)[:cache_size])
		fobj.write("%f,%.2f,%.2f" % (alpha, max_gain, LFU))
		for k in setting:
			fobj.write(",%.2f" % testcases[k].result())
		fobj.write('\n')
		fobj.close()

def change_std(filename, setting):
	fobj = open("single_%s.csv" %filename, "w+")
	fobj.write("%s,max_gain,LFU" % filename)
	for k in setting:
		fobj.write(",%s" % k)
	fobj.write('\n')
	fobj.close()
	for std in STD:
		print "%s = %f" %(filename, std)
		cache_size = int(N_CONTENT * CACHE_SIZE[2])
		testcases = {k: TestPolicy(cache_size, **v) for k, v in setting.iteritems()}

		global dist, dis, merge_dist, qs
		random.seed(SEED)
		np.random.seed(SEED)
		dist = TruncatedZipfDist(ALPHA[2], N_CONTENT)
		weight_dis = range(N_CONTENT)
		np.random.shuffle(weight_dis)
		dis = [dist.pdf[weight_dis[_]] * 10 ** 8 for _ in range(N_CONTENT)]
		# print dis[:5]
		merge_dist = np.multiply(dist.pdf, dis)
		# sort_list = merge_dist.argsort()
		max_dis = max(dis)
		qs = np.array(dis) * 1.0 / max_dis

		cnt = 0
		t = 0.0

		while cnt < N_WARMUP + N_MEASURE:
			t += (random.expovariate(RATE))
			content = int(dist.rv())
			log = (cnt >= N_WARMUP)
			event = {'t': t, 'content': content, 'log': log}
			for poli, testcase in testcases.iteritems():
				# print cnt, ratio, poli
				testcase.request(**event)
			cnt += 1

		fobj = open("single_%s.csv" %filename, "a+")
		LFU = sum(merge_dist[:cache_size])
		max_gain = sum(sorted(merge_dist, reverse=True)[:cache_size])
		fobj.write("%f,%.2f,%.2f" % (std, max_gain,LFU))
		for k in setting:
			fobj.write(",%.2f" % testcases[k].result())
		fobj.write('\n')
		fobj.close()

if __name__ == '__main__':
	SETTING = collections.OrderedDict(SETTING)
	change_alpha('alpha', SETTING)
	change_cache_size('cache_size', SETTING)
	change_std('std', SETTING)

