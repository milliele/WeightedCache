import numpy as np
import pandas as pd

import matplotlib.pyplot as pyt

STRATEGIES = [
     'LCE-LFU',             # Leave Copy Everywhere
     'LCE-LRU',             # Leave Copy Everywhere
     # # 'NO_CACHE',        # No caching, shorest-path routing
     # # 'HR_SYMM',         # Symmetric hash-routing
     # # 'HR_ASYMM',        # Asymmetric hash-routing
     # # 'HR_MULTICAST',    # Multicast hash-routing
     # # 'HR_HYBRID_AM',    # Hybrid Asymm-Multicast hash-routing
     # # 'HR_HYBRID_SM',    # Hybrid Symm-Multicast hash-routing
     # # 'CL4M',            # Cache less for more
     # 'PROB_CACHE',      # ProbCache
     'WLRU',
     'WLFU',
     'GRD',
	 # 'PD',
             ]

SCEN = {
	'alpha': 'Zipf Exponent Alpha',
	'cache_ratio': 'Cache to Population Ratio',
	# 'std': 'Change Stardard Derivation',
}

STYLE = {
		 'WLRU':         'b-o',
		 'WLFU':        'g-D',
		 'GRD':    'm--^',
		 'PD':    'c-s',
		 'LCE-LRU':    'r--v',
		 'LCE-LFU':  'k--*',
		 'PROB_CACHE':  'y--X',
}

STRATEGY_LABEL = {
		 'WLRU':         'WLRU',
		 'WLFU':        'WLFU',
		 'GRD':    'GRD',
		 'PD':    'Offline',
		 'LCE-LRU':    'LCE-LRU',
		 'LCE-LFU':  'LCE-LFU',
		 'PROB_CACHE':  'ProbCache',
}

TOPO = [
	'GEANT',
	'TISCALI',
]


# print results
data = pd.read_csv('multi_data.csv')

fig = pyt.figure(figsize=(16, 4))
pyt.subplots_adjust(wspace=0.3)

for j, metric in enumerate(SCEN.keys()):
	fixed_metric = SCEN.keys()[1 - j]
	fixed_value = data.groupby(fixed_metric).size().argmax()
	for i, topo in enumerate(TOPO):
		ax = pyt.subplot(1,len(SCEN)+len(TOPO),i*len(TOPO)+j+1)
		res = data.loc[(data[fixed_metric] == fixed_value) & (data['topology']==topo)].sort_values(by=metric)
		# print res
		x = res[metric]
		for method in STRATEGIES:
			y = []
			y_up = []
			y_down = []
			for x_value in x:
				screen_out = res.loc[(res[metric]==x_value) & (res['strategy']=='NOCACHE')]['weight'] - \
							 res.loc[(res[metric]==x_value) & (res['strategy']==method)]['weight']
				# print np.mean(screen_out)
				y.append(np.mean(screen_out))
				y_up.append(np.percentile(screen_out,0.95)-y[-1])
				y_down.append(y[-1]-np.percentile(screen_out,0.05))
			pyt.errorbar(x, y, yerr=[y_down,y_up], fmt=STYLE[method], label=STRATEGY_LABEL[method])
		pyt.xlabel(SCEN[metric])
		pyt.ylabel("Caching Gain")
		pyt.title("(%c) Topology=%s" % (chr(ord('a')+i*len(TOPO)+j), topo))
		if j + i == 0:
			pyt.legend(loc="upper left", ncol=5, bbox_to_anchor=(-0.2,1.15, 5, 0.05), mode='expand')
# pyt.show()
pyt.savefig("multi.pdf", bbox_inches='tight')
pyt.savefig("multi.png", bbox_inches='tight')
pyt.close()
