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

Z = 2


class part(object):
    """Class for defining an object. This class is virtual"""

    def __init__(self, size=[0,0,0]):
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
        print "//-- {}".format(self.cmd)

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
        
        #-- Add the debug mode
        if self.debug:
            cad += '%'
        
        cad += "union() {\n"
        
        #-- Add the object cmd
        cad += cmd + '\n'
        
        #-- Attached parts
        for ap in self.conn_childs:
            cad += ap.scad_gen(indent+2)
        
        cad += "}\n"
        
        #-- Add the Frame of reference
        if self.show_frame:
          cad += frame().scad_gen()
        
        #-- List of connectos
        for conn in self.lconns:
            p,o = conn  #-- Get the position and orientation vectors
            cad += connector(p,o).scad_gen(indent+2)
        
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

    def id(self):
        print "//-- {}".format(self.cmd)

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

    def id(self):
        print "//-- {}".format(self.cmd)

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

    def id(self):
        print "//-- {}".format(self.cmd)
        
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

    def id(self):
        print "//-- {}".format(self.cmd)

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

    def id(self):
        print "//-- {}".format(self.cmd)

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
    def __init__(self, h, r=0, r1=0, r2=0, res=20):
        
        #-- Two kind of cylinder. Depending on the value of r
        if r == 0:
            self.r1 = r1
            self.r2 = r2
            self.r = 0
            self.h = h
            m = max([r1, r2])
            self.size = [m, m, h]
            cmd = "cylinder(r1={0}, r2={1},h={2}, $fn={3}, center=true);"
            self.cmd = cmd.format(r1, r2, h, res)
        else:
            self.r1 = r1
            self.r2 = r2
            self.r = r
            self.h = h
            self.size = [2 * r, 2 * r, h]
            self.cmd = (
            "cylinder(r={0}, h={1}, $fn={2},center=true);".format(r, h, res))
            
        #-- Call the parent calls constructor
        super(cylinder, self).__init__(size=self.size)

    def id(self):
        print "//-- {0}".format(self.cmd)

    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        cad = self.cmd
        return super(cylinder, self).scad_gen(indent, cad)


class cube(part):
    """Primitive part: A cube"""
    def __init__(self, size):

        #-- Call the parent calls constructor first
        super(cube, self).__init__(size)

        self.cmd = "cube({},center=true);".format(self.size)

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        cad = self.cmd
        return super(cube, self).scad_gen(indent, cad)


class sphere(part):
    """A sphere"""
    def __init__(self, r, res=40):

        #-- Call the parent calls constructor first
        super(sphere, self).__init__()

        self.res = res
        self.r = r
        self.size = [2 * r, 2 * r, 2 * r]
        self.cmd = "sphere({0}, $fn={1});".format(self.r, self.res)

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        
        cad = self.cmd
         #-- Call the super-calls scad_gen method
        return super(sphere, self).scad_gen(indent,cad)


class bcube(part):
    """Beveled cube"""

    def __init__(self, size, cr = 2, cres = 5):

        #-- Initialize the object
        self.cr = cr
        self.cres = cres
        self.cmd = "bcube({0},cr={1}, cres={2});".format(size, cr, cres)
        
        #-- Call the parent calls constructor
        super(bcube, self).__init__(size)
        
        self.expr = self._expr()

    def id(self):
        print "//-- {}".format(self.cmd)

    def _expr(self):
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

        #-- Use a cylinder for rounding. Locate it at the first quadrant
        cyl = cylinder(r = self.cr, h = sz / 2.,
                       res = 4 * (self.cres + 1)).translate([sx / 2.,
                                                             sy / 2., 0])

        #-- Return the part created
        obj = minkowski([cyl,
              cube([sx, sy, sz / 2.])]).translate([-sx / 2., -sy / 2., 0])
        return obj

    def scad_gen(self, indent=0):
        """Create the openscad commands for this object"""
        cad = self.expr.scad_gen(indent)
        return super(bcube, self).scad_gen(indent, cad)


