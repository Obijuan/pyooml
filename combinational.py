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

class combinational(part):
    def scad_gen(self, indent=0):

        #-- Get the object geometry
        cad = self._geometry().scad_gen(indent)
        
        #-- Call the super-class scad_gen method
        return super(combinational, self).scad_gen(indent,cad)


class vector(combinational):
    """a 3D Vector!!"""

    def __init__(self, v, l_arrow = 4, mark = False):
        """
        v : vector components
        l_arrow: Arrow length
        mark: Show a mark in the arrow, for showing the rotaing angle
        """

        self.l = np.linalg.norm(v)  #-- Vector length
        self.l_arrow = l_arrow
        self.mark = mark
        self.size = [1, 1, self.l]
        self.v = v
        self.cmd = "vector([{0}], l_arrow={1}, mark={2}".format(list(v),
                                                                l_arrow,
                                                                 mark)

        #-- Call the parent class constructor first
        super(vector, self).__init__(self.size)

    def _geometry(self):
        """Build the vector geometry (combinational part)"""

        #-- Draw the vector body
        #-- vector body length (not including the arrow)
        lb = self.l - self.l_arrow

        #----- Create the vector parts: Head, body, base and mark (optional)
        head = cone(r1 = 2 / 2, r2 = 0.2, h = self.l_arrow, res = 20)
        body = cylinder(r= 1 / 2., h = lb, res = 20)
        base = sphere(r = 1 / 2., res = 20)
        mark = cube([2, 0.3, self.l_arrow * 0.8])

        #------ Translation vector

        #-- vector for moving the arrow to the top of the body
        atop = [0, 0, self.l_arrow / 2 + lb / 2.]
        
        #-- Vector for placing the mark on the top of the vector body
        mtop = [1, 0, self.l_arrow * 0.8 / 2. + lb / 2.]
        
        #-- Vector for placing the application point in the origin
        vorig = [0, 0, lb / 2.]
        
        #----- Build the vector
        vec = head.Tras(atop) + body

        #-- Add the optional mark
        if self.mark:
            vec += mark.Tras(mtop)
            
        #-- Place the vector with the application point in the origin
        #-- Add the base in the origin
        obj = vec.Tras(vorig) + base
        
        #-- The current vector is pointing in z direction
        #-- Orientate it to the v direction
        vo = obj.Orien(self.v)

        return vo


class frame(combinational):
    def __init__(self, l=10, l_arrow=4):
        
        self.l = l
        self.l_arrow = l_arrow
        self.size = [l, l, l]
        self.cmd = "frame(l={0}, l_arrow={1})".format(l, l_arrow)

        #-- Call the parent class constructor first
        super(frame, self).__init__(self.size)
        
    def _geometry(self):
        z_axis = vector([0, 0, self.l], l_arrow=self.l_arrow).color("Blue")
        x_axis = vector([self.l, 0, 0], l_arrow=self.l_arrow).color("Red")
        y_axis = vector([0, self.l, 0], l_arrow=self.l_arrow).color("Green")
        fig = x_axis + y_axis + z_axis + sphere(r=1).color("Gray")
        return fig

from operators import *
        
class bcube(combinational):
    """Beveled cube"""

    def __init__(self, size, cr = 2, cres = 5):

        #-- Initialize the object
        self.cr = cr
        self.cres = cres
        self.cmd = "bcube({0},cr={1}, cres={2});".format(size, cr, cres)
        
        #-- Call the parent calls constructor
        super(bcube, self).__init__(size)

    def _geometry(self):
        """Expresion for building the object"""

        #-- if cr is 0, means a standar cube
        if (self.cr == 0):
            return cube(self.size)

        #-- Make sure the corner radius is not too big
        if self.cr > min([self.size[0], self.size[1]]) / 2.:
            self.cr = min([self.size[0], self.size[1]]) / 2.

        #-- Get the internal cube size
        sx, sy, sz = bsize = list(np.array(self.size) -
                   2 * np.array([self.cr, self.cr, 0]))

        #-- The cube cannot have lengths equal to 0
        if sx == 0:
            sx = 0.001

        if sy == 0:
            sy = 0.001

        #-- Use a cylinder for rounding. 
        cyl = cylinder(r = self.cr, h = sz / 2.,
                       res = 4 * (self.cres + 1))

        #--  Place it at the first quadrant                                              
        cyl = cyl.Tras([sx / 2.,sy / 2., 0])

        #-- Apply the minkowski operator
        obj = minkowski([cyl, cube([sx, sy, sz / 2.])])
        
        #-- Move the resulting object to the origin
        obj = obj.Tras([-sx / 2., -sy / 2., 0])
        
        return obj


class point(combinational):
    """A point"""
    def __init__(self, p, diam=2):
        """A point"""
        
        self.p = p
        self.diam = 2
        self.size=[diam, diam, diam]
        self.cmd = "point(p={0}, diam={1})".format(list(p),diam)
        
        #-- Call the parent clasa constructor first
        super(point, self).__init__(self.size)
        
        
    def _geometry(self):
        """Build the object"""  
        return sphere(self.diam/2.).Tras(self.p)
        
        
class grid(combinational):
    def __init__(self, gsize=[100, 100], step=10, width = 0.5):
        
        self.gsize = gsize
        self.size = [gsize[0], gsize[1], width]
        self.step = step
        self.width = width
        self.cmd = "grid(size={0}, step={1}, width={2})".format(gsize,step,width)
        
        #-- Call the parent calls constructor first
        super(grid, self).__init__(self.size)
        
    def _geometry(self):
        linex = cube([self.gsize[0], self.width, self.width])
        sx,sy = self.gsize
        lx = [linex.Tras([0,y,0]) for y in range(-sy/2, sy/2+self.step, self.step)]
        lx = union(lx)
        fig = (lx + lx.Rot(90, [0,0,1]))
        return fig.color("Gray")


