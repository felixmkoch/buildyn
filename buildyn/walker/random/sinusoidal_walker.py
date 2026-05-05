import math
from buildyn.walker.walker import Walker
from buildyn.distributions.discrete.discrete_distribution import DiscreteDistribution
from buildyn.distributions.discrete.random_choice import RandomChoiceDistribution

class SinusoidalWalker(Walker):

    def __init__(self,
                 min: float = 0.0,
                 max: float = 1.0,
                 freq_distribution: DiscreteDistribution = RandomChoiceDistribution(list(range(5, 40))),
                 amp_distribution: DiscreteDistribution = RandomChoiceDistribution([0.2, 0.4, 0.6, 0.8, 1.0]),
                 steady_distribution: DiscreteDistribution = RandomChoiceDistribution(list(range(1, 8))),
                 ):

        self.min = min
        self.max = max
        self.mid = (max + min) / 2
        self.diff = (max - min)

        self.freq_distribution = freq_distribution
        self.amp_distribution = amp_distribution
        self.steady_distribution = steady_distribution

        self.phase = 0.0  # GLOBAL phase (important!)

    def walk_pattern(self, num_steps: int = 1):

        result = []

        while len(result) < num_steps:

            freq = self.freq_distribution.sample_one()
            amp = self.amp_distribution.sample_one()
            steady = self.steady_distribution.sample_one()

            # convert freq → angular step
            omega = 2 * math.pi / freq

            for _ in range(freq):

                value = self.mid + (self.diff / 2) * amp * math.sin(self.phase)

                # IMPORTANT: avoid hard clamping if possible
                value = max(self.min, min(self.max, value))

                result.append(value)

                self.phase += omega  # continuous evolution

            # steady hold (no weird feedback from last sine value)
            result.extend([result[-1]] * steady)

        return result[:num_steps]