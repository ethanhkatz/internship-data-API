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
    #large counts condition
    assert x >= 10 and n-x >= 10
    return (n, x/n)

def binary_test(parameters, results):
    #two-tailed two-proportion p test for difference in proportions
    (n0, p0) = counts(0, parameters, results)
    (n1, p1) = counts(1, parameters, results)
    total_prop = counts(-1, parameters, results)[1]
    
    r_se = np.sqrt(1/(total_prop*(1-total_prop)) * (n0*n1/(n0+n1)))
    z = (p1-p0)*r_se
    return 2 * dist.norm.cdf(-abs(z))
