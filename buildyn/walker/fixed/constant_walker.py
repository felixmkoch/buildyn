from buildyn.walker.walker import Walker

class ConstantWalker(Walker):

    def __init__(self, 
                 constant: int = 0
                 ):
        
        super().__init__()
        
        self.constant = constant


    def walk_pattern(self, num_steps: int = 1):

        return [self.constant for _ in range(num_steps)]