class vectorz(part):
    """Vector poiting in the z axis direction"""

    def __init__(self, l = 10, l_arrow = 4, mark = False):
        """
        l : vector length
        l_arrow: Arrow length
        mark: Show a mark in the arrow, for showing the rotaing angle
        """
        #-- Call the parent calls constructor first
        super(vectorz, self).__init__()

        self.l = l
        self.l_arrow = l_arrow
        self.mark = mark
        self.size = [1, 1, l]
        self.cmd = "vectorz(l={0}, l_arrow={1}, mark={2}".format(self.l,
                                                      self.l_arrow,
                                                      self.mark)
        self.expr = self._expr()

    def id(self):
        print "//-- {}".format(self.cmd)

    def _expr(self):
        """Build the object"""

        #-- Draw the vector body
        #-- vector body length (not including the arrow)
        lb = self.l - self.l_arrow

        #-- the vector head
        head = cylinder(r1 = 2 / 2, r2 = 0.2,
                        h = self.l_arrow,
                        res = 20).translate([0, 0, self.l_arrow / 2 + lb / 2.])

        #-- Vector body
        body = cylinder(r= 1 / 2., h = lb, res = 20)

        #-- Vector mark (optional)
        mark = cube([2, 0.3,
                    self.l_arrow * 0.8]).translate([1, 0,
                                                    self.l_arrow *
                                                    0.8 / 2. + lb / 2.])

        #-- Add a sphere in the base (application point)
        base = sphere(r = 1 / 2., res = 20)

        #-- Build the vector
        vec = head + body

        #-- Add the optiona mark
        if self.mark:
            vec += mark

        return vec.translate([0, 0, lb / 2.]) + base

    def scad_gen(self, indent=0):
        
        cad = self.expr.scad_gen(indent)
        
        #-- Call the super-calls scad_gen method
        return super(vectorz, self).scad_gen(indent,cad)


class vector(part):
    """Graphical vector"""

    def __init__(self, v, l_arrow=4, mark=False):
        """
        v : vector
        l_arrow: Arrow lentgt
        mark: Show a mark in the arrow
        """
        #-- Call the parent calls constructor first
        super(vector, self).__init__()

        #-- calculate the vector module
        self.l = np.linalg.norm(v)
        self.v = list(v)
        self.l_arrow = l_arrow
        self.mark = mark
        self.size = [1, 1, self.l]
        self.cmd = "vector(v={0}, l_arrow={1}, mark={2}".format(self.v,
                                                     self.l_arrow,
                                                     self.mark)
        self.expr = self._expr()

    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):
        cad = self.expr.scad_gen(indent)
        #-- Call the super-calls scad_gen method
        return super(vector, self).scad_gen(indent, cad)
        

    def _expr(self):
        """Build the object"""

        return vectorz(l=self.l,
                       l_arrow=self.l_arrow,
                       mark = self.mark).orientate(self.v)


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


class frame(part):
    def __init__(self, l=10, l_arrow=4):
        #-- Call the parent calls constructor first
        super(frame, self).__init__()
        
        self.l = l
        self.l_arrow = l_arrow
        
        self.cmd = "frame(l={0}, l_arrow={1})".format(l, l_arrow)
        self.expr = self._expr()
        
    def id(self):
        print "//-- {}".format(self.cmd)

    def scad_gen(self, indent=0):

        cad = self.expr.scad_gen(indent)
        #-- Call the super-class scad_gen method
        return super(frame, self).scad_gen(indent,cad)
        
    def _expr(self):
        z_axis = vector([0, 0, self.l], l_arrow=self.l_arrow).color("Blue")
        x_axis = vector([self.l, 0, 0], l_arrow=self.l_arrow).color("Red")
        y_axis = vector([0, self.l, 0], l_arrow=self.l_arrow).color("Green")
        fig = x_axis + y_axis + z_axis + sphere(r=1).color("Gray")
        return fig

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

