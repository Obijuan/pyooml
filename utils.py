import numpy as np

def anglev(u,v):
    """Calculate the angle between 2 vectors (in degrees)"""
    angle =  np.arccos( np.dot(u,v) /  (np.linalg.norm(u)*np.linalg.norm(v)))
    
    return np.degrees(angle)


