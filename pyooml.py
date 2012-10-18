#-------------------------------------------------------------
#-- Pyooml: Python Object Oriented Mechanics Library
#-------------------------------------------------------------
#-- (c)  Juan Gonzalez-Gomez  (Obijuan)
#-- (c)  Alberto Valero
#-- October-2012
#-------------------------------------------------------------
#-- GPL licence
#-------------------------------------------------------------


class part():
    """Class for defining an object. This class is virtual"""
    
    def __init__(self):
        self.cmd="(none)"
    
    def id(self):
        print "//-- {}".format(self.cmd)

    def translate(self, pos):
        return translate(self, pos)

    # overload +
    def __add__(self, other):
        return union([self, other])

    #-- This method is used for optimizacion
    def is_union(self):
        return False
        
    def render(self, indent=0):
        print self.scad_gen()
        
    def show(self):
        f = open("test.scad","w")
        
        code = self.scad_gen()
        
        f.write(code) 
        
        f.close()


class translate(part):
    """A translated part"""
    def __init__(self, part, pos):
        self.pos = pos
        self.child = part
        self.cmd = "translate({})".format(self.pos)

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        cad = " " * indent + "{}\n".format(self.cmd) + self.child.scad_gen(indent + 2)
        return cad


class union(part):
    """A group of parts"""
    def __init__(self, list_parts):
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
        cad = " " * indent + "{} {{\n".format(self.cmd)
        childs_cad = [part.scad_gen(indent + 2) for part in self.lparts]
        cad = cad + "".join(childs_cad)
        cad = cad + " " * indent + "}\n"
        return cad

    def is_union(self):
        return True


class minkowski(part):
    """Minkowski operator"""
    def __init__(self, childs):
        self.childs = childs
        self.cmd = "minkowski()"
        
    def id(self):
        print "//-- {}".format(self.cmd)
        
    def scad_gen(self, indent=0):
        cad = " " * indent + self.cmd + "{\n"
        childs_cad = [part.scad_gen(indent + 2) for part in self.childs]
        cad += "".join(childs_cad)
        cad += " " * indent + "}\n"
        return cad


class cylinder(part):
    def __init__(self, r, h, res=20):
        self.r = r
        self.h = h
        self.size = [2*r, 2*r, h]
        self.cmd = "cylinder(r={0},h={1},$fn={2},center=true);".format(r,h,res)
        
    def id(self):
        print "//-- {0}".format(self.cmd)
        
    def scad_gen(self, indent=0):
        cad = " " * indent + self.cmd
        return cad

class cube(part):
    """Primitive part: A cube"""
    def __init__(self, size):
        self.size = size
        self.cmd = "cube({},center=true);".format(self.size)

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        cad = " " * indent + self.cmd + "\n"
        return cad
        
    
        
        
        
        
