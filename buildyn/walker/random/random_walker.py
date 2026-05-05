from buildyn.walker.walker import Walker
import random

class RandomWalker(Walker):

    def __init__(self, 
                 min: int = 0,
                 max: int = 1,
                 is_discrete: bool = False
                 ):
        
        super().__init__()
        
        self.min = min
        self.max = max
        self.is_discrete = is_discrete


    def walk_pattern(self, num_steps: int = 1):

        if self.is_discrete:
            return [random.randint(self.min, self.max) for _ in range(num_steps)]
        
        return [random.uniform(self.min, self.max) for _ in range(num_steps)]
