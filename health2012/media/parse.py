#!/usr/bin/python

arrs = map(lambda x : x.strip().split(','),open('/home/minghen/django/health2012/media/CountingOnUSData.csv').readlines())
print arrs[0:2]
