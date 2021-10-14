#following https://medium.com/analytics-vidhya/testing-a-difference-in-population-proportions-in-python-89d57a06254

import numpy as np
import scipy.stats.distributions as dist

def binary_test(parameters, results):
    #2-prop p test for difference in proportions in results for those samples with parameters true vs false.
