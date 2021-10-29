#following https://medium.com/analytics-vidhya/testing-a-difference-in-population-proportions-in-python-89d57a06254

import numpy as np
import scipy.stats.distributions as dist

def counts(target, parameters, results):
    #number and proportion of successes and total number of in samples with "parameters" value of "target".
    #if "target" is -1 it counts everything.
    x = 0
    n = 0
    for i, sample in enumerate(parameters):
        if target == -1 or sample == target:
            x += results[i]
            n += 1
    return (n, x)

def binary_test(parameters, results):
    #two-tailed two-proportion p test for difference in proportions
    (n0, x0) = counts(0, parameters, results)
    (n1, x1) = counts(1, parameters, results)
    (nt, xt) = counts(-1, parameters, results)
    #large counts condition
    lcc = lambda n, x: x <= 10 or n-x <= 10
    if lcc(n0, x0) or lcc(n1, x1):
        return -1

    #reciprocal of standard error
    r_se = np.sqrt(n0*n1*nt/(xt*(nt-xt)))
    #z-score
    z = (x1/n1-x0/n0)*r_se
    return 2 * dist.norm.cdf(-abs(z))
