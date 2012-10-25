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
        
    def translate(self, pos):
        return translate(self, pos)

    def rotate(self, a, v):
        return rotate(self, a, v)

    def orientate(self, v, vref=[0, 0, 1], roll=0):
        return orientate(self, v, vref, roll)

    def color(self, c, alpha=1.0):
        return color(self, c, alpha)
        
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
        fig = fig.orientate(v=o1, vref=o2)
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
        
        #-- Add the debug mode
        if self.debug:
            cad += '%'
            
        cad += cmd + '\n'
        
        #-- Add the Frame of reference
        if self.show_frame:
          cad += frame().scad_gen() 
        
        cad += "}\n"
        
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
        

class color(part):
    """Operator: add color"""
    def __init__(self, part, c, alpha=1.0):
        #-- The color can be give either by a str or by a vector (R,G,B)

        #-- Call the parent calls constructor first
        super(color, self).__init__()
        
        #-- The color
        if isinstance(c, str):
            self.c = '"{0}"'.format(c)
        else:
            self.c = list(c)
        self.alpha = alpha
        self.child = part
        self.cmd = 'color({0},{1})'.format(self.c,alpha)
        
    def scad_gen(self, indent=0):
        cad = format(self.cmd) + '\n' + self.child.scad_gen(indent + 2)
        #-- Call the super-calls scad_gen method
        return super(color, self).scad_gen(indent,cad)
        
class union(part):
    """A group of parts"""
    def __init__(self, list_parts):
        #-- Call the parent calls constructor first
        super(union, self).__init__()

        self.lparts = list_parts
        self.cmd = "union()"

    #def __add__(self, other):
        #-- Optimizacion: if the second argument is an
        #-- Union too.. incorporate their childs into the
        #-- union list

        #-- Create list of child objects of the new union
        #-- (A copy of the current union)
        #lparts = [p for p in self.lparts]

        #-- If the new object is a union, just added their childs
        #-- (not the union itself)
        #if other.is_union():
            #-- Union + union
        #    lparts.extend(other.lparts)
        #else:
            #-- Union + other part (not union)
         #   lparts.extend([other])

        #return union(lparts)

    def scad_gen(self, indent=0):

        cad = "{0} {{\n".format(self.cmd)
        childs_cad = [part.scad_gen(indent + 2) for part in self.lparts]
        cad = cad + "".join(childs_cad)
        cad = cad + " " * indent + "}\n"
        
        #-- Call the super-calls scad_gen method
        return super(union, self).scad_gen(indent, cad)

    def is_union(self):
        return True


class difference(part):
    """Difference operator"""
    def __init__(self, list_parts):
        #-- Call the parent calls constructor first
        super(difference, self).__init__()

        self.lparts = list_parts
        self.cmd = "difference()"
        
    def id(self):
        print "//-- {}".format(self.cmd)
        
    def scad_gen(self, indent=0):
        

        cad = "{0} {{\n".format(self.cmd)
        childs_cad = [part.scad_gen(indent + 2) for part in self.lparts]
        cad = cad + "".join(childs_cad)
        cad = cad + " " * indent + "}\n"
        
        #-- Call the super-calls scad_gen method
        return super(difference, self).scad_gen(indent,cad)
            

