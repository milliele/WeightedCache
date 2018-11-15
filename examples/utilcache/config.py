# -*- coding:utf-8 -*-

"""This module contains all configuration information used to run simulations
"""
from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

# GENERAL SETTINGS

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'DEBUG'

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = 'OBJECT'

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported 
RESULTS_FORMAT = 'PICKLE'

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 1
M_REPLICATIONS = 8
M_BEGIN = 0

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icaurs/execution/collectors.py
DATA_COLLECTORS = ['WEIGHT']

# Range of alpha values of the Zipf distribution using to generate content requests
# alpha values must be positive. The greater the value the more skewed is the 
# content popularity distribution
# Note: to generate these alpha values, numpy.arange could also be used, but it
# is not recommended because generated numbers may be not those desired. 
# E.g. arange may return 0.799999999999 instead of 0.8. 
# This would give problems while trying to plot the results because if for
# example I wanted to filter experiment with alpha=0.8, experiments with
# alpha = 0.799999999999 would not be recognized 
ALPHA = [0.6, 0.7, 0.8, 0.9]

# Total size of network cache as a fraction of content population
NETWORK_CACHE = [0.004, 0.002, 0.01, 0.05]

# variance
EDGE_WEIGHTS = [10,100,1000]

# Number of content objects
N_CONTENTS = 3*10**5

# Number of requests per second (over the whole network)
NETWORK_REQUEST_RATE = 12.0

# Number of content requests generated to prepopulate the caches
# These requests are not logged
N_WARMUP_REQUESTS = 3*10**6

# Number of content requests generated after the warmup and logged
# to generate results. 
N_MEASURED_REQUESTS = 6*10**6

SEED = 0

# List of all implemented topologies
# Topology implementations are located in ./icarus/scenarios/topology.py
TOPOLOGIES =  [
        'GEANT',
        # 'WIDE',
        # 'GARR',
        'TISCALI',
              ]
# TOPOLOGIES =  [
#         'GEANT',
#         'WIDE',
#         'GARR',
#         'TISCALI',
#               ]

# List of caching and routing strategies
# The code is located in ./icarus/models/strategy.py
STRATEGIES = [
     'LCE-LFU',             # Leave Copy Everywhere
     'LCE-LRU',             # Leave Copy Everywhere
     # 'PROB_CACHE',          # ProbCache
     'WLRU',
     'WLFU',
     'GRD',
	 'NOCACHE',
	 # 'PD',
             ]

# # Cache replacement policy used by the network caches.
# # Supported policies are: 'LRU', 'LFU', 'FIFO', 'RAND' and 'NULL'
# # Cache policy implmentations are located in ./icarus/models/cache.py
CACHE_POLICY = {
    'LCE-LFU': {
         'strategy':{
             'name':'LCE',
         },
         'cache_policy':{
             'name':'PERFECT_LFU',
         },
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS/10,
			 'n_measured': N_MEASURED_REQUESTS/10,
		 }
     },
    'NOCACHE': {
         'strategy':{
             'name':'NO_CACHE',
         },
         'cache_policy':{
             'name':'LRU',
         },
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS/10,
			 'n_measured': N_MEASURED_REQUESTS/10,
		 }
     },
	'LCE-LRU': {
		'strategy': {
			'name': 'LCE',
		},
		'cache_policy': {
			'name': 'LRU',
		},
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS/10,
			 'n_measured': N_MEASURED_REQUESTS/10,
		 }
	},
    'PROB_CACHE': {
         'strategy':{
             'name':'PROB_CACHE',
         },
		 'cache_policy':{
			 'name':'LRU',
		 },
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS/10,
			 'n_measured': N_MEASURED_REQUESTS/10,
		 }
	 },
    'WLRU': {
         'strategy':{
             'name':'Q',
         },
		 'cache_policy':{
			 'name':'LRU',
		 },
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS,
			 'n_measured': N_MEASURED_REQUESTS,
		 }
	 },
    'WLFU': {
         'strategy':{
             'name':'Q',
         },
		 'cache_policy':{
			 'name':'PERFECT_LFU',
		 },
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS,
			 'n_measured': N_MEASURED_REQUESTS,
		 }
	 },
    'GRD': {
         'strategy':{
             'name':'GRD',
         },
		 'cache_policy':{
			 'name':'GRD',
		 },
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS/10,
			 'n_measured': N_MEASURED_REQUESTS/10,
		 }
	 },
	'PD': {
		 'strategy':{
			 'name':'PD',
			 'offline': True,
		 },
		 'cache_policy':{
			 'name':'LRU',
		 },
		 'workload':{
			 'n_warmup': N_WARMUP_REQUESTS,
			 'n_measured': N_MEASURED_REQUESTS,
		 }
	},
}

# Queue of experiments
EXPERIMENT_QUEUE = deque()
default = Tree()
default['workload'] = {'name':       'STATIONARY',
                       'n_contents': N_CONTENTS,
                       'rate':       NETWORK_REQUEST_RATE
                       }
default['cache_placement']['name'] = 'UNIFORM'
default['content_placement']['name'] = 'UNIFORM'
default['topology']['edge_weight'] = EDGE_WEIGHTS
default['strategy']['alpha'] = 0.1
# default['content_placement']['seed'] = SEED
# default['topology']['seed'] = SEED
# default['cache_policy']['name'] = CACHE_POLICY

def generate_scenarios(n_replication, n_begin=M_BEGIN):
	scenarios = []
	for alpha in ALPHA:
		for topology in TOPOLOGIES:
			scenarios.append((alpha, NETWORK_CACHE[-1], topology))

	for network_cache in NETWORK_CACHE:
		for topology in TOPOLOGIES:
			scenarios.append((ALPHA[-1], network_cache, topology))

	scenarios = list(set(scenarios))

	for scenario in scenarios:
		for _ in range(n_begin, n_begin+n_replication):
			yield {'alpha': scenario[0], 'network_cache': scenario[1], 'topology': scenario[2], 'seed': _}


for scenario in generate_scenarios(M_REPLICATIONS):
	for strategy in STRATEGIES:
		experiment = copy.deepcopy(default)
		experiment['workload']['alpha'] = scenario['alpha']
		experiment['content_placement']['seed'] = scenario['seed']
		experiment['topology']['seed'] = scenario['seed']
		experiment['topology']['name'] = scenario['topology']
		experiment['cache_placement']['network_cache'] = scenario['network_cache']

		experiment['strategy'] = CACHE_POLICY[strategy]['strategy']
		experiment['workload']['n_warmup'] = CACHE_POLICY[strategy]['workload']['n_warmup']
		experiment['workload']['n_measured'] = CACHE_POLICY[strategy]['workload']['n_measured']
		experiment['cache_policy']['name'] = CACHE_POLICY[strategy]['cache_policy']['name']

		experiment['label']['name'] = strategy
		experiment['label']['seed'] = scenario['seed']

		experiment['desc'] = "Alpha: %s, strategy: %s, topology: %s, network cache: %s" \
							 % (str(scenario['alpha']), strategy, scenario['topology'], str(scenario['network_cache']))
		EXPERIMENT_QUEUE.append(experiment)
