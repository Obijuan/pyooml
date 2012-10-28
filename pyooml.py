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

        #-- Use the default color
        self.col = ""
        
        #-- Only if an empty string, the col_rgb
        #-- will be used (the str format has priority over rgb)
        self.col_rgb = [2, 2, 2]  #--- [2,2,2] means default color
        
        #-- Object alpha channel
        self.alpha = 1.0
        
        self.debug = False
        self.show_frame = False
        self.show_conns = False
        
        #-- List of connectors
        self.lconns=[]
        
        #-- Parts connected through the conectors
        self.conn_childs = []
        
        #-- Unit vectors of the local frame
        self.uvx = np.array([1,0,0])
        self.uvy = np.array([0,1,0])
        self.uvz = np.array([0,0,1])
        
        #-- Object size (bounding box)
        self.size = size
        
        self.top = np.array([0, 0, self.size[2]/2.])
        self.bottom = np.array([0, 0, -self.size[2]/2.])
        
        self.right = np.array([self.size[0]/2., 0, 0])
        self.left = np.array([-self.size[0]/2., 0, 0])
        
        self.back = np.array([0,self.size[1]/2., 0])
        self.front = np.array([0,-self.size[1]/2., 0])
        
        
    def addconn(self, p, o):
        """Add a connector to the part"""
        conn = (list(p), list(o))
        self.lconns.append(conn)

    def id(self):
        return  "//-- {}".format(self.cmd)

    def Tras(self, vt):
        """Translate function. It returns the same object
        but translated a vetor vt"""
        
        #-- Make a copy of the object
        obj = copy.deepcopy(self)
        
        #-- Calculate the new transformation matrix
        obj.T = self.T.dot( trans.Tras(vt) )
        
        #-- Return the NEW object
        return obj    

    def Rot(self, a, v):
        """Rotate function. It returns the same object
        but Rotated an angle a around the axis given by v"""
        
        #-- Make a copy of the object
        obj = copy.deepcopy(self)

        #-- Calculate the new transformation matrix
        obj.T = self.T.dot( trans.Rot(a, v) )
        
        #-- Return the NEW object
        return obj
        
    def Orien(self, v, vref=[0, 0, 1], roll = 0):
        
        #-- Calculate the rotating axis: raxis = vref x v
        raxis = list(np.cross(vref, v))

        #-- Calculate the angle to rotate vref around rxis
        #-- so that vref = v
        ang = utils.anglev(vref, v)
        
        #-- Special case.. If ang is 0, the same object is return
        if ang == 0.0:
            obj = copy.deepcopy(self)
            return obj
        
        #--Special case... If the rotation angle is 180...
        #-- we should calculate a new rotation axis (because
        #-- it will be 0,0,0, and it is not valid)
        if ang == 180.0:
            a,b,c = vref
            if a != 0:
                raxis = [-b/a, 1, 0]
            elif b != 0:
                raxis = [1, -a/b, 0]
            elif c != 0:
                raxis = [0, 1, -b/c]
            else:
                print "Error! Vref=(0,0,0)"
        
        #-- Create a new object with the given orientation
        obj = self.Rot(roll,v).Rot(ang, raxis)
        
        return obj
        
    def translate(self, pos):
        return translate(self, pos)

    def rotate(self, a, v):
        return rotate(self, a, v)

    #def color(self, c, alpha=1.0):
    #    return color(self, c, alpha)
    
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

    def attach(self, part, roll=0):
        """Attach operator"""
        
        #-- The attached part should have free connectors
        if len(part.lconns) == 0:
            print "Error! Attached Part has no free connectors!"
            return None
            
        #-- The main part should also have free connectors
        if len(self.lconns) == 0:
            print "Error! The main part has no free connectors!"
            return None
        
        #-- Retrieve the next free connectors
        p1,o1 = self.lconns.pop(0)
        p2,o2 = part.lconns[0]
        
        t = list(-np.array(p2))
        fig = part.translate(t)
        fig = fig.Orien(v=o1, vref=o2)
        fig = fig.rotate(a=roll, v=o1)
        fig = fig.translate(p1)
        
        self.conn_childs.append(fig)
        
        return self

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


class translate(part):
    """A translated part"""
    def __init__(self, part, pos):
        #-- Call the parent calls constructor first
        super(translate, self).__init__()

        self.pos = pos
        self.child = part
        self.cmd = "translate({})".format(list(self.pos))

    def scad_gen(self, indent=0):

        cad = "{} {{\n".format(self.cmd) + self.child.scad_gen(indent + 2) + "}"
        #-- Call the super-calls scad_gen method
        return super(translate, self).scad_gen(indent,cad)


class rotate(part):
    """A rotated part"""
    def __init__(self, part, a, axis):
        #-- Call the parent calls constructor first
        super(rotate, self).__init__()

        self.ang = a
        self.axis = axis
        self.child = part
        self.cmd = "rotate(a={0}, v={1})".format(self.ang, self.axis)

    def scad_gen(self, indent=0):

        cad = "{} {{\n".format(self.cmd) + '\n' + self.child.scad_gen(indent + 2) + "}"
        
        #-- Call the super-calls scad_gen method
        return super(rotate, self).scad_gen(indent,cad)
            


from primitive import *
from combinational import *
from operators import *

