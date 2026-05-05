from abc import abstractmethod

from buildyn.distributions.distribution import Distribution

class DiscreteDistribution(Distribution):

    @abstractmethod
    def sample_all(self):

        pass