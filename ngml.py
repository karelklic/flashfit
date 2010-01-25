import numpy
from numpy import matrix, matlib, linalg
import math

def rcalcABC(k, a_0, t, y):
    """
    Parameter k (=parameter) is a column vector.
    Parameter a_0 is a number.
    Parameter t is a list of time values.
    Parameter y is a column vector of measured values.
    Returns tuple of three values:
       - first value is a list of residuals 'r'
       - second value is a matrix of concentrations 'c'
       - third value is a matrix 'a'
    """
    # First column of C contains concentrations of A
    c0 = []
    for tloop in t:
        c0.append(a_0 * math.exp(-k[0,0] * tloop))

    # Second column of C contains concetrations of B
    c1 = []
    for tloop in t:
        c1.append(a_0 * k[0,0] / (k[1,0] - k[0,0]) * (math.exp(-k[0,0] * tloop) - math.exp(-k[1,0] * tloop)))

    # Third column of C contains concentrations of C
    c2 = []
    for i in range(0, len(c0)):
        c2.append(a_0 - c0[i] - c1[i])

    c = matlib.mat([c0, c1, c2])
    c = c.transpose()
    
    # elimination of linear parameters
    # [0] because we just need the result, not the residuals etc.
    a = linalg.lstsq(c, y)[0]

    # calculate residuals
    # ca = c * a (matrix multiplication)
    ca = matlib.dot(c, a)
    r = y - ca
    
    return (r, c, a)

def rcalcFirst(k, a_0, t, y):
    # First column of C contains concentrations of A
    c0 = []
    for tloop in t:
        c0.append(a_0 * math.exp(-k[0,0] * tloop))
   
    c = matlib.mat([c0])
    c = c.transpose()
    
    # elimination of linear parameters
    # [0] because we just need the result, not the residuals etc.
    a = linalg.lstsq(c, y)[0]

    # calculate residuals
    # ca = c * a (matrix multiplication)
    ca = matlib.dot(c, a)
    r = y - ca
    
    return (r, c, a)

def rcalcFirst2(k, a_0, t, y):
    c0 = []
    for tloop in t:
        c0.append(a_0 * math.exp(-k[0,0] * tloop))
   
    c1 = []
    for tloop in t:
        c1.append(a_0 * math.exp(-k[1,0] * tloop))

    c = matlib.mat([c0, c1])
    c = c.transpose()
    
    # elimination of linear parameters
    # [0] because we just need the result, not the residuals etc.
    a = linalg.lstsq(c, y)[0]

    # calculate residuals
    # ca = c * a (matrix multiplication)
    ca = matlib.dot(c, a)
    r = y - ca
    
    return (r, c, a)

def ngml(function, p, a_0, t, y):
    """
    Newton-Gauss-Levenberg/Marquardt algorithm
    Parameter p is a list of initial parameters.
    a_0 is a number (usually 1e-3)
    Parameter t contains a list of time values.
    Parameter y is a list of measured values.
    """

    # make column vector from y
    y = matrix(y).transpose()
    # make column vector from p
    p = matrix(p).transpose()

    ssq_old = 1e50
    # Marquardt parameter
    mp = 0
    # convergence limit
    mu = 1e-4
    # step size for numerical diff
    delta = 1e-6

    it = 0 # iteration
    j = matlib.empty([len(t), len(p)]) # Jacobian
    while it < 50:
        # call calc of residuals
        (r0, c, a) = function(p, a_0, t, y)
        ssq = matlib.sum(matlib.multiply(r0, r0))
        conv_crit = (ssq_old - ssq) / ssq_old
        print "it=%i, ssq=%g, mp=%g, conv_crit=%g" % (it, ssq, mp, conv_crit)
        if abs(conv_crit) <= mu: # ssq_old=ssq, minimum reached !
            if mp == 0:
                break # if Marquardt par zero, stop
            else:
                mp = 0 # set to 0 , another iteration
                r0_old = r0
        elif conv_crit > mu: # convergence !
            mp = mp / 3
            ssq_old = ssq  
            r0_old = r0
            for i in range(0, len(p)):					
                p[i] = (1 + delta) * p[i]						
                r = function(p, a_0, t, y)[0];
                ji = (r - r0) / (delta * p[i])
                for loop in range(0, matlib.size(r)):
                    j[loop, i] = ji[loop, 0]
                p[i] = p[i] / (1 + delta);						
        elif conv_crit < -mu: # divergence !
            if mp == 0:											
                mp = 1 # use Marquardt parameter
            else:
                mp = mp * 5										 
            p = p - delta_p # and take shifts back

        # augment Jacobian matrix
        j_mp = matlib.vstack((j, mp * matlib.eye(len(p))))
        # augment residual vector
        r0_mp = matlib.concatenate((r0_old, matlib.zeros(p.shape)))
        # calculate parameter shifts
        delta_p = linalg.lstsq(-j_mp, r0_mp)[0]
        # add parameter shifts
        p = p + delta_p 
        it += 1
       
    # Curvature matrix
    curv = j.H * j

    # Should 'r' be returned, or maybe 'r0' should be? 
    return (p, ssq, c, a, curv, r0)

