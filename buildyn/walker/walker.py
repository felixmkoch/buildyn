from abc import ABC, abstractmethod

class Walker(ABC):

    @abstractmethod
    def walk_pattern(self, num_steps: int = 1):

        pass