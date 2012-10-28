#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyooml import *
from primitive import *
from combinational import *
import servos
import math


def test_points():
    N=50  #-- Number of points
    
    #-- Get a list of points
    l = [point([x, 20 * math.sin(2 * math.pi * x / float(N)), 0])
         for x in range(-N, N)]
    
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

def test_attach_1():
    c = cube([30,20,30])
    c.addconn([-15,0,5],[-1,0,0])
    c.addconn([15,0,5],[1,0,0])

    c2 = cube([10,50,10])
    c2.addconn([5, 20,0],[-1,0,0])
    c2.debug=True

    c.attach(c2)
    c.attach(c2,30)
    c.show()


def test_relative_pos_1():
    c = cube([50,30,50])
    c.debug = True
    c.show_frame=True
    p = point(c.top + c.right + c.back).color("Magenta")
    (c+p).show()
    
def test_difference_1():
    c1 = cube([50,50,10])
    c2 = cylinder(r=3, h=c1.size[2]+10)
    (c1-c2).show()

def servo_ring(servo):
    
    thick_z = 4
    thick_xy = servo.ear_size[0] + 4
    tolerance = 0.2
    
    #-- Get the servo body dimensions
    sx, sy, sz = servo.body_size + np.array([tolerance, tolerance, 0])
    
    #-- Cutout: servo body + tolerance
    cutout = bcube([sx, sy, sz],cr = servo.body_cr, cres = servo.body_cres)
    
    #-- Add the tolerance to the 
    
    obj = bcube([sx + 2*thick_xy + 2*tolerance, sy + thick_xy + 2*tolerance, thick_z])
    
    return (obj - cutout - servo.drills(dh=10)).Tras([0,0,-thick_z/2 + servo.ear_hi_center])

def test_servo_ring_1():
    
    #-- Create a "ring" part for the first servo
    s1 = servos.Futaba3003()
    sr1 = servo_ring(s1)

    #-- Create a "ring" for another servo
    s2 = servos.TowerProSG90()
    sr2 = servo_ring(s2)

    #-- Show the objetcs (servos + rings)
    obj1 = (sr1 + s1).Tras([0, 30, s1.body_size[2]/2.])
    obj2 = (sr2 + s2).Tras([0, -30, s2.body_size[2]/2.0])

    (obj1 + obj2).show()

def mark(p, o=[0,0,1], roll=0):
    f = frame(l=5, l_arrow=2).Orien(v=o, roll=roll).Tras(p)
    return f
#--- Main ----

#test_points()
#test_connector_1()
#test_frame_1()
#test_grid_1()
#test_relative_pos_1()
#test_difference_1()
#test_servo_ring_1()


#test_attach_1()

ct = cube([20,20,20])
#ct.debug = True
#ct.show_frame = True
pt = [-10,0,0]
ot = [-1, 0, 0]

pt2 = [10,0,0]
ot2 = [1, 0, 0]

mt = mark(p=pt, o=ot)
obt = (ct + mt)

cs = cube([5, 30, 10])
ps = [-5/2., 10, 0]
os = [1,0,0]
cs.debug = True
ms = mark(p=ps, o=os)
obs = (cs + ms)

a = (cs + ms).Move(pt = pt, ot = ot, ps = ps, os = os, ang=30)
b = (cs + ms).Move(pt = pt2, ot = ot2, ps = ps, os = os, ang=30)

(a + b + obt).show()



#mt = vector(ot).Tras(pt)
#ms = vector(os).Tras(ps)

#(body + mt).show()

#(body + c.Move(pt = pt, ot = ot, ps = ps, os = os) + ms + mt).show()



#(body + point(pt).color("magenta")).show()


#s1 = servos.Futaba3003()
#s1.debug=True
#s2 = servos.TowerProSG90()
#(s1.Tras([0, 50, 0]) + s2).show()

