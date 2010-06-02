import data_fit
import data_fit_parameter
import numpy
import math
import copy

class Parameter(data_fit_parameter.Parameter):
    def __init__(self):
        data_fit_parameter.Parameter.__init__(self)
        self.firstOrder = True

    def __str__(self):
        result = data_fit_parameter.Parameter.__str__(self)
        result += " firstOrder:" +  str(self.firstOrder)
        return result

def ngml(time, absorbance, parameters, logger):
    """
    Calculates the fit, residuals, and reaction rate coefficients from
    absorbance values.

    Returns
    -------
    A tuple containing the following items:
    p : array of reaction rate coefficients
    absorbance_fit : array of *fitted* absorbance values
    The array has the same size as the input array `time`
    and `absorbance`
    residuals : array of differences between measured and fitted absorbances
    The array has the same size as the `absorbance_fit` array.
    """
    # make column vector from y
    y = numpy.matrix(absorbance).T

    val = 10 / (time[len(time) / 2] - time[0])
    for parameter in parameters:
        if parameter.fixed:
            continue
        if parameter.value > 0:
            continue
        parameter.value = val
        val /= 2

    # Add another parameter containing linear part.
    linearParam = Parameter()
    linearParam.value = 0
    linearParam.firstOrder = False
    linearParam.fixed = True
    parameters.append(linearParam)

    ssq_old = 1e100
    # Marquardt parameter
    mp = 0
    # convergence limit
    mu = 1e-6

    def calcHessianJtrA(dc, c, y):
        """
        Hessian matrix = square matrix of secnd order partial derivatives
        c = matrix of concentrations of various components (depends on parameter count)
        """
        ct = c.T
        ctc = numpy.matlib.dot(ct, c)
        ctcinv = ctc.I
        aux = numpy.matlib.dot(ctcinv, ct)
        a = numpy.matlib.dot(aux, y)
        aux = numpy.matlib.dot(c, a)
        r = aux - y
        ssq = 0
        for i in range(0, r.shape[0]):
            for j in range(0, r.shape[1]):
                ssq += r[i,j] * r[i,j]
        j = numpy.matlib.zeros([dc[0].shape[0], len(dc)]) # 1 = y dimension
        dq = []
        for p in range(0, len(dc)):
            dctc = numpy.matlib.dot(dc[p].T, c)
            dq.append(dctc + dctc.T)

        hessian = numpy.matlib.zeros([j.shape[1], j.shape[1]])
        jtr = numpy.matlib.zeros([j.shape[1], 1])
        for p in range(0, len(dc)):
            dqa = numpy.matlib.dot(dq[p], a)
            dct = dc[p].T
            dcty = numpy.matlib.dot(dct, y)
            dca = numpy.matlib.dot(dc[p], a)
            dctyminusdqa = dcty - dqa
            aux = numpy.matlib.dot(ctcinv, dctyminusdqa)
            aux1 = numpy.matlib.dot(c, aux)
            jvec = dca - aux1
            j[:,p] = jvec
        hessian += numpy.matlib.dot(j.T, j)
        jtr += numpy.matlib.dot(j.T, r)
        return (hessian, jtr, a, ssq)

    it = 0 # iteration
    end = False
    while it < 200 and not end:
        # Calculate C and dC for some parameters p
        c = numpy.matlib.zeros([len(time), len(parameters)])
        dc = []
        for i in range(0, len(parameters)):
            dci = numpy.matlib.zeros([len(time), len(parameters)])
            for j in range(0, len(time)):
                kt = parameters[i].value * time[j]
                if parameters[i].firstOrder:
                    if abs(kt) >= 5E3:
                        raise "Numeric error"

                    c[j,i] = math.exp(-kt)
                    if parameters[i].fixed:
                        dci[j,i] = 1
                    else:
                        dci[j,i] = -c[j,i] * time[j]
                else:
                    if abs(kt) <= -1:
                        raise "Numeric error"

                    c[j,i] = 1 / (kt + 1)
                    if parameters[i].fixed:
                        dci[j,i] = 1
                    else:
                        dci[j,i] = -time[j] / ((kt + 1) * (kt + 1))
            dc.append(dci)

        (hessian, jtr, a, ssq) = calcHessianJtrA(dc, c, y)
        conv_crit = (ssq_old - ssq) / ssq_old
        logger("Fitting absorbance: it=%i, ssq=%g, mp=%g, conv_crit=%g" % (it, ssq, mp, conv_crit))
        if abs(conv_crit) < mu:
            if mp == 0:
                end = True # if Marquardt par zero, stop
            else:
                mp = 0 # set to 0 , another iteration
        elif conv_crit > 0:
            mp = mp / 3
            ssq_old = ssq
            p_old = copy.deepcopy(parameters)
            jtr_old = jtr
            hessian_old = hessian
        else:
            if mp == 0:
                mp = hessian[0,0]
            mp *= 5
            parameters, jtr, hessian = p_old, jtr_old, hessian_old

        for i in range(0, hessian.shape[0]):
            hessian[i,i] += mp

        hessianInv = hessian.I
        shifts = numpy.matlib.dot(hessianInv, jtr)
        for i in range(0, len(parameters)):
            if not parameters[i].fixed:
                parameters[i].value -= shifts[i]
        it += 1

    sigma = math.sqrt(ssq / (numpy.matlib.size(y) - 1))
    for i in range(0, len(parameters)):
        if parameters[i].fixed:
            parameters[i].sigma = 0
        else:
            parameters[i].sigma = sigma * math.sqrt(hessianInv[i,i])

    for i in range(0, len(parameters)):
        parameters[i].a0minusAinf = c[0, i] * a[i,0]
    ainf = parameters[len(parameters) - 1].a0minusAinf

    a_tot = numpy.matlib.dot(c, a)
    absorbanceFit = a_tot[:,0].transpose().tolist()[0]
    r = y - a_tot
    residuals = data_fit.Residuals(r.transpose().tolist()[0])

    # Remove the last p we added in this function.
    parameters = parameters[0:-1]
    return (parameters, absorbanceFit, residuals, ainf)
