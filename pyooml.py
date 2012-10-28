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
import utils
import copy
import transformations as trans


Z = 2

class part(object):
    """Class for defining an object. This class is virtual"""

    def __init__(self, size=[0, 0, 0]):
        
        #-- Object transformation matrix
        #-- It defines its position and orientation
        self.T = trans.Identity()

        #-- Set the default color parameters, it they had not been
        #-- already set by the subclases
        try:
            self.col
        except AttributeError:     
          #-- An empty string means the default color
          self.col = ""
        
        try:
            self.col_rgb
        except AttributeError: 
            #-- Only if an empty string, the col_rgb
            #-- will be used (the str format has priority over rgb)
            self.col_rgb = [2, 2, 2]  #--- [2,2,2] means default color
        
        try:
            self.alpha
        except AttributeError:     
            #-- Object alpha channel
            self.alpha = 1.0
        
        self.debug = False
        self.show_frame = False
        
        #-- Object size (bounding box)
        self.size = size

    def id(self):
        return  "//-- {}".format(self.cmd)

    def Tras(self, vt):
        """Translate function. It returns the same object
        but translated a vetor vt (ABSOLUTE TRANSLATION)"""
        
        #-- Make a copy of the object
        obj = copy.deepcopy(self)
        
        #-- Calculate the new transformation matrix
        obj.T[0,3] += vt[0]
        obj.T[1,3] += vt[1]
        obj.T[2,3] += vt[2]
        
        #-- Return the NEW object
        return obj    

    def Rot(self, a, v):
        """Rotate function. It returns the same object
        but Rotated an angle a around the axis given by v
        (ABSOLUTE ROTATION)"""
        
        #-- Make a copy of the object
        obj = copy.deepcopy(self)

        #-- Calculate the new transformation matrix
        obj.T = trans.Rot(a,v).dot(self.T)
        
        #-- Return the NEW object
        return obj
        
    def Orien(self, v, vref=[0., 0., 1.], roll = 0.):
        
        #-- Calculate the rotating axis: raxis = vref x v
        raxis = list(np.cross(vref, v))

        #-- Calculate the angle to rotate vref around rxis
        #-- so that vref = v
        ang = utils.anglev(vref, v)
        
        #-- Special case.. If ang is 0 is because vref and v are paralell
        #-- Only the roll angle have to be applied
        #-- Give raxis a random value (it should be != [0,0,0]
        if ang == 0.0:
            raxis = [0,0,1]
        
        #--Special case... If the rotation angle is 180...
        #-- we should calculate a new rotation axis (because
        #-- it will be 0,0,0, and it is not valid)
        if ang == 180.0:
            a,b,c = vref
            if a != 0.:
                raxis = [-b/a, 1., 0.]
            elif b != 0.:
                raxis = [1., -a/b, 0.]
            elif c != 0.:
                raxis = [0., 1., -b/c]
            else:
                print "Error! Vref=(0,0,0)"
        
        #-- Create a new object with the given orientation
        obj = self.Rot(ang, raxis).Rot(roll,v)
        
        return obj

    def Move(self, pt, ot = [0., 0., 1.], ps = [0., 0., 0.], os = [0., 0., 1.], ang = 0.):
        
        #--- Convert the vectors into arrays
        pt = np.array(pt)
        ot = np.array(ot)
        ps = np.array(ps)
        os = np.array(os)
        
        #-- Fist, translate the objet to the origin
        obj = self.Tras(-ps)
        
        #--- Set the new object orientation
        obj = obj.Orien(v=ot, vref = os, roll = ang)
        
        #-- Translate the object to the target position
        obj = obj.Tras(pt)
        
        return obj
        
    def color(self, c, alpha = 1.0):
        """Create a copy of the object in a different color"""
        
        #-- Determine how the user passes the arguments
        #-- By string ("Blue", "Yellow"...) or by list (r,g,b)
        if isinstance(c, str):
            col = c            #-- is a string
        else:
            c = list(c)  #-- Otherwise it should be a list
            col = ""
            
        #-- Make a copy of the object
        obj = copy.deepcopy(self)
        
        #-- Change the color
        obj.col = col
        obj.c = c
        obj.alpha = alpha
        
        #-- Return the new object
        return obj

    # overload +
    def __add__(self, other):
        return union([self, other])

    #-- Overload - operator
    def __sub__(self, other):
        return difference([self, other])
    
    def scad_gen(self, indent=0, cmd=""):
        
        #-- Initial string
        cad = " " * indent
        
        
        #-- Get the object matrix as a list
        T = [list(v) for v in self.T]
        
        cad = self.id()+'\n'
        cad += "multmatrix(m={0}) {{".format(T) 
        
        #-- Add the Frame of reference
        if self.show_frame:
          cad += frame().scad_gen() 
        
        #-- Add the debug mode
        if self.debug:
            cad += '%'

            
        #----- Color managment
        if self.col == "" and self.col_rgb == [2, 2, 2]:
            #-- No color
            cad += cmd + '\n'
            
        else:
            #-- Color given..
            
            #-- Get the color argument
            if self.col == "":
                color_arg = "{0}".format(list(self.col_rgb))
            else:
                color_arg = '"{0}"'.format(self.col)
        
            #-- Calculate the final color argument
            color_cmd = 'color({0},{1})'.format(color_arg, self.alpha)
            
            cad += color_cmd + '{\n' + cmd + '\n}\n'

        cad += "}\n"  #-- Close the multimatrix bracket
        
        #-- Attached parts
        #for ap in self.conn_childs:
        #    cad += ap.scad_gen(indent+2)

        #-- List of connectos
        #for conn in self.lconns:
        #    p,o = conn  #-- Get the position and orientation vectors
        #    cad += connector(p,o).scad_gen(indent+2)
        
        return cad

    #-- This method is used for optimizacion
    def is_union(self):
        return False

    def render(self, indent=0):
        print self.scad_gen(indent)

    def show(self):
        f = open("test.scad", "w")

        code = self.scad_gen()

        f.write(code)

        f.close()


from primitive import *
from combinational import *
from operators import *

