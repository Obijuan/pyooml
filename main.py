#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyooml import *
import math


def test_points():
    N=50  #-- Number of points
    
    #-- Get a list of points
    l = [point([x, 20 * math.sin(2 * math.pi * x / float(N)), 0]) for x in range(-N, N)]
    
    #-- Join al the points with a union
    fig = union(l)
    
    #-- Show
    fig.show()
    
    
#--- Main ----
a = cube([50,10,10])
b = cube([10,50,10])
u =  a + b
u2 = u + a
#u2.show()

test_points()

"""
a = cube([10,10,10]).translate([10,0,0])
b = cube([10,10,10])
#t = translate(a, [10,0,0])
#a.id()
u = union([a,b]).translate([20,0,0])
c = (b+b+b+b+b+b+b+b) + (b+b)

c = (cube([50,10,10]) + cube([10,50,10]) + cube([10,10,40])).translate([0,0,10])

c.render()
"""
