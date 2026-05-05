from buildyn.walker.walker import Walker
from dataclasses import dataclass

@dataclass
class IntervalWalker:

    walker: Walker
    interval: int = 900

    
    def create_interval(self, start_time: int = 0, stop_time: int = 86_400):

        num_steps = int((stop_time - start_time) / self.interval)

        self.actions = self.walker.walk_pattern(num_steps=num_steps)


    def get_action(self, time: int = 0):

        if time % self.interval != 0:
            raise Exception(f"Intervalwalker could not get action for timestamp {time} with interval {self.interval}")
        
        idx = int(time / self.interval)

        return self.actions[idx]
        
        




        
