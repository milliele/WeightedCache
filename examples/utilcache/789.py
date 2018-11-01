# -*- coding: utf-8 -*-
import random

p = 0.3

d = 0.6

cnt = 0

sus = 0

eff = 0

while cnt<160:
	cnt += 1
	if random.random()<p:
		sus +=1
		if random.random()<d:
			eff += 1
	print 1.0*sus/cnt, 1.0*eff/cnt, 1.0*eff/sus if sus>0 else None
