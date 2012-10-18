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


class part(object):
    """Class for defining an object. This class is virtual"""
    
    def __init__(self):
        self.cmd="(none)"
        self.debug = False
    
    def id(self):
        print "//-- {}".format(self.cmd)

    def translate(self, pos):
        return translate(self, pos)

    def rotate(self, rot):
        return rotate(self, rot)
        
    # overload +
    def __add__(self, other):
        return union([self, other])

    def _modified_scad(self, indent=0):
        if self.debug:
            cad = "%" + self.scad_gen(indent)
        else:
            cad = self.scad_gen(indent)
        return cad
        
    def scad_gen(self, indent=0):
        if self.debug:
            cad = "%"
        else:
            cad = ""
        cad += " " * indent
        return cad
        
    #-- This method is used for optimizacion
    def is_union(self):
        return False
        
    def render(self, indent=0):
        print self.scad_gen(indent)
        
    def show(self):
        f = open("test.scad","w")
        
        code = self.scad_gen()
        
        f.write(code) 
        
        f.close()


class translate(part):
    """A translated part"""
    def __init__(self, part, pos):
        #-- Call the parent calls constructor first
        super(translate,self).__init__()
        
        self.pos = pos
        self.child = part
        self.cmd = "translate({})".format(self.pos)

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        #-- Call the super-calls scad_gen method
        cad = super(translate, self).scad_gen(indent)
        
        cad += "{}\n".format(self.cmd) + self.child.scad_gen(indent + 2)
        return cad

class rotate(part):
    """A rotated part"""
    def __init__(self, part, rot):
        #-- Call the parent calls constructor first
        super(rotate,self).__init__()
        
        self.rot = rot
        self.child = part
        self.cmd = "rotate({})".format(self.rot)

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        #-- Call the super-calls scad_gen method
        cad = super(rotate, self).scad_gen(indent)
        
        cad +=  format(self.cmd)+ '\n' + self.child.scad_gen(indent + 2)
        return cad
        

class union(part):
    """A group of parts"""
    def __init__(self, list_parts):
        #-- Call the parent calls constructor first
        super(union,self).__init__()
        
        self.lparts = list_parts
        self.cmd = "union()"

    def id(self):
        print "//-- {}".format(self.cmd)

    
    def __add__(self, other):
        #-- Optimizacion: if the second argument is an
        #-- Union too.. incorporate their childs into the
        #-- union list
        
        #-- Create list of child objects of the new union
        #-- (A copy of the current union)
        lparts = [p for p in self.lparts]
        
        #-- If the new object is a union, just added their childs
        #-- (not the union itself)
        if other.is_union():
            #-- Union + union
            lparts.extend(other.lparts)
        else:
            #-- Union + other part (not union)
            lparts.extend([other])
        
        return union(lparts)

    def scad_gen(self, indent=0):
        #-- Call the super-calls scad_gen method
        cad = super(union, self).scad_gen(indent)
        
        cad += "{0} {{\n".format(self.cmd)
        childs_cad = [part.scad_gen(indent + 2) for part in self.lparts]
        cad = cad + "".join(childs_cad)
        cad = cad + " " * indent + "}\n"
        return cad

    def is_union(self):
        return True


class minkowski(part):
    """Minkowski operator"""
    def __init__(self, childs):
        #-- Call the parent calls constructor first
        super(minkowski,self).__init__()
        
        self.childs = childs
        self.cmd = "minkowski()"
        
    def id(self):
        print "//-- {}".format(self.cmd)
        
    def scad_gen(self, indent=0):
        #-- Call the super-calls scad_gen method
        cad = super(minkowski, self).scad_gen(indent)
        
        cad += self.cmd + "{\n"
        childs_cad = [part.scad_gen(indent + 2) for part in self.childs]
        cad += "".join(childs_cad)
        cad += " " * indent + "}\n"
        return cad


class cylinder(part):
    def __init__(self, r, h, res=20):
        #-- Call the parent calls constructor first
        super(cylinder,self).__init__()
        
        self.r = r
        self.h = h
        self.size = [2*r, 2*r, h]
        self.cmd = "cylinder(r={0},h={1},$fn={2},center=true);".format(r,h,res)
        
    def id(self):
        print "//-- {0}".format(self.cmd)
        
    def scad_gen(self, indent=0):
        #-- Call the super-calls scad_gen method
        cad = super(cylinder, self).scad_gen(indent)
        
        cad += self.cmd + "\n"
        return cad

class cube(part):
    """Primitive part: A cube"""
    def __init__(self, size):
        
        #-- Call the parent calls constructor first
        super(cube,self).__init__()
        
        self.size = size
        self.cmd = "cube({},center=true);".format(self.size)

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        
        #-- Call the super-calls scad_gen method
        cad = super(cube, self).scad_gen(indent)
        
        cad += self.cmd + "\n"
        return cad
        
    
        
class bcube(part):
    """Beveled cube"""
    def __init__(self, size, cr = 2, cres=5):
        
        #-- Call the parent calls constructor first
        super(bcube,self).__init__()
        
        #-- Initialize the object
        self.size = size
        self.cr = cr
        self.cres = cres
        self.cmd = "bcube({0},cr={1}, cres={2});".format(self.size, self.cr, self.cres)
        self.expr = self._expr()
        
    def id(self):
        print "//-- {}".format(self.cmd)
        
    def _expr(self):    
        """Expresion for building the object"""  
        
        #-- if cr is 0, means a standar cube
        if (self.cr == 0):
            return cube(self.size)
        
        #-- Make sure the corner radius is not too big
        if self.cr> min([self.size[0], self.size[1]])/2:
            self.cr = min([self.size[0], self.size[1]])/2
            print "Saturation!"
            
        #-- Get the internal cube size
        sx,sy,sz = bsize = list(np.array(self.size) - 2*np.array([self.cr, self.cr, 0]));
        
        #-- The cube cannot have lengths equal to 0
        if sx==0:
            sx = 0.001
        
        if sy==0:
            sy = 0.001
            
        #-- Use a cylinder for rounding. Locate it at the first quadrant
        cyl = cylinder(r=self.cr, h = sz/2, res = 4*(self.cres + 1)).translate([sx/2, sy/2, 0]);
        
        #-- Return the part created
        return minkowski([cyl, cube([sx,sy,sz/2])]).translate([-sx/2, -sy/2, 0])
        

    def scad_gen(self, indent=0):
        #-- Call the super-calls scad_gen method
        cad = super(bcube, self).scad_gen(indent)
        
        #-- do the particular stuff for this class
        cad += self.expr.scad_gen(indent)
        return cad

