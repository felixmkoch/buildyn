from buildyn.distributions.continuous.continuous_distribution import ContinuousDistribution
import random

class GaussDistribution(ContinuousDistribution):

    def __init__(self, mu, sigma, min: float = None, max: float = None):

        super().__init__()

        self.mu = mu
        self.sigma = sigma
        self.min = min
        self.max = max


    def sample_one(self):

        # No bounds → return normally
        if self.min is None and self.max is None:
            return random.gauss(self.mu, self.sigma)

        # Otherwise, keep sampling until value is within bounds
        for _ in range(999):
            value = random.gauss(self.mu, self.sigma)

            if self.min is not None and value < self.min:
                continue
            if self.max is not None and value > self.max:
                continue

            return value
        
        # We assume that the min-max is near-impossible to hit.
        raise Exception(f"Gauss distribution: Not realistic with min {self.min} and max {self.max}")
    