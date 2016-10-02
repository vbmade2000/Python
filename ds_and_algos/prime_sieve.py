"""Prime number generator between a range of two numbers.
Uses Sieve of Eratosthenes method
"""
import math
lower_bound = 1 
upper_bound = 20

def get_primes(lower_bound, upper_bound):
    """Calculates prime nos and returns list of them"""
    if lower_bound == 1:
        lower_bound = 2
    nos = dict(zip(range(lower_bound, upper_bound+1), [True] * (upper_bound - lower_bound)))
    square_root = int(math.sqrt(upper_bound))
    for i in range(lower_bound, square_root + 1):
        for j in range(i*2, upper_bound+1, i):
            nos[j] = False
    primes = filter(lambda x: nos[x] == True, nos.keys())
    return primes

print get_primes(lower_bound, upper_bound)
