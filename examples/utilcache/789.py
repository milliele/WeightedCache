# -*- coding: utf-8 -*-
import random

p = 0.001

d = 0.6

cnt = 0

sus = 0

eff = 0

while cnt == 0 or abs(1.0*sus/cnt-p)>=0.000001:
	cnt += 1
	if random.random()<p:
		sus +=1
		if random.random()<d:
			eff += 1
	print cnt, 1.0*sus/cnt, 1.0*eff/cnt, 1.0*eff/sus if sus>0 else None
	print abs(1.0 * sus / cnt - p)
