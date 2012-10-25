#-------------------------------------------------------------
#-- Pyooml: Python Object Oriented Mechanics Library
#-------------------------------------------------------------
#-- (c)  Juan Gonzalez-Gomez  (Obijuan)
#-- (c)  Alberto Valero
#-- October-2012
#-------------------------------------------------------------
#-- GPL licence
#-------------------------------------------------------------
import numpy as np
from pyooml import *

class primitive(part):
    """Primitive objects. Simple geometries"""
    
    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        
        return super(primitive, self).scad_gen(indent, self.cmd)


class cube(primitive):
    """Primitive part: A cube"""
    
    def __init__(self, size):
        
        #-- Openscad command
        self.cmd = "cube({},center=true);".format(size)
        self.size = size
        
        #-- Call the parent class constructor first
        super(cube, self).__init__(size)


class cylinder(primitive):
    def __init__(self, h, r, res=20):
        self.r = r
        self.h = h
        self.size = [2 * r, 2 * r, h]
        self.cmd = (
        "cylinder(r={0}, h={1}, $fn={2},center=true);".format(r, h, res))
            
        #-- Call the parent class constructor
        super(cylinder, self).__init__(size = self.size)

class cone(primitive):
    def __init__(self, h, r1, r2, res=20):
        self.r1 = r1
        self.r2 = r2
        self.r = 0
        self.h = h
        m = max([r1, r2])
        self.size = [m, m, h]
        cmd = "cylinder(r1={0}, r2={1},h={2}, $fn={3}, center=true);"
        self.cmd = cmd.format(r1, r2, h, res)
            
        #-- Call the parent class constructor
        super(cone, self).__init__(size = self.size)

class sphere(primitive):
    """A sphere"""
    def __init__(self, r, res=40):

        self.res = res
        self.r = r
        self.size = [2 * r, 2 * r, 2 * r]
        self.cmd = "sphere({0}, $fn={1});".format(self.r, self.res)
    
        #-- Call the parent calls constructor first
        super(sphere, self).__init__(size = self.size)

