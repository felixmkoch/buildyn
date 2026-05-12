[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3100/)
[![GitHub License](https://img.shields.io/badge/License-MIT-blue)](https://inf-git.th-rosenheim.de/felix.koch/mo_prior/-/blob/main/LICENSE)
![PyPI](https://img.shields.io/badge/PyPI-todo-white)
![Version](https://img.shields.io/badge/Version-1.0.0-green)

BuilDyn is an open-source free-to-use PyPI package to help simulating Functional Mockup Units (FMU) for buildings. Its primarily use is probing buildings thermal dynamics, randomizing building parameters, and demand-driven building simulation. As this is an open-source project, we encourage users and researchers to contribute with new ideas and directions to follow for future releases! 

## Setup

The only hard requirement for this package is python == 3.13.  
 Aside from that, there are two ways to build this package in your environment:

### Installation via Pip

We distribute the newest version of this package over PyPI [available in future releases]. 

```bash
pip install buildyn
```

### Installation from source code

Aside from the pip installation, you can also build the newest version of this package from scratch. First, clone this repository.

```
git clone https://github.com/felixmkoch/buildyn.git
```

After that, you can pip install this package into your python environemnt using  
```
pip install .
``` 

## Strcture

The package has two main classes to consider: FMU and BuilDyn. FMU is a modified and extended wrapper around the FmuSlave from FmPy. BuilDyn enables users full control over variations, walker distributions, and demand-dirven simulation. Multiple functionalities are inspired by [BuilDa](https://github.com/fabianraisch/BuilDa). For further information about the structure we refer to our paper.

## Usage

One general use-case would be the following:  
```python
from buildyn import FMU
from buildyn.buildyn import BuilDyn
from buildyn.walker.random.random_walker import RandomWalker
from buildyn.walker.interval_walker import IntervalWalker


fmu_path = "model1.fmu"

start_variables = {
    "weaDat.filNam": "resources/Munich.mos",
    "internalGain.fileName": "resources/NoActivity.txt"
}

fmu = FMU(fmu_path, init_values=start_variables)

observables = ["thermalZone.TAir", "heatingPower"]

rw = RandomWalker(min=10, max=500, is_discrete=True)
iw = IntervalWalker(rw, 900) # 900 is the step size of the walker.

buildyn = BuilDyn(fmu, observables=observables)

buildyn.add_walker_distribution("heatingPower", iw)

print(buildyn.sample_one())
```

To explore all features of BuilDyn, we refer to our notebooks; each of them thematizes one key part.

## Citation
If you are using BuilDyn, consider citing the corresponding paper.
```
@inproceedings{
  koch26buildyn,
  title={BuilDyn: Excitation-Driven Data Generation for Building Thermal Dynamics Modeling and Control},
  author={Koch, Felix and Krug, Thomas and Raisch, Fabian and Schäfer, Benjamin and Tischler, Benjamin},
  booktitle={Proceedings of the 17th ACM International Conference on Future and Sustainable Energy Systems}
  year={2026}
}
```

