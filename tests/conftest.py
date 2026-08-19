from pathlib import Path

import pytest

RESOURCES = Path(__file__).resolve().parent.parent / "notebooks" / "resources"

DYMOLA_FMU = RESOURCES / "building_dymola_linux_v3.fmu"
OPENMODELICA_FMU = RESOURCES / "building_OM_linux_v2.fmu"


def dymola_init_values() -> dict:
    return {
        "weaDat.filNam": str(RESOURCES / "Munich.mos"),
        "internalGain.fileName": str(RESOURCES / "NoActivity.txt"),
        "hygienicalWindowOpening.fileName": str(RESOURCES / "no_opening.txt"),
        "UseInternalController.k": 0,
    }


# Same variable names as the Dymola-family FMU; kept as its own function since
# the two model families are free to diverge.
def openmodelica_init_values() -> dict:
    return {
        "weaDat.filNam": str(RESOURCES / "Munich.mos"),
        "internalGain.fileName": str(RESOURCES / "NoActivity.txt"),
        "hygienicalWindowOpening.fileName": str(RESOURCES / "no_opening.txt"),
        "UseInternalController.k": 0,
    }


@pytest.fixture
def make_dymola_fmu():
    """Factory for fresh, independently-instantiated Dymola-family FMU instances."""

    from buildyn.fmu import FMU

    def _make(start_time: int = 0):
        return FMU(
            fmu_file=str(DYMOLA_FMU),
            start_time=start_time,
            init_values=dymola_init_values(),
        )

    return _make


@pytest.fixture
def make_openmodelica_fmu():
    """Factory for fresh, independently-instantiated OpenModelica-family FMU instances."""

    from buildyn.fmu import FMU

    def _make(start_time: int = 0):
        return FMU(
            fmu_file=str(OPENMODELICA_FMU),
            start_time=start_time,
            init_values=openmodelica_init_values(),
        )

    return _make


@pytest.fixture
def openmodelica_fmu_path() -> str:
    return str(OPENMODELICA_FMU)


@pytest.fixture
def dymola_params() -> dict:
    return dymola_init_values()
