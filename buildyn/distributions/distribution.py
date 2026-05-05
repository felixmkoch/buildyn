from abc import ABC, abstractmethod

class Distribution(ABC):

    @abstractmethod
    def sample_one(self):

        pass
    

    def sample_multiple(self, n: int):

        return [self.sample_one() for _ in range(n)]