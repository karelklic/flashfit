from numpy import matrix
import math

def rcalcABC(k, a_0, t, y):
    """
    Parameter k (=parameter) is a column vector.
    Parameter A_0 is a number.
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
        c0.append(a_0 * math.exp(-k[0] * tloop))
    c[:,0] = c0

    # Second column of C contains concetrations of B
    c1 = []
    for tloop in t:
        c1.append(a_0 * k[0] / (k[1] - k[0]) * (math.exp(-k[0] * tloop) - math.exp(-k[1] * tloop)))
    c[:,1] = c1

    # Third column of C contains concentrations of C
    c2 = []
    for i in range(0, len(c0) - 1):
        c2.append(a_0 - c0[i] - c1[i])

    c = matrix([c0,c1,c2])
    c = c.transpose()
    
    # elimination of linear parameters
    a = linalg.lstsq(c, y)

    # residuals
    r = y - c * a
    
    return (r.transpose(), c, a)

def ngml(function, p, a_0, t, y):
    """
    Newton-Gauss-Levenberg/Marquardt algorithm
    Parameter p (=initial parameter) is a column vector.
    A_0 is a number (usually 1e-3)
    Parameter t contains a list of time values.
    Parameter y is a list of measured values.
    """

    # make column vector from y
    y = matrix(y).transpose()

    ssq_old = 1e50
    # Marquardt parameter
    mp = 0
    # convergence limit
    mu = 1e-4
    # step size for numerical diff
    delta = 1e-6

    it = 0 # iteration
    while it < 50:
        # call calc of residuals
        (r0, C, A) = function(p, A_0, t, y)
        ssq = sum(multiply(r0, r0))
        conv_crit = (ssq_old - ssq) / ssq_old
        fprintf(1,'it=%i, ssq=%g, mp=%g, conv_crit=%g\n',it,ssq,mp,conv_crit)
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
            for i in range(0, len(p) - 1):					
                p[i] = (1 + delta) * p[i]						
                r = function(p, a_0, t, y);				
                J(:,i) = (r - r0) / (delta * p[i]);			
                p[i] = p[i] / (1 + delta);						
        elif conv_crit < -mu: # divergence !
            if mp == 0:											
                mp = 1 # use Marquardt parameter
            else:
                mp = mp * 5										 
            p = p - delta_p # and take shifts back 
   
       # augment Jacobian matrix
       J_mp = [J; mp * eye(len(p))]	
       # augment residual vector
       r0_mp = [r0_old; zeros(size(p))] 
       # calculate parameter shifts
       delta_p = -J_mp \ r0_mp 
       # add parameter shifts
       p = p + delta_p 
       it += 1



[k,ssq,C,A,Curv,r]=nglm2(fname,k0,A_0,t,Y); 	               % call ngl/m
A_tot=C*A;
sig_y=sqrt(ssq/(prod(size(Y))-length(k)-(prod(size(A)))));     % sigma_r
sig_k=sig_y*sqrt(diag(inv(Curv))); % sigma_par

for i=1:length(k)
   fprintf(1,'k(%i): %g +- %g\n',i,k(i),sig_k(i));
end
fprintf(1,'sig_y: %g\n',sig_y);
figure(1);
subplot(2,1,1);plot(t,A_tot,t,Y,'.');
ylabel('absorbance')
subplot(2,1,2);plot(t,r);
xlabel('time');ylabel('residuals');
print('plot.png', '-dpng');
