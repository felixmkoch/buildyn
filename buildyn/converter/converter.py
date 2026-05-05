from buildyn.converter.converter_function import ConverterFunction

class Converter:

    def __init__(self):

        self.converter_functions: set[ConverterFunction] = []

        # For variables that should be used in the variation step of an fmu.
        self.converter_variables: dict[str, str | bool | float | int] = {}


    def add_converter_function(self, converter_function: ConverterFunction = None):

        if not converter_function:
            return
        
        self.converter_functions.append(converter_function)


    def get_converter_functions(self) -> list[ConverterFunction]:

        return self.converter_functions
    

    def update_converter_variables(self, d: dict[str, str | bool | float | int]):

        self.converter_variables.update(d)


    def get_converter_variables(self) -> dict[str, str | bool | float | int]:

        return self.converter_variables

        