class part():
    """Class for defining an object. This class is virtual"""
    def id(self):
        pass

    def translate(self, pos):
        return translate(self,pos)
        
    # overload +
    def __add__(self, other):
        return union([self, other])
    
    #-- This method is used for optimizacion
    def is_union(self):
        return False
            

class translate(part):
    """A translated part"""
    def __init__(self, part, pos):
        self.pos = pos
        self.child = part
        self.cmd = "translate({})".format(self.pos)
        
    def id(self):
        print "//-- {}".format(self.cmd)
        
    def render(self,indent=0):
        print " "*indent + "{} {{".format(self.cmd)
        self.child.render(indent+2)
        print " "*indent + "}"
  
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
        if other.is_union():
            #-- Union + union
            self.lparts.extend(other.lparts)
        else:
            #-- Union + other part (not union)
            self.lparts.extend([other])
        return self    
        
    def render(self, indent=0):
        print " "*indent + "{} {{".format(self.cmd)
        for part in self.lparts:
            part.render(indent+2)
        print " "*indent + "}"
        
    def is_union(self):
        return True
  
class cube(part):
    """Primitive part: A cube"""
    def __init__(self,size):
        self.size = size
        self.cmd = "cube({},center=true);".format(self.size)
        
    def id(self):
        print "//-- {}".format(self.cmd)

    def render(self, indent=0):
        print " "*indent + self.cmd
        


a = cube([10,10,10]).translate([10,0,0])
b = cube([10,10,10])
#t = translate(a, [10,0,0])
#a.id()
u = union([a,b]).translate([20,0,0])
c = (b+b+b+b+b+b+b+b) + (b+b)

c = (cube([50,10,10]) + cube([10,50,10]) + cube([10,10,50])).translate([0,0,10])

c.render()

