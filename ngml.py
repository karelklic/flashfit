# -*- coding: utf-8 -*- (Python reads this)
import numpy
from numpy import matrix, matlib, linalg
import math

class BaseModel:
    def calculate(self, time, absorbance, implementation, logger):
        """
        Calculates the fit, residuals, and reaction rate coefficient
        from absorbance values.

        Parameters
        ----------
        time : array of times when a measurement of absorbance happened
        absorbance : array of absorbance values
            Must be the same size as `time`.
        implementation: 0 or 1
            0 is the new implementation
            1 is the old implementation

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
        """
        # Prepare initial parameters
        (p, p_firstOrder)  = self.getInitialParameters(time)
        # TODO: fix some parameters right here.
        p_fixed = []
        for i in range(0, len(p)):
            p_fixed.append(False)

        # Run the fitting algorithm.
        # We have two possibilities: ngml and ngml2
        # ngml is from the book
        # ngml2 is from the old source
        if implementation == 1:
            return self.ngml2(p, p_firstOrder, p_fixed, time, absorbance, logger)
        else:
            a_0 = 1e-3
            return self.ngml(p, a_0, time, absorbance, logger)

    def ngml2(self, p, p_firstOrder, p_fixed, time, absorbance, logger):
        """
        Calculates the fit, residuals, and reaction rate coefficients from
        absorbance values.

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
        """
        # make column vector from y
        y = matrix(absorbance).T

        # Add another parameter containing linear part.
        p.append(0)
        p_firstOrder.append(False)
        p_fixed.append(True)

        # make column vector from p
        p = matrix(p).T

        ssq_old = 1e100
        # Marquardt parameter
        mp = 0
        # convergence limit
        mu = 1e-4

        def calcHessianJtrA(dc, c, y):
            ctc = matlib.dot(c.T, c)
            ctcinv = ctc.I
            aux = matlib.dot(ctcinv, c.T)
            a = matlib.dot(aux, y)
            aux = matlib.dot(c, a)
            r = aux - y
            ssq = 0
            for i in range(0, r.shape[0]):
                for j in range(0, r.shape[1]):
                    ssq += r[i,j] * r[i,j]
            j = matlib.empty([dc[0].shape[0], len(dc)])
            dq = []
            for p in range(0, len(dc)):
                dct = dc[p].T
                dctc = matlib.dot(dct, c)
                dq.append(dctc + dctc.T)
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
            hessian = matlib.dot(j.T, j)
            jtr = matlib.dot(j.T, r)
            return (hessian, jtr, a, ssq)

        it = 0 # iteration
        end = False
        while it < 50 and not end:
            # Calculate C and dC
            c = matlib.empty([len(time), matlib.size(p)])
            dc = []
            for i in range(0, matlib.size(p)):
                dci = matlib.empty([len(time), matlib.size(p)])
                for j in range(0, len(time)):
                    kt = p[i] * time[j]
                    if p_firstOrder[i]:
                        c[j,i] = math.exp(-kt)
                        if p_fixed[i]:
                            dci[j,i] = 1
                        else:
                            dci[j,i] = -c[j,i] * time[j]
                    else:
                        c[j,i] = 1 / (kt + 1)
                        if p_fixed[i]:
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

            for i in range(0, matlib.size(p)):
                hessian[i,i] += mp

            hessianInv = hessian.I
            shifts = matlib.dot(hessianInv, jtr)
            for i in range(0, matlib.size(p)):
                if not p_fixed[i]:
                    p[i] -= shifts[i]
            it += 1

        p = p.T.tolist()[0]
        sigma = math.sqrt(ssq / (matlib.size(y) - 1))
        sigma_p = []
        for i in range(0, len(p)):
            if p_fixed[i]:
                sigma_p.append(0)
            else:
                sigma_p.append(sigma * hessianInv[i,i])

        ainf = a[len(p)-1,0]
        a0 = 0
        for i in range(0, len(p) - 1):
            a0minusainf = a[i,0]
            a0 += a0minusainf
        a0 += ainf

        absorbanceFit = []
        residuals = []
        for t in range(0, len(time)):
            afit = ainf
            for i in range(0, len(p) - 1):
                a0minusainf = a[i,0]
                if p_firstOrder[i]:
                    afit += a0minusainf * math.exp(-p[i] * (time[t]))
                else:
                    afit += a0minusainf / (p[i] * (time[t]) + 1)
            absorbanceFit.append(afit)
            residuals.append(absorbance[t] - afit)

        # Remove the last p we added in this function.
        p = p[0:-1]
        sigma_p = sigma_p[0:-1]
        return (p, sigma_p, absorbanceFit, residuals)

    def ngml(self, p, a_0, t, y, logger):
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
        # make column vector from y
        y = matrix(y).transpose()
        # make column vector from p
        p = matrix(p).transpose()
        # make column vector from t
        t = matrix(t).transpose()

        ssq_old = 1e100
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
            (r0, c, a) = self.rcalc(p, a_0, t, y)
            ssq = matlib.sum(matlib.multiply(r0, r0))
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
                    r = self.rcalc(p, a_0, t, y)[0]
                    j[:,i] = ((r - r0) / (delta * p[i]))[:,0]
                    p[i] = p[i] / (1 + delta)
            elif conv_crit < -mu: # divergence !
                if mp == 0:
                    mp = 1 # use Marquardt parameter
                else:
                    mp *= 5
                p = p - delta_p # and take shifts back

            # augment Jacobian matrix
            j_mp = matlib.vstack((j, mp * matlib.eye(len(p))))
            # augment residual vector
            r0_mp = matlib.vstack((r0_old, matlib.zeros(p.shape)))
            # calculate parameter shifts
            delta_p = linalg.lstsq(-j_mp, r0_mp)[0]
            # add parameter shifts
            p = p + delta_p
            it += 1

        # Curvature matrix
        curv = matlib.dot(j.H, j)

        # Set parameters (speed constants?) and sigma for parameters
        logger("Fitting absorbance: final calculations")
        sigma_y = math.sqrt(ssq / (matlib.size(y) - matlib.size(p) - matlib.size(a)))
        p = p.transpose().tolist()[0]
        sigma_p = sigma_y * numpy.sqrt(matlib.diag(linalg.inv(curv)))
        sigma_p = sigma_p.tolist()

        # Set absorbance fit curve
        a_tot = matlib.dot(c, a)
        absorbanceFit = a_tot[:,0].transpose().tolist()[0]

        # Set residuals
        # Should 'r' be used, or maybe 'r0' should be?
        residuals = r0.transpose().tolist()[0]
        return (p, sigma_p, absorbanceFit, residuals)

