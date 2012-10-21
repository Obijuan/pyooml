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
    
def test_connector_1():
    
    #-- A cube
    size = [10,10,10]
    c = bcube(size)
    
    #-- Create a connector (on the top of the cube)
    conn = connector([0,0,size[2]/2.], [0,0,1])
    conn.debug = True
    
    #-- Show the cube and the connector
    (c + conn).show()
    
def test_frame_1():
    c = cube([10,10,10])
    c.debug = True
    f = frame(l=20)
    
    (f + c).show()


def test_grid_1():
    g = grid()
    g.debug = True
    c = cube([10, 10, 10])
    
    (c + g).show()
    
#--- Main ----
a = cube([50,10,10])
b = cube([10,50,10])
u =  a + b
u2 = u + a
#u2.show()

#test_points()
#test_connector_1()
#test_frame_1()
test_grid_1()



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
