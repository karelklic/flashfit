# -*- coding: utf-8 -*- (Python reads this)
import data_fit
import data_fit_parameter
import numpy
import math
import nonneglstsq

class ModelAtoBtoC:
    NAME = u"A→B→C"

    def initialParameters(self, time):
        return [10 / (time[len(time) / 2] - time[0]),
                3 / (time[len(time) / 2] - time[0])]

    def rcalc(self, k, a_0, t, y):
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
        c0 = a_0 * numpy.matlib.exp(-k[0,0] * t)
        # Second column of C contains concetrations of B
        c1 = a_0 * (k[0,0] / (k[1,0] - k[0,0])) * (numpy.matlib.exp(-k[0,0] * t) - numpy.matlib.exp(-k[1,0] * t))
        # Third column of C contains concentrations of C
        c2 = a_0 - c0 - c1
        # Fourth column for the linear part
        c3 = numpy.empty(t.shape)
        c3.fill(1)
        c = numpy.matlib.hstack((c0, c1, c2, c3))

        # elimination of linear parameters
        # [0] because we just need the result, not the residuals etc.
        # allows negative results
        #a = numpy.linalg.lstsq(c, y)[0]
        a = numpy.matrix(nonneglstsq.nonneglstsq(c.getA(), y.getA1())[0]).T

        # calculate residuals
        # ca = c * a (matrix multiplication)
        r = y - numpy.matlib.dot(c, a)
        return (r, c, a)

class ModelAtoB:
    NAME = u"A→B"

    def initialParameters(self, time):
        return [10 / (time[len(time) / 2] - time[0])]

    def rcalc(self, k, a_0, t, y):
        """
        Function used by ngml, but not by ngml2.
        Parameter k (=parameter) is a column vector.
        Parameter a_0 is a number.
        Parameter t is a list of time values.
        Parameter y is a column vector of measured values.
        Returns tuple of three values:
        - first value is a list of residuals 'r'
        - second value is a matrix of concentrations 'c'
        - third value is a absorbance matrix 'a'
        """
        # First column of C contains concentrations of A
        c0 = a_0 * numpy.matlib.exp(-k[0,0] * t)
        # Second column for the linear part.
        c1 = numpy.empty(t.shape)
        c1.fill(1)
        c = numpy.matlib.hstack((c0, c1))

        # elimination of linear parameters
        # [0] because we just need the result, not the residuals etc.
        a = numpy.matrix(nonneglstsq.nonneglstsq(c.getA(), y.getA1())[0]).T

        # calculate residuals
        r = y - numpy.matlib.dot(c, a)
        return (r, c, a)

class ModelAtoBCtoD:
    NAME = u"A→B, C→D"

    def initialParameters(self, time):
        return [10 / (time[len(time) / 2] - time[0]), 3 / (time[len(time) / 2] - time[0])]

    def rcalc(self, k, a_0, t, y):
        """
        Function used by ngml, but not by ngml2.
        Parameter k (=parameter) is a column vector.
        Parameter a_0 is a number.
        Parameter t is a list of time values.
        Parameter y is a column vector of measured values.
        Returns tuple of three values:
        - first value is a list of residuals 'r'
        - second value is a matrix of concentrations 'c'
        - third value is a matrix 'a'
        """
        c0 = a_0 * numpy.matlib.exp(-k[0,0] * t)
        c1 = a_0 * numpy.matlib.exp(-k[1,0] * t)
        # Linear part
        c2 = numpy.empty(t.shape)
        c2.fill(1) # or a_0?
        c = numpy.matlib.hstack((c0, c1, c2))

        # elimination of linear parameters
        # [0] because we just need the result, not the residuals etc.
        a = numpy.matrix(nonneglstsq.nonneglstsq(c.getA(), y.getA1())[0]).T

        # calculate residuals
        r = y - numpy.matlib.dot(c, a)
        return (r, c, a)

