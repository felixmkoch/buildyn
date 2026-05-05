from buildyn.walker.walker import Walker
from buildyn.distributions.discrete.discrete_distribution import DiscreteDistribution
from buildyn.distributions.discrete.random_choice import RandomChoiceDistribution

# Our custom Walker class we can use in combination with the MoPrior package.
class RampWalker(Walker):

    def __init__(self, 
                 min: int = 0, 
                 max: int = 1, 
                 freq_distribution: DiscreteDistribution = RandomChoiceDistribution(list(range(2, 16))),
                 stead_distribution: DiscreteDistribution = RandomChoiceDistribution(list(range(1, 8))),
                 ):
        self.min = min
        self.max = max
        self.diff = abs(max - min)
        self.freq_distribution = freq_distribution
        self.stead_distribution = stead_distribution

    # Override this walk function.
    def walk_pattern(self, num_steps: int = 1):

        result = []
        while len(result) < num_steps:
            freq = self.freq_distribution.sample_one()
            result.extend([self.min + (self.diff / (freq-1)) * i for i in range(freq)])
            result.extend([self.max] * self.stead_distribution.sample_one())
            result.extend([self.max - (self.diff / (freq-1)) * i for i in range(1, freq-1)])
            result.extend([self.min] * self.stead_distribution.sample_one())

        return result[:num_steps]