import platform

from buildyn.converter import Converter
from buildyn.examples.builda.converter_functions.Component_configurator import Component_configurator
from buildyn.examples.builda.converter_functions.Link_resolver import Link_resolver
from buildyn.examples.builda.converter_functions.Miscellaneous_handler import Miscellaneous_handler
from buildyn.examples.builda.converter_functions.Model_compatibility_layer import Model_compatibility_layer
from buildyn.examples.builda.converter_functions.Nominal_cooling_power_calculator import Nominal_cooling_power_calculator
from buildyn.examples.builda.converter_functions.Nominal_heating_power_calculator import Nominal_heating_power_calculator
from buildyn.examples.builda.converter_functions.RC_Distribution_Configurator import RC_Distribution_Configurator
from buildyn.examples.builda.converter_functions.Zone_dimensions_calculator import Zone_dimensions_calculator
from buildyn.examples.builda.converter_functions.Component_properties_calculator import Component_properties_calculator


# Selects the BuilDa FMU built for the current host OS.
def get_builda_fmu_path() -> str:
    system = platform.system()
    if system == "Windows":
        return "resources/building_OM_windows_v2.fmu"
    elif system == "Linux":
        return "resources/building_dymola_linux_v3.fmu"
    else:
        raise RuntimeError(f"No BuilDa FMU available for host OS '{system}'.")


# Helper function to retrieve the pre-configured BuilDa FMU with all converter functions and default values set.
def get_configured_builda_fmu(internal_controller: bool = False):

    converter = Converter()

    # All the converter functiosn from BuilDa 2.0
    converter_functions = [Link_resolver, Miscellaneous_handler, Model_compatibility_layer, Zone_dimensions_calculator, Component_configurator, RC_Distribution_Configurator, Component_properties_calculator, Nominal_heating_power_calculator, Nominal_cooling_power_calculator]

    for cf in converter_functions:
        converter.add_converter_function(cf())

    converter_variables = {
        "zone_length": 9.4125,
        "zone_width": 8,
        "floor_height": 3.04,
        "n_floors": 2,
        "fAWin_south": 0.14056,
        "fAWin_west": 0.14056,
        "fAWin_north": 0.14056,
        "fAWin_east": 0.14056,
        "fATransToAWindow": 0.9,
        "fARoofToAFloor": 1.63612217795485,
        "fAInt": 1.238235294117647,
        "heatCapacity_furniture_per_m2": 2230,
        "UExt": 0.665,
        "heatCapacity_wall": 192000,
        "UFloor": 0.514,
        "heatCapacity_floor": 483840,
        "UInt": 1,
        "heatCapacity_internalWall": 145154,
        "URoof": 0.402,
        "heatCapacity_roof": 81240,
        "UWin": 3.2,
        "thermalZone.gWin": 0.7,
        "heatRecoveryRate": 0,
        "airChangeRate": 0.3,
        "heatingCurve_steepness": 1,
        "relative_heatPump_efficiency": 0.8,
        "internalGainsConvectiveFraction": 0.4,
        "heatingConvectiveFraction": 1,
        "weaDat.fileName": "resources/Munich.mos",
        "internalGain.fileName": "resources/NoActivity.txt",
        "hygienicalWindowOpening.fileName": "resources/no_opening.txt",
        "roomTempLowerSetpoint": 18,
        "roomTempUpperSetpoint": 22,
        #"UseInternalController": 0,
        "extWall_C_distribution": "monolythic",
        "floor_C_distribution": [478800, 5040, 0.001],
        "roof_C_distribution": [22440, 58800, 0.001],
        "extWall_R_distribution": "monolythic",
        "floor_R_distribution": [0.0525, 0.0525, 0.1579, 0.0001],
        "roof_R_distribution": [1.1085, 1.1085, 0.1, 0.0001],
        "intWall_R_distribution": "monolythic",
        "intWall_C_distribution": "monolythic",
        "Rsi_extWall": 0.13333333333333333,
        "Rsi_intWall": 0.13333333333333333,
        "Rsi_floor": 0.17543859649122806,
        "Rsi_roof": 0.1,
        "Rse_extWall": 0.04,
        "Rse_roof": 0.04,
        "Rsi_window": 0.13333333333333333,
        "Rse_window": 0.05,
        "ta_min": None,
        "ti_set": None
    }

    # Set the converter variables in the converter. This also updates previously set variables.
    converter.update_converter_variables(converter_variables)

    from buildyn import FMU
    import json

    # Example FMU from BuilDa 2.0
    fmu_path = get_builda_fmu_path()

    # Initial variables from the BuilDa 2.0 FMU -> Needs extra variables here because the BuilDa FMU is weird. For other use-cases you don't have to do this.
    with open("resources/fmu_state_dict.json", "r") as f:
        start_variables = json.load(f)

    start_variables.update({
        "weaDat.filNam": "resources/Munich.mos",
        "internalGain.fileName": "resources/NoActivity.txt",
        "hygienicalWindowOpening.fileName": "resources/no_opening.txt",
        "UseInternalController.k": 1 if internal_controller else 0
    })

    # FMU object from the buil_dyn package
    fmu = FMU(fmu_file=fmu_path, init_values=start_variables)

    fmu.set_converter(converter=converter)

    return fmu
