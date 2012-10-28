import numpy as np

def unit(v):
    """return the unit vector"""
    
    return v/np.linalg.norm(v)

def Tras(vt):
    """Homogeneous matrix for translation to the point vt"""
    return np.array([
        [1., 0., 0.,  vt[0]],
        [0., 1., 0.,  vt[1]],
        [0., 0., 1.,  vt[2]],
        [0., 0., 0.,  1.]])
    
def Identity():
    """Identity homogeneous transformation"""
    return np.array([
         [ 1.,  0.,  0.,  0.],
         [ 0.,  1.,  0.,  0.],
         [ 0.,  0.,  1.,  0.],
         [ 0.,  0.,  0.,  1.]])
         
def Rot(a, k):
    """Rotation an angle a around the k axis"""
    
    #-- The rotation axis should be defined by a unit vector
    k = unit(k)
    
    #-- Convert the angle to rad
    a = np.radians(a)
    
    C = np.cos(a)
    V = 1. - np.cos(a)
    S = np.sin(a)
    
    #-- Get the axis components
    kx, ky, kz = k
    
    return np.array([
         [ kx * kx * V + C,       kx * ky * V - kz * S,  kx * kz * V + ky * S,  0.],
         [ kx * ky * V + kz * S,  ky * ky * V + C,       ky * kz * V - kx * S,  0.],
         [ kx * kz * V - ky * S,  ky * kz * V + kx * S,  kz * kz * V + C,       0.],
         [ 0.,  0.,  0.,  1.]])
