#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyooml import *


a = cube([50,10,10])
b = cube([10,50,10])
u =  a + b
u2 = u + a

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
