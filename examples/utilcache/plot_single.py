import numpy as np
import pandas as pd

import matplotlib.pyplot as pyt

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

SCEN = {
	'alpha': 'Zipf Exponent Alpha',
	'cache_ratio': 'Cache to Population Ratio',
	# 'std': 'Stardard Derivation',
}

STYLE = {
		 'WLRU':         'b-o',
		 'WLFU':        'g-D',
		 'GRD':    'm--^',
		 'Optimal':    'c-s',
		 'LRU':    'r--v',
		 'LFU':  'k--*',
				}

STRATEGY_LABEL = {
		 'WLRU':         'WLRU',
		 'WLFU':        'WLFU',
		'LRU': 'LRU',
		 'GRD':    'GRD',
		 'Optimal':    'Optimal',
		'LFU': 'LFU'
}


# print results
data = pd.read_csv('single_data.csv')

for j, metric in enumerate(SCEN.keys()):
	fig = pyt.figure(figsize=(6, 4))
	# ax = pyt.subplot(2,1,j+1)
	fixed_metric = SCEN.keys()[1-j]
	fixed_value = data.groupby(fixed_metric).size().argmax()

	res = data.loc[data[fixed_metric] == fixed_value].sort_values(by=metric)
	# print res
	x = res[metric]
	for i, method in enumerate(STYLE.keys()):
		y = []
		y_up = []
		y_down = []
		for x_value in x:
			screen_out = res.loc[res[metric]==x_value][method]
			# print np.mean(screen_out)
			y.append(np.mean(screen_out))
			y_up.append(np.percentile(screen_out,0.95)-y[-1])
			y_down.append(y[-1]-np.percentile(screen_out,0.05))
		pyt.errorbar(x, y, yerr=[y_down,y_up], fmt=STYLE[method], label=STRATEGY_LABEL[method])
	pyt.xlabel(SCEN[metric])
	pyt.ylabel("Caching Gain")
	# pyt.title("(%c) Fixed %s=%.3f" % (chr(ord('a')+j), fixed_metric.replace('_', ' '), fixed_value))
	if j == 0:
		pyt.legend(loc="upper left", ncol=3, bbox_to_anchor=(0,1.15, 1., 0.05), mode='expand')
	# pyt.show()
	pyt.savefig("single-%s.pdf" % metric, bbox_inches='tight')
	pyt.savefig("single-%s.png" % metric, bbox_inches='tight')
	pyt.close()
