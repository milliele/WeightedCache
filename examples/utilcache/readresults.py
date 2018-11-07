#!/usr/bin/env python
"""Plot results read from a result set
"""
from __future__ import division
import os
import argparse
import collections
import logging

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from icarus.util import Settings, Tree, config_logging, step_cdf
from icarus.tools import means_confidence_interval
from icarus.results import plot_lines, plot_bar_chart
from icarus.registry import RESULTS_READER


# Logger object
logger = logging.getLogger('plot')

res_paths = {
	'param': {
		# alpha, cache_size, topology, strategy
		'alpha': ('workload', 'alpha'),
		'cache_ratio': ('cache_placement', 'network_cache'),
		'topology': ('topology', 'name'),
		'strategy': ('label','name'),
		'round': ('label','seed'),
		# 'walpha': ('strategy', 'alpha'),
	},
	'res': {
		'weight': ('WEIGHT','MEAN'),
	},
}

def run(results):
	"""Run the plot script

	Parameters
	----------
	config : str
		The path of the configuration file
	results : str
		The file storing the experiment results
	plotdir : str
		The directory into which graphs will be saved
	"""
	resultset = RESULTS_READER['PICKLE'](results)
	data = pd.DataFrame()
	for result in resultset:
		param, res = result
		one = {}
		for k in res_paths['param']:
			one[k]=[param.getval(res_paths['param'][k])]
		for k in res_paths['res']:
			one[k]=[res.getval(res_paths['res'][k])]
		data = pd.DataFrame(one).append(data)
		data.to_csv('multi_data.csv', index=0)


def main():
	parser = argparse.ArgumentParser(__doc__)
	parser.add_argument("-r", "--results", dest="results",
						help='the results file',
						required=True)
	args = parser.parse_args()
	run(args.results)

if __name__ == '__main__':
	main()