def ngml(time, absorbance, model, logger):
    """
    Calculates the fit, residuals, and reaction rate coefficients from
    absorbance values using Newton-Gauss-Levenberg/Marquardt algorithm.
    
    Parameter p is a list of initial parameters.
    a_0 is a number (usually 1e-3)
    Parameter t contains a list of time values.
    Parameter y is a list of measured values.
    
    Returns
    -------
    A tuple containing the following items:
    p : array of reaction rate coefficients
    sigma_p : array of p coefficient precisions
    The array has the same size as array `p`.
    absorbance_fit : array of *fitted* absorbance values
    The array has the same size as the input array `time`
    and `absorbance`
    residuals : array of differences between measured and fitted absorbances
    The array has the same size as the `absorbance_fit` array.
    
    Notes
    -----
    Also check leastsq in SciPy, as it might be useful:
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.leastsq.html
    Wikipedia:
    http://en.wikipedia.org/wiki/Levenberg%E2%80%93Marquardt_algorithm
    http://en.wikipedia.org/wiki/Non-linear_least_squares
    """
    a_0 = 1e-3
    parameters = model.initialParameters(time)

    # make column vector from y
    y = numpy.matrix(absorbance).transpose()
    # make column vector from p
    p = numpy.matrix(parameters).transpose()
    # make column vector from t
    t = numpy.matrix(time).transpose()

    ssq_old = 1e100
    # Marquardt parameter
    mp = 0
    # convergence limit
    mu = 1e-4
    # step size for numerical diff
    delta = 1e-6

    it = 0 # iteration
    j = numpy.matlib.empty([len(t), len(p)]) # Jacobian
    while it < 50:
        # call calc of residuals
        (r0, c, a) = model.rcalc(p, a_0, t, y)
        ssq = numpy.matlib.sum(numpy.matlib.multiply(r0, r0))
        conv_crit = (ssq_old - ssq) / ssq_old
        logger("Fitting absorbance: it=%i, ssq=%g, mp=%g, conv_crit=%g" % (it, ssq, mp, conv_crit))
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
                r = model.rcalc(p, a_0, t, y)[0]
                j[:,i] = ((r - r0) / (delta * p[i]))[:,0]
                p[i] = p[i] / (1 + delta)
        elif conv_crit < -mu: # divergence !
            if mp == 0:
                mp = 1 # use Marquardt parameter
            else:
                mp *= 5
            p = p - delta_p # and take shifts back

        # augment Jacobian matrix
        j_mp = numpy.matlib.vstack((j, mp * numpy.matlib.eye(len(p))))
        # augment residual vector
        r0_mp = numpy.matlib.vstack((r0_old, numpy.matlib.zeros(p.shape)))
        # calculate parameter shifts
        delta_p = numpy.linalg.lstsq(-j_mp, r0_mp)[0]
        # add parameter shifts
        p = p + delta_p
        it += 1

    # Curvature matrix
    curv = numpy.matlib.dot(j.H, j)

    # Set parameters (speed constants?) and sigma for parameters
    logger("Fitting absorbance: final calculations")
    sigma_y = math.sqrt(ssq / (numpy.matlib.size(y) - numpy.matlib.size(p) - numpy.matlib.size(a)))
    p = p.transpose().tolist()[0]
    sigma_p = sigma_y * numpy.sqrt(numpy.matlib.diag(numpy.linalg.inv(curv)))
    sigma_p = sigma_p.tolist()

    parameters = []
    for i in range(0, len(p)):
        param = data_fit_parameter.Parameter()
        param.value = p[i]
        param.sigma = sigma_p[i]
        param.a0minusAinf = 12345
        parameters.append(param)
    
    # Set absorbance fit curve
    a_tot = numpy.matlib.dot(c, a)
    absorbanceFit = a_tot[:,0].transpose().tolist()[0]

    # Set residuals
    # Should 'r' be used, or maybe 'r0' should be?
    residuals = data_fit.Residuals(r0.transpose().tolist()[0])
    return (parameters, absorbanceFit, residuals)
