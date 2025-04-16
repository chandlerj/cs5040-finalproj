

# SciUt comments denotes snippet from paper : https://www.sci.utah.edu/~beiwang/publications/MFA_BeiWang_2024.pdf
from paraview.simple import *
import numpy as np
from scipy.interpolate import BSpline, make_lsq_spline
from scipy.linalg import lstsq

def rescale(vector):
    # SciUt "(rescale) input data points to the interval [0, 1]
    # Library dependencies: np.min, np.max
    return (vector - np.min(vector)) / (np.max(vector) - np.min(vector))

def knot_vector(degree, num_ctrl_pts):
    # SciUt: a degree-p spline with n control point must have n + p + 1 knots 
    return np.linspace(0, 1, num_ctrl_pts + degree + 1)
   
def basis_vector(x, knot_vector, deg):
    # SciUt: Mathematically, B-splines may be described as linear combinations of B-spline basis functions, where
        # the coefficient on each basis function is a control point
    num_bas_functions = len(knot_vector)
    basis = []
    for i in range(num_bas_functions):
        bSpline = BSpline.basis_element(knot_vector[i:i + deg + 2])
        basis.append(bSpline(x))
    
    return basis

def tensor_product(b_u, b_v, b_w):
    return np.einsum('iu, iv, iw -> iuv', b_u, b_v, b_w)


def b_spline(u, v, w, func, degree, num_ctrl_pts):
    # SciUt: initializing a knot distribution with a small number of control points."
    u, v, w = rescale(u), rescale(v), rescale(w)
    knot_u, knot_v, knot_w = knot_vector(degree, num_ctrl_pts), knot_vector(degree, num_ctrl_pts), knot_vector(degree, num_ctrl_pts)      
    b_u, b_v, b_w = basis_vector(u, knot_u), basis_vector(v, knot_v), basis_vector(w, knot_w)
    # B = np.einsum(b_u, b_v, b_w)

def gradient(knot_vector):
    dev_0 = knot_vector
    dev_1 = knot_vector.derivative(1)
    dev_2 = knot_vector.derivative(2)

    return dev_0, dev_1, dev_2
    



def log_dataset_info(filePath):
    data = XMLUnstructuredGridReader(FileName=[filePath])
    print('Vector names:')
    print(data.PointData.keys())
    print('FieldData names')
    print(data.FieldData.keys())


def extract_points(filePath):
    data = XMLUnstructuredGridReader(FileName=[filePath])

log_dataset_info("C:/Users/emily/Downloads/CS5040/5040_Final_Project/Interface/run01/run01/timestep_059.vtu")
extract_points("C:/Users/emily/Downloads/CS5040/5040_Final_Project/Interface/run01/run01/timestep_059.vtu")