class orientate(part):
    """Orientate operator"""

    def __init__(self, part, v, vref=[0, 0, 1], roll=0):
        #-- Call the parent calls constructor first
        super(orientate, self).__init__()

        self.vref = vref
        self.v = v
        self.child = part
        self.roll = roll
        self.cmd = "orientate(vref={0},v={1}, roll={2})".format(self.vref,
                                                     self.v,
                                                     self.roll)

        #-- Rotation axis
        self.raxis = list(np.cross(vref, v))

        #-- Angle to rotate
        self.ang = utils.anglev(vref, v)
        
        #--Special case... If the rotation angle is 180...
        #-- we should calculate a new rotation axis (because
        #-- it will be 0,0,0, and it is not valid)
        if self.ang == 180.0:
            a,b,c = vref
            if a != 0:
                self.raxis = [-b/a, 1, 0]
            elif b != 0:
                self.raxis = [1, -a/b, 0]
            elif c != 0:
                self.raxis = [0, 1, -b/c]
            else:
                print "Error! Vref=(0,0,0)"

        #-- Child expresion
        self.expr = self._expr()

    def scad_gen(self, indent=0):
        
        cad = self.expr.scad_gen(indent)
        
        #-- Call the super-calls scad_gen method
        return super(orientate, self).scad_gen(indent, cad)

    def _expr(self):

        #-- rotate the part so that it points in the v direction
        fig = part.rotate(self.child, a=self.ang, v=self.raxis)

        #-- Apply the roll and return
        return fig.rotate(a=self.roll, v=self.v)


class minkowski(part):
    """Minkowski operator"""
    def __init__(self, childs):
        #-- Call the parent calls constructor first
        super(minkowski, self).__init__()

        self.childs = childs
        self.cmd = "minkowski()"

    def scad_gen(self, indent=0):
        
        cad = self.cmd + "{\n"
        childs_cad = [part.scad_gen(indent + 2) for part in self.childs]
        cad += "".join(childs_cad)
        cad += " " * indent + "}\n"
        
        #-- Call the super-calls scad_gen method
        return super(minkowski, self).scad_gen(indent, cad)

from primitive import *
from combinational import *
        
class point(part):
    """A point"""
    def __init__(self, p, diam=2):
        """A point"""
        #-- Call the parent calls constructor first
        super(point, self).__init__()
        
        self.p = list(p)
        self.diam = 2
        self.cmd = "point(p={0}, diam={1})".format(p,diam)
        self.expr = self._expr()
        
    def id(self):
        print "//-- {}".format(self.cmd)
        
    def scad_gen(self, indent=0):

        cad = self.expr.scad_gen(indent)
        #-- Call the super-calls scad_gen method
        return super(point, self).scad_gen(indent, cad)
        
    def _expr(self):
        """Build the object"""  
        return sphere(self.diam/2.).translate(self.p)
        

class connector(part):
    """Graphical connector"""
    def __init__(self, p, o):
        """Arguments: p: connector position (vector)
                      o: connector orientation (vector)
        """
        #-- Call the parent calls constructor first
        super(connector, self).__init__()
        
        self.p = list(p)
        self.o = list(o)
        self.def_color = "gray"
        self.l = 6 #-- default length
        self.l_arrow = 2 #-- default arrow length
        self.cmd = "connector(p={0}, o={1})".format(p,o)
        self.expr = self._expr()
        
    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        

        cad = self.expr.scad_gen(indent)
        
        #-- Call the super-calls scad_gen method
        return super(connector, self).scad_gen(indent,cad)
        
    def _expr(self):
        
        p = point(self.p)
        vec = vectorz(l=self.l, l_arrow=self.l_arrow).orientate(self.o)
        
        conn = (vec.translate(self.p) + p).color(self.def_color)

        return conn


class grid(part):
    def __init__(self, size=[100, 100], step=10, width = 0.5):
        #-- Call the parent calls constructor first
        super(grid, self).__init__()
        
        self.gsize = size
        self.step = step
        self.width = width
        self.cmd = "grid(size={0}, step={1}, width={2})".format(size,step,width)
        self.expr = self._expr()
        self.debug = False
        
    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        #-- Call the super-class scad_gen method
        cad = super(grid, self).scad_gen(indent)

        cad += self.expr.scad_gen(indent)
        return cad
        
    def _expr(self):
        linex = cube([self.gsize[0], self.width, self.width])
        sx,sy = self.gsize
        lx = [linex.translate([0,y,0]) for y in range(-sy/2, sy/2+self.step, self.step)]
        lx = union(lx)
        fig = (lx + lx.rotate(a=90, v=[0,0,1]))
        return fig.color("Gray")

