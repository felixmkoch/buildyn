from buildyn.fmu import FMU
from typing import Dict
from buildyn.walker.walker import Walker
from buildyn.walker.interval_walker import IntervalWalker
from buildyn.distributions.distribution import Distribution
from buildyn.distributions.discrete.discrete_distribution import DiscreteDistribution

from copy import copy
import itertools

class BuilDyn:

    def __init__(self, 
                 fmu: FMU,
                 observables: list = []
                 ):

        self.variation_distributions: Dict[str, Distribution] = dict()

        self.walker_distributions: Dict[str, IntervalWalker | DiscreteDistribution] = dict()

        self.fmu: FMU = fmu

        self.observables = observables


    def add_variation_distribution(self, variable: str, distribution: Distribution):

        self.variation_distributions[variable] = distribution


    def add_walker_distribution(self, variable: str, distribution: IntervalWalker | DiscreteDistribution):

        self.walker_distributions[variable] = distribution


    def sample_one(self,
                   simulation_period: int = 24*3600,
                   step_size: int = 900):
        

        # Sample one fmu with random variation
        fmu = self.sample_one_fmu()

        # Sample the walker from the correpnding walker distributions
        walker: Dict[str, Walker] = dict()

        for param, walker_dist in self.walker_distributions.items():
            
            if isinstance(walker_dist, IntervalWalker):

                walker[param] = walker_dist
                continue

            walker[param] = walker_dist.sample_one()

        res = fmu.simulate(
                    simulation_period=simulation_period,
                    step_size=step_size,
                    observables=self.observables,
                    walker=walker
                )

        return res
    

    def sample_one_fmu(self):

        fmu = self.fmu.__copy__()

        fmu_initial_variables = dict()

        # Sample the variations from the corresponding distributions
        for param, distirbution in self.variation_distributions.items():

            variable_value = distirbution.sample_one()

            fmu_initial_variables[param] = variable_value

            fmu.set_initial_variables(variables=fmu_initial_variables)

        return fmu
    

    def sample_all_fmus(self):

        all_fmus = []
        all_samples = {}

        # Check if all distributions in this class are Discrete, else it would not be possible to really sample all.

        for variable, distribution in self.variation_distributions.items():

            if not isinstance(distribution, DiscreteDistribution):

                return TypeError(f"Sampling all FMUs in not possible because {distribution.__class__.__name__} is not a discrete distribution.")
            
            all_samples[variable] = distribution.sample_all()

        keys = list(all_samples.keys())
        values = list(all_samples.values())

        # Making the cartesian product of the sample_all
        for combination in itertools.product(*values):

            variation_dict = dict(zip(keys, combination))

            fmu = copy(self.fmu)
            fmu.set_initial_variables(variation_dict)

            all_fmus.append(fmu)

        return all_fmus



        



            

            

        


