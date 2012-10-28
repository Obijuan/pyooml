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

class operator(part):
    def __init__(self, childs, size=[0,0,0]):
        self.childs = childs
        
        #-- Call the parent class constructor
        super(operator, self).__init__(size)
        
    def scad_gen(self, indent=0):
        
        cad = self.cmd + "{\n"
        childs_cad = [part.scad_gen(indent + 2) for part in self.childs]
        cad += "".join(childs_cad)
        cad += " " * indent + "}\n"
        
        #-- Call the super-calls scad_gen method
        return super(operator, self).scad_gen(indent, cad)


class difference(operator):
    """Difference operator"""
    def __init__(self, childs):
        
        self.cmd = "difference()"

        #-- Call the parent calls constructor first
        super(difference, self).__init__(childs)


class minkowski(operator):
    """Minkowski operator"""
    def __init__(self, childs):

        self.cmd = "minkowski()"

        #-- Call the parent calls constructor first
        super(minkowski, self).__init__(childs)

class union(operator):
    """A group of parts"""
    def __init__(self, childs):
        
        self.cmd = "union()"
        
        #-- Call the parent calls constructor first
        super(union, self).__init__(childs)

    #--- this is for optimization... Not useful at the moment
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

    #def is_union(self):
    #    return True
    