class ModelABC(BaseModel):
    name = u"A→B→C"

    def getInitialParameters(self, time):
        return ([10 / (time[len(time) / 2] - time[0]), 3 / (time[len(time) / 2] - time[0])],
                [True, False])

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
        # First column of C contains concentrations of A
        c0 = a_0 * matlib.exp(-k[0,0] * t)
        # Second column of C contains concetrations of B
        c1 = a_0 * (k[0,0] / (k[1,0] - k[0,0])) * (matlib.exp(-k[0,0] * t) - matlib.exp(-k[1,0] * t))
        # Third column of C contains concentrations of C
        c2 = a_0 - c0 - c1
        c = matlib.hstack((c0, c1, c2))

        # elimination of linear parameters
        # [0] because we just need the result, not the residuals etc.
        a = linalg.lstsq(c, y)[0]

        # calculate residuals
        # ca = c * a (matrix multiplication)
        r = y - matlib.dot(c, a)
        return (r, c, a)

class ModelFirst(BaseModel):
    name = u"Single First Order"

    def getInitialParameters(self, time):
        return ([10 / (time[len(time) / 2] - time[0])],
                [True])

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
        # First column of C contains concentrations of A
        c = a_0 * matlib.exp(-k[0,0] * t)

        # elimination of linear parameters
        # [0] because we just need the result, not the residuals etc.
        a = linalg.lstsq(c, y)[0]

        # calculate residuals
        r = y - matlib.dot(c, a)
        return (r, c, a)

class ModelFirst2(BaseModel):
    name = u"Dual First Order"

    def getInitialParameters(self, time):
        return ([10 / (time[len(time) / 2] - time[0]), 3 / (time[len(time) / 2] - time[0])],
                [True, True])

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
        c0 = a_0 * matlib.exp(-k[0,0] * t)
        c1 = a_0 * matlib.exp(-k[1,0] * t)
        c = matlib.hstack((c0, c1))

        # elimination of linear parameters
        # [0] because we just need the result, not the residuals etc.
        a = linalg.lstsq(c, y)[0]

        # calculate residuals
        r = y - matlib.dot(c, a)
        return (r, c, a)
