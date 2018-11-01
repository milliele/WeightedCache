import numpy as np
import pandas as pd

import matplotlib.pyplot as pyt

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
	'max_gain':{},
	'LFU':{}
}

SCEN = {
	'alpha': 'Zipf Exponent Alpha',
	'cache_size': 'Cache to Population Ratio',
	'std': 'Stardard Derivation',
}

STYLE = {
		 'qLRU':         'b-o',
		 'qLFU':        'g-D',
		 'GRD':    'm--^',
		 'max_gain':    'c-s',
		 'LRU':    'r-v',
		 # 'HR_HYBRID_SM':    '',
		 # 'LCE':             'b--p',
		 # 'LCD':             'g-->',
		 # 'CL4M':            'g-->',
		 # 'PROB_CACHE':      'c--<',
		 # 'RAND_CHOICE':     'r--<',
		 'LFU':  'g--*',
		 # 'NO_CACHE':        'k:o',
				}

STRATEGY_LABEL = {
		 'qLRU':         'WLRU',
		 'qLFU':        'WLFU',
		'LRU': 'LRU',
		 'GRD':    'GRD',
		 'max_gain':    'Optimal',
		'LFU': 'LFU'
}


# print results
fig = pyt.figure(figsize=(16, 4))
for j, metric in enumerate(SCEN.keys()):
	ax = pyt.subplot(1,3,j+1)
	res = pd.read_csv("single_%s.csv" % metric).sort_values(by=metric)
	x = res[metric]
	for i, method in enumerate(SETTING.keys()):
		pyt.plot(x, res[method], STYLE[method], label=STRATEGY_LABEL[method])
	pyt.xlabel(SCEN[metric])
	pyt.ylabel("Caching Gain")
	if j == 0:
		pyt.legend(loc="upper left", ncol=5, bbox_to_anchor=(0,1.07, 3.1, 0.05), mode='expand')
# pyt.show()
pyt.savefig("single.pdf", bbox_inches='tight')
pyt.savefig("single.png", bbox_inches='tight')
pyt.close()
