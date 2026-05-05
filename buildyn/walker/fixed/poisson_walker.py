from buildyn.walker.walker import Walker
import numpy as np

class PoissonWalker(Walker):

    '''
    Walker to return constant values for a certain number of time after each other.
    The number of constant values that follow each other is determined by a Poisson distribution. 
    The value itself is randomly sampled from an interval. 

    Args:
        - min: Minimal value to be sampled as a constant.
        - max: Maximum value to be sampled as a constant.
        - lam: Lambda parameter of the Poisson distribution.
        - is_discrete: Flag whether the constants should be Integers or floats.
    '''

    def __init__(self,
                 min: int = 0,
                 max: int = 1,
                 lam: int = 1,
                 is_discrete: bool = False
                 ):
        
        super().__init__()
        
        self.min = min
        self.max = max
        self.lam = lam
        self.is_discrete = is_discrete


    def _sample_poisson(self):

        return np.random.poisson(self.lam)
    

    def _sample_num(self):

        if self.is_discrete:

            return np.random.randint(self.min, self.max + 1)
        
        else:

            return np.random.uniform(self.min, self.max)


    def walk_pattern(self, num_steps: int = 1):

        to_return = []

        while len(to_return) < num_steps:
            
            to_return += [self._sample_num()] * self._sample_poisson()

        return to_return[:num_steps]
