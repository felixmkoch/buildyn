from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from buildyn.walker.interval_walker import IntervalWalker
from buildyn.converter.converter import Converter
from typing import Dict, List
import pandas as pd

from copy import deepcopy

class FMU:

    def __init__(self,
                 fmu_file: str,
                 start_time: int = 0,
                 init_values: dict = {},            # A dict of variables - without these the FMU object cannot be created.
                 ):
        
        # Set args of init as class attributes
        self.fmu_file: str = fmu_file
        self.start_time: int = start_time
        self.init_values: dict = init_values
        self.fmu_state_dict: dict = {}
        self.updated_fmu_state: dict = {}       # Updated state that memorizes whether FMU changes were made in initialization.
        self.has_entered_exited_mode: bool = False

        # FMU specifics
        self.model_description = read_model_description(fmu_file)
        self.guid: str = self.model_description.guid
        self.model_identifier: str = self.model_description.coSimulation.modelIdentifier
        self.model_variables = self.model_description.modelVariables
        self.unzip_dir = extract(fmu_file)

        self.time = start_time
        self.converter = None

        # Load the FMU as a FmPy2 FMU object
        self.fmu = FMU2Slave(
            guid=self.guid,
            unzipDirectory=self.unzip_dir,
            modelIdentifier=self.model_identifier,
            instanceName='fmu_instance'
        )

        # Map matching internal FMU types to python type casts for easier access.
        self.__type_map = {
            "Real": float,
            "String": str,
            "Integer": int,
            "Boolean": bool
        }

        # Skim through FMU variables once to later access them easily
        self.variable_types = dict()
        self.variable_references = dict()
        self.variable_starts = dict()
        self.variable_names = list()

        for variable in self.model_variables:
            name = variable.name
            self.variable_names.append(name)
            self.variable_references[name] = variable.valueReference
            self.variable_starts[name] = variable.start
            self.variable_types[name] = variable.type

        # If state dict is not yet available, create it FROM FMU FILE != FMU_START_DICT.JSON!!
        self.fmu_state_dict = {
            k: self.__type_map.get(self.variable_types[k], lambda x: x)(v) 
            if v is not None else None
            for k, v in self.variable_starts.items() 
        }

        # only update parameters from the fmu_state_dict that are None
        self.fmu_state_dict.update(
            {k: v for k, v in self.init_values.items() if self.fmu_state_dict.get(k, -1) is None}
        )

        self._init_fmu()

        # Save initial FMU state here
        self.start_state = self.fmu.serializeFMUState(state=self.fmu.getFMUState())

        
    def _init_fmu(self):

        self.fmu.instantiate()
        self.fmu.setupExperiment(startTime=self.time)


    def reset_fmu_state(self):

        # Note: This currently leads to an exit() call - I don't know why. TODO: Inverstigate why this happens and fix afterwards.

        self.fmu.reset()

        self.has_entered_exited_mode = False


    def set_converter(self, converter: Converter):

        self.converter = converter


    def remove_converter(self):

        self.converter = None


    def set_initial_variables(self, variables: dict = {}):


        if self.has_entered_exited_mode:
            raise Exception("FMU already entered the initialization mode. You probably called set_initial_variables more than once, which is not allowed.")

        self.fmu.enterInitializationMode()

        # deepcopy fmu_state_dict variables and initial values
        variables_to_update = deepcopy(self.fmu_state_dict)
        variables_to_update |= self.init_values

        # if converter is specified, iteratively update state dict with converter function output
        if self.converter:

            conversion_result_dict = self.converter.get_converter_variables()

            for converter_function in self.converter.get_converter_functions():

                convert_dict = self.fmu_state_dict | self.init_values | variables | conversion_result_dict

                conversion_result_dict |= converter_function.convert(convert_dict)

            variables_to_update |= conversion_result_dict

        # include args of this function
        variables_to_update |= variables

        # Save updated variables for later (copy for instance).
        self.updated_fmu_state.update(variables_to_update)

        for name, value in variables_to_update.items():

            self.set_variable(name=name, value=value)

        self.fmu.exitInitializationMode()

        self.has_entered_exited_mode = True

        # Start state may vary now due to initialization.
        self.start_state = self.fmu.serializeFMUState(state=self.fmu.getFMUState())


    def _enter_exit_init_mode(self):
        # Not sure if this is all right. Need to check whether this works as intended. Until then, init_fmu({}) is a workaround.
        # self.init_values possibly does not contain all necessary variables, as they are updated from the self.fmu_state_dict

        self.fmu.enterInitializationMode()

        # Initial values that are needed.   TODO: Look if this is the best way here ...
        for name, value in self.init_values.items():
            self.set_variable(name=name, value=value)

        self.fmu.exitInitializationMode()


    def set_variable(self, name: str, value: bool | int | str | float):

        if not name or name not in self.variable_names:
            return
        
        reference = self.variable_references[name]

        try:
            match self.variable_types[name]:
                case "Real":
                    return self.fmu.setReal([reference], [value])
                case "String":
                    return self.fmu.setString([reference], [str(value)])
                case "Boolean":
                    return self.fmu.setBoolean([reference], [value])
                case "Integer":
                    return self.fmu.setInteger([reference], [value])
                
        except Exception:
            pass
            
    
    def get_variable(self, name: str = ""):

        # If not in right mode -> go there.
        if not self.has_entered_exited_mode:
            self._enter_exit_init_mode()
            self.has_entered_exited_mode = True

        if not name or name not in self.variable_names:
            raise Exception(f"Variable with name {name} not in the FMU variables.")
        
        reference = self.variable_references[name]
        
        match self.variable_types[name]:
            case "Real":
                return self.fmu.getReal([reference])[0]
            case "String":
                return self.fmu.getString([reference])[0]
            case "Boolean":
                return self.fmu.getBoolean([reference])[0]
            case "Integer":
                return self.fmu.getInteger([reference])[0]
            case "Enumeration":
                return self.fmu.getReal([reference])[0]
            
        raise Exception(f"Variable with name {name} has the variable type {self.variable_types[name]}, which is not defined.")
    

    def step_fmu(self, step_size):

        # If not in right mode -> go there.
        if not self.has_entered_exited_mode:
            self._enter_exit_init_mode()
            self.has_entered_exited_mode = True

        self.fmu.doStep(
            currentCommunicationPoint=self.time,
            communicationStepSize=step_size
        )

        self.time = self.time + step_size


    def _init_interval_walkers(self, 
                               start_time: int = 0, 
                               stop_time: int = 86_400, 
                               step_size: int = 900, 
                               interval_walkers: List[IntervalWalker] = []):
        
        stop_points = set()

        stop_points.update([x for x in range(start_time, stop_time, step_size)])
        
        for walker in interval_walkers:

            walker.create_interval(
                start_time=start_time,
                stop_time=stop_time
            )

            stop_points.update([x for x in range(start_time, stop_time, walker.interval)])

        stop_points = list(stop_points)
        stop_points.sort()

        return stop_points[1:]
    

    def _do_walks(self, start_time: int, time: int, walkers: Dict[str, IntervalWalker] = {}):

        for param, iwalker in walkers.items():

            if time % iwalker.interval != 0:
                continue

            self.set_variable(param, iwalker.get_action(time - start_time))


    def simulate(self,
                 simulation_period: int = 86_400,
                 step_size: int = 900,
                 observables: list[str] = [],
                 walker: Dict[str, IntervalWalker] = {} 
                 ):
        
        rows = []
        
        start_time = self.time
        stop_time = start_time + simulation_period

        # If not in right mode -> go there.
        if not self.has_entered_exited_mode:
            self._enter_exit_init_mode()
            self.has_entered_exited_mode = True


        stop_points = self._init_interval_walkers(
            start_time=start_time,
            stop_time=stop_time,
            step_size=step_size,
            interval_walkers=list(walker.values())
        )

        if not observables:
            observables = list(self.variable_names)

        # Append the header to the rows
        header = ["time"] + observables

        for time in stop_points:

            last_step_size = time - self.time

            self._do_walks(start_time=start_time, time=time, walkers=walker)

            if time % step_size == 0:
                rows.append([time] + [self.get_variable(name) for name in observables])

            self.step_fmu(step_size=last_step_size)

        df = pd.DataFrame(rows, columns=header)

        return df
    

    def __copy__(self):

        fmu_copy = FMU(
            fmu_file=deepcopy(self.fmu_file),
            init_values=deepcopy(self.updated_fmu_state if self.updated_fmu_state else self.init_values),
            start_time=deepcopy(self.start_time)
        )

        fmu_copy.set_converter(self.converter)

        return fmu_copy

    def __str__(self):
        return f"buildyn.fmu.FMU object at {hex(id(self))}:\n\n\t- src file: {self.fmu_file}\n\t- time: {self.time}\n\t- initialized: {self.has_entered_exited_mode}"

    def __repr__(self):
        return f"buildyn.fmu.FMU object at {hex(id(self))}:\n\n\t- src file: {self.fmu_file}\n\t- time: {self.time}\n\t- initialized: {self.has_entered_exited_mode}"


        







            

        





        