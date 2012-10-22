import pyooml as oom
import numpy as np

#-- for accesing the X,Y and Z components of a vector
X = 0
Y = 1
Z = 2


class Servo(oom.part):
    """Class for using servos"""

    #-- Default parameters
    #-- Servo color
    col = np.array([1, 1, 1]) * 0.4
    alpha = 1.0

    def __init__(self):
        """NO arguments. Servo Initialization"""

        #-- Call the parent calls constructor
        super(Servo, self).__init__()

        #------------- Data calculated from the user parameters ----------

        #---------Create the drill table
        #-- Distance from the center to the drills
        self.dx = self.drills_x_dist / 2.
        self.dy = self.drills_y_dist / 2.

        #-- Typical servos have 4 drills

        #-- list of (x,y,z) coordinates for the drills
        self.drills_pos = [
            [self.dx,  self.dy, 0.],
            [-self.dx, self.dy, 0.],
            [-self.dx, -self.dy, 0.],
            [self.dx, -self.dy, 0.]
        ]

        #--- position
        #-- Calculate the shaft botom point
        self.shaft_base_pos = np.array([self.body_size[X] / 2. -
                                        self.shaft_d -
                                        self.shaft_diam / 2.,
                                        0,
                                        self.body_size[Z] / 2.])
        #-- For building the servo what is really used is the
        #-- distance from the servo center
        self.ear_hi_center = self.ear_hi - self.body_size[Z] / 2.

        #-- Build the geometry
        self.expr = self._expr()

    def id(self):
        print "//-- {}".format(self.cmd)

    def _expr(self):
        #-- Draw the servo

        bsx, bsy, bsz = self.body_size
        esx, esy, esz = self.ear_size

        body = oom.bcube(self.body_size,
                         cr = self.body_cr,
                         cres = self.body_cres)
        ears = oom.bcube([2 * esx + bsx, esy, esz],
                         cr = self.body_cr,
                         cres = self.body_cres)

        #-- Translate the ears to their position
        ears = ears.translate([0, 0, self.ear_hi_center] - ears.bottom)

        base_shaft = oom.cylinder(r=self.shaft_base_diam / 2.,
                                  h=self.shaft_base_hi,
                                  res=50)
        base_shaft = base_shaft.translate(self.shaft_base_pos - base_shaft.bottom)

        shaft = oom.cylinder(r = self.shaft_diam/2., h = self.shaft_hi, res = 50)
        shaft = shaft.translate(self.shaft_base_pos + [0, 0, self.shaft_base_hi] -
                                shaft.bottom)

        drills = self.drills(dh=self.ear_size[Z]+1).translate([0,0,self.ear_hi_center+self.ear_size[Z]/2.])

        servo = shaft + body + (ears - drills) + base_shaft 

        return servo.color(self.col, self.alpha)

    def drills(self, dh):
        """Create the cylinder for making the servo drills
        dh = drill height
        """

        l = [oom.cylinder(r = self.drills_diam / 2., h = dh).translate(p)
             for p in self.drills_pos]

        obj = oom.union(l)

        return obj

    def scad_gen(self, indent=0):

        cad = self.expr.scad_gen(indent)
        #-- Call the super-calls scad_gen method
        return super(Servo, self).scad_gen(indent, cad)


class Futaba3003(Servo):

    #-- Servo identification
    cmd = "Futaba3003()"  

    #------------------------ Given by the user -----------
    #-- Servo body size
    body_size = np.array([40.8, 20., 36.2])
    body_cr = 1        #-- Corner radius
    body_cres = 5      #-- Corner resolution

    #-- Servo ears
    ear_size = [7.8, 18., 2.5]

    #-- Servo drills
    drills_x_dist = 48.5  #-- x-distance between left and right drills
    drills_y_dist = 9.6   #-- y distance between the front and rear drills

    drills_diam = 3

    #-- Distance from the servo bottom to the
    #-- bottom of the ears (it can be measured with a caliper)
    ear_hi = 27.

    #-- Shaft base (height and diameter)
    shaft_base_diam = 14.5
    shaft_base_hi = 2.

    #-- Shaft
    shaft_diam = 6
    shaft_hi = 3.8

    #-- Distance from the right side servo body to the rigth side of shaft
    #-- It can be meassured with a caliper
    shaft_d = 7.3


class TowerProSG90(Servo):

    #-- Object identification
    cmd = "TowerProSG90()"

    #------------------------ Given by the user -----------
    #-- Servo color
    col = np.array([0, 0, 1])*1.0
    alpha = 0.9

    #-- Servo body size
    body_size = np.array([23.2, 12.4, 22.9])
    body_cr = 1        #-- Corner radius
    body_cres = 5      #-- Corner resolution

    #-- Servo ears
    ear_size = [4.8, 11.9, 2.4]

    #-- Servo drills
    drills_x_dist = 28.1  #-- x-distance between left and right drills
    drills_y_dist = 0    #-- y distance between the front and rear drills

    drills_diam = 2.5

    #-- Distance from the servo bottom to the
    #-- bottom of the ears (it can be measured with a caliper)
    ear_hi = 15.5

    #-- Shaft base (height and diameter)
    shaft_base_diam = 11.3
    shaft_base_hi = 4.

    #-- Shaft
    shaft_diam = 4.6
    shaft_hi = 2.8

    #-- Distance from the right side servo body to the rigth side of shaft
    #-- It can be meassured with a caliper
    shaft_d = 3.4

    def __init__(self):

        #-- Call the parent calls constructor
        super(TowerProSG90, self).__init__()

        #-- These servos only have 2 drills

        #-- list of (x,y,z) coordinates for the drills
        self.drills_pos = [
            [self.dx,  0., 0.],
            [-self.dx, 0., 0.],
        ]
    
    
    
