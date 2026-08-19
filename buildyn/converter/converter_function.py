from abc import ABC

class ConverterFunction(ABC):

    def __init__(self):

        pass


    def convert(self, var_dict: dict):

        raise NotImplementedError("Function convert not implemented in this ConverterFunction. Please override this method first.")
