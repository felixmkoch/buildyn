from buildyn.distributions.discrete.discrete_distribution import DiscreteDistribution
import random

class RandomChoiceDistribution(DiscreteDistribution):

    def __init__(self, choices: list | set):

        super().__init__()

        self.choices = choices


    def sample_one(self):
        
        return random.choice(self.choices)
    

    def sample_all(self):
        
        return self.choices
    