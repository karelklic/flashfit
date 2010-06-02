import data_fit_parameter

class Parameter(data_fit_parameter.Parameter):
    def __init__(self):
        data_fit.Parameter.__init__(self)
        self.firstOrder = True

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
    y = matrix(absorbance).T

    # Add another parameter containing linear part.
    linearParam = Parameter()
    linearParam.value = 0
    linearParam.firstOrder = True
    linearParam.fixed = True
    parameters.append(linearParam)

    # make column vector from p
    p = matrix(parameters).T

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
        ctc = matlib.dot(ct, c)
        ctcinv = ctc.I
        aux = matlib.dot(ctcinv, ct)
        a = matlib.dot(aux, y)
        aux = matlib.dot(c, a)
        r = aux - y
        ssq = 0
        for i in range(0, r.shape[0]):
            for j in range(0, r.shape[1]):
                ssq += r[i,j] * r[i,j]
        j = matlib.zeros([dc[0].shape[0], len(dc)]) # 1 = y dimension
        dq = []
        for p in range(0, len(dc)):
            dctc = matlib.dot(dc[p].T, c)
            dq.append(dctc + dctc.T)

        hessian = matlib.zeros([j.shape[1], j.shape[1]])
        jtr = matlib.zeros([j.shape[1], 1])
        for p in range(0, len(dc)):
            dqa = matlib.dot(dq[p], a)
            dct = dc[p].T
            dcty = matlib.dot(dct, y)
            dca = matlib.dot(dc[p], a)
            dctyminusdqa = dcty - dqa
            aux = matlib.dot(ctcinv, dctyminusdqa)
            aux1 = matlib.dot(c, aux)
            jvec = dca - aux1
            j[:,p] = jvec
        hessian += matlib.dot(j.T, j)
        jtr += matlib.dot(j.T, r)
        return (hessian, jtr, a, ssq)

    it = 0 # iteration
    end = False
    while it < 50 and not end:
        # Calculate C and dC for some parameters p
        c = matlib.zeros([len(time), matlib.size(p)])
        dc = []
        for i in range(0, matlib.size(p)):
            dci = matlib.zeros([len(time), matlib.size(p)])
            for j in range(0, len(time)):
                kt = p[i].value * time[j]
                if p[i].firstOrder:
                    if abs(kt) >= 5E3:
                        raise "Numeric error"

                    c[j,i] = math.exp(-kt)
                    if p[i].fixed:
                        dci[j,i] = 1
                    else:
                        dci[j,i] = -c[j,i] * time[j]
                else:
                    if abs(kt) <= -1:
                        raise "Numeric error"

                    c[j,i] = 1 / (kt + 1)
                    if p[i].fixed:
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
            ssq_old, p_old, jtr_old, hessian_old = ssq, p, jtr, hessian
        else:
            if mp == 0:
                mp = hessian[0,0]
            mp *= 5
            p, jtr, hessian = p_old, jtr_old, hessian_old

        for i in range(0, hessian.shape[0]):
            hessian[i,i] += mp

        hessianInv = hessian.I
        shifts = matlib.dot(hessianInv, jtr)
        for i in range(0, matlib.size(p)):
            if not p[i].fixed:
                p[i] -= shifts[i]
        it += 1

    p = p.T.tolist()[0]
    sigma = math.sqrt(ssq / (matlib.size(y) - 1))
    for i in range(0, len(p)):
        if p[i].fixed:
            p[i].sigma = 0
        else:
            p[i].sigma = sigma * hessianInv[i,i]

    ainf = a[len(p)-1,0]
    a0 = 0
    for i in range(0, len(p) - 1):
        p[i].a0minusAinf = a[i,0]
        a0 += p[i].a0minusAinf
    a0 += ainf

    absorbanceFit = []
    residualsValues = []
    for t in range(0, len(time)):
        afit = ainf
        for i in range(0, len(p) - 1):
            a0minusainf = a[i,0]
            if p[i].firstOrder:
                afit += p[i].a0minusAinf * math.exp(-p[i].value * (time[t]))
            else:
                afit += p[i].a0minusAinf / (p[i].value * (time[t]) + 1)
        absorbanceFit.append(afit)
        residualsValues.append(absorbance[t] - afit)

    # Remove the last p we added in this function.
    p = p[0:-1]

    residuals = data_fit.Residuals(residualsValues)
    return (p, absorbanceFit, residuals, ainf)
