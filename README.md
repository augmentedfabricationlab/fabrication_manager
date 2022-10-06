# Fabrication Manager


## Requirements 
* [Rhinoceros 3D 7.0](https://www.rhino3d.com/): Update Rhino to the newest version

**Quick links:** [compas docs](https://compas-dev.github.io/main/) | [compas_fab docs](https://gramaziokohler.github.io/compas_fab/latest/)

* [Rhinoceros 3D 7.0](https://www.rhino3d.com/)
* [Anaconda Python Distribution](https://www.anaconda.com/download/): 3.x
* Git: [official command-line client](https://git-scm.com/) or visual GUI (e.g. [Github Desktop](https://desktop.github.com/) or [SourceTree](https://www.sourcetreeapp.com/))
* [VS Code](https://code.visualstudio.com/) with the following `Extensions`:
  * `Python` (official extension)
  * `EditorConfig for VS Code` (optional)
  * `Docker` (official extension, optional)

## Set-up and Installation

For the installation of the fabrication_manager repository you are required to have a virtual environment compatible with Compas, a guide to set this up can be found at [LE-AR-N](https://github.com/le-ar-n/le-ar-n)

### 1. Fabrication Manager installation
    
    (your_env) python -m pip install git+https://github.com/augmentedfabricationlab/fabrication_manager@master#egg=fabrication_manager
    (your_env) python -m compas_rhino.install -p fabrication_manager -v 7.0
