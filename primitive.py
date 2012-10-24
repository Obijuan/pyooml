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
import copy
import transformations as trans


class cube(part):
    """Primitive part: A cube"""
    
    def __init__(self, size):
        
        #-- Openscad command
        self.cmd = "cube({},center=true);".format(size)
        
        #-- Call the parent calls constructor first
        super(cube, self).__init__(size)
    
    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        
        return super(cube, self).scad_gen(indent, self.cmd)
        