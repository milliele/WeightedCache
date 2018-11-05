import numpy as np
import pandas as pd

import matplotlib.pyplot as pyt

STRATEGIES = [
     'LCE',             # Leave Copy Everywhere
     # 'NO_CACHE',        # No caching, shorest-path routing
     # 'HR_SYMM',         # Symmetric hash-routing
     # 'HR_ASYMM',        # Asymmetric hash-routing
     # 'HR_MULTICAST',    # Multicast hash-routing
     # 'HR_HYBRID_AM',    # Hybrid Asymm-Multicast hash-routing
     # 'HR_HYBRID_SM',    # Hybrid Symm-Multicast hash-routing
     # 'CL4M',            # Cache less for more
     'PROB_CACHE',      # ProbCache
     # 'LCD',             # Leave Copy Down
     # 'RAND_CHOICE',     # Random choice: cache in one random cache on path
     # 'RAND_BERNOULLI',  # Random Bernoulli: cache randomly in caches on path
     'WLRU',
     'WLFU',
     'GRD',
	 # 'PD',
             ]

SCEN = {
	'alpha': 'Change Zipf Exponent Alpha',
	'cache_size': 'Change Cache to Population Ratio',
	'std': 'Change Stardard Derivation',
}

STYLE = {
		 'WLRU':         'r-o',
		 'WLFU':        'g-D',
		 'GRD':    'm-^',
		 'PD':    'c-s',
		 'PROB_CACHE':    'r-v',
		 # 'HR_HYBRID_SM':    '',
		 'LCE':             'b--p',
		 # 'LCD':             'g-->',
		 # 'CL4M':            'g-->',
		 # '':      'c--<',
		 # 'RAND_CHOICE':     'r--<',
		 # 'RAND_BERNOULLI':  'g--*',
		 # 'NO_CACHE':        'k:o',
				}

STRATEGY_LABEL = {
		 'WLRU':         'WLRU',
		 'WLFU':        'WLFU',
		'LCE': 'LCE',
		 'GRD':    'GRD',
		 'PD':    'OFFLINE',
		 'PROB_CACHE':    'ProbCache',
		 # 'PD':    'OFFLINE',
}

TOPO = [
	'GEANT',
	'TISCALI',
]


# print results
fig = pyt.figure(figsize=(16, 8))
pyt.subplots_adjust(wspace =0.17, hspace =0.33)
for k, topo in enumerate(TOPO):
	for j, metric in enumerate(SCEN.keys()):
		ax = pyt.subplot(2,3,k*3+j+1)
		ax.yaxis.get_major_formatter().set_powerlimits((0, 1))
		res = pd.read_csv("multi-%s.csv" % metric)
		# print res
		for i, method in enumerate(STRATEGIES):
			data = res.loc[(res['topology']==topo) & (res['strategy']==method)].sort_values(by=metric)
			# print data
			pyt.plot(data[metric], data['weight'], STYLE[method], label=STRATEGY_LABEL[method])
		pyt.xlabel(SCEN[metric])
		pyt.ylabel("Per-request Link Cost")
		pyt.title("(%c) %s" % (chr(ord('a')+j+3*k), "TOPOLOGY = %s" % topo))
		if k+j == 0:
			pyt.legend(loc="upper left", ncol=5, bbox_to_anchor=(0,1.2, 3.1, 0.05), mode='expand')
# pyt.show()
pyt.savefig("multi.pdf", bbox_inches='tight')
pyt.savefig("multi.png", bbox_inches='tight')
pyt.close()
