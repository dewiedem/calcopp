# CalcOPP
A Suite for the Calculation of One-Particle Potentials (OPPs)

![GitHub Release](https://img.shields.io/github/release/dewiedem/calcopp.svg)
![GitHub Release Date](https://img.shields.io/github/release-date/dewiedem/calcopp.svg)
![GitHub License](https://img.shields.io/github/license/dewiedem/calcopp.svg)

## Author and Maintainer
Dr. Dennis Wiedemann\
Technische Universität Berlin\
Institut für Chemie, Sekr. C 2\
Straße des 17. Juni 135\
10623 Berlin, Germany

Phone:	+49 30 314-26178\
Fax:	+49 30 314-79656\
E-mail:	[dennis.wiedemann@chem.tu-berlin.de](mailto:dennis.wiedemann@chem.tu-berlin.de)\
Web:	http://dennis.wiedemann.name

## Description
In the OPP approach, every atom is treated as an individual Einstein oscillator subject to Boltzmann statistics in the classical limit. The OPP itself represents the potential as experienced by an atom at a certain position and allows, *e.g.*, to assess the viability and activation barriers of migration pathways (see [K. N. Trueblood *et al.*, *Acta Crystallogr., Sect. A: Found. Crystallogr.* **1996**, *52*, 770–781](https://doi.org/10.1107/S0108767396005697) and [H. Boysen, *Z. Kristallogr.* **2003**, *218*, 123–131](https://doi.org/10.1524/zkri.218.2.123.20668)).

Depending on the problem, CalcOPP allows to calculate the OPP from a probability-density function (PDF) sampled in 2D or 3D by [JANA2006](http://jana.fzu.cz/) or from the MEM-reconstructed scatterer density sampled using [Dysnomia](https://jp-minerals.org/dysnomia/en/)—under certain additional conditions. It can also reformat 2D PDF input and handle the associated error maps.

## Compiling
### Modules *calcopp-gui* and *sd2opp*
The source code adheres to the specifications of Python 3.7 and heeds [*PEP 8 – Style Guide for Python Code*](https://www.python.org/dev/peps/pep-0008/). It has been compiled using Python X.X.X/X.X.X (Windows/Linux) and [PyInstaller](https://www.pyinstaller.org/) X.X.X with assert statements, any code conditional on the value of `__debug__`, and docstrings removed.

```
python -OO -m PyInstaller --name="CalcOPP[.exe]" calcopp-gui.py
python -OO -m PyInstaller --name="sd2opp[.exe]" sd2opp.py
```

The module *calcopp-gui* further relies on [PySimpleGUI](https://pypi.org/project/PySimpleGUI/), used in version X.X.X for compiling.

### Modules *pdf2opp_2d* and *pdf2opp_3d*
The source code adheres strictly to the specifications of Fortran2008. It has been compiled using GFortran from GCC X.X.X/X.X.X (Windows/Linux) with static linking, all symbol table and relocation information removed, and optimization level set to “O3”:

```
gfortran -std=f2008 -pedantic -Wall -Wextra -O3 -static -s [-m64] pdf2opp_2d.f08 -o pdf2opp_2d[.exe]
gfortran -std=f2008 -pedantic -Wall -Wextra -O3 -static -s [-m64] pdf2opp_3d.f08 -o pdf2opp_3d[.exe]
```

## Installation
Unpack one of the archives (64-/32-bit version for Windows/Linux) into any user-writable directory. For the graphical user interface (GUI) to work correctly, the executables must be in a common directory. You can also use the executables `pdf2opp_2d[.exe]`, `pdf2opp_3d[.exe]`, and `sd2opp[.exe]` in a stand-alone (scriptable) fashion. It may be necessary to set the execute permission on Unix-like systems.

## Usage
### GUI
Start the application `CalcOPP[.exe]` *via* desktop environment or shell. Further instructions are displayed in the box on the left. 

### Drag and Drop
For `pdf2opp_2d[.exe]`, you can drag and drop the icon of an appropriate `*.stf` file on the icon of the executable. The latter will then try to read the measurement temperature from a JANA2006 `*.m90` file in the working directory and, if the file is found, automatically write the output to `*_opp.asc`. If an error map with the name `*_err.stf` is also present, it will be processed, too.

For `pdf2opp_3d[.exe]`, you can drag and drop the icon of an appropriate `*_tmp.xsf` file on the icon of the executable. The latter will then try to read the measurement temperature from a JANA2006 `*.m90` file in the working directory and, if the file is found, automatically write the output to `*_opp.xsf` and `*_opp.vesta`.

### Command Line
If you want to use the executables `pdf2opp_2d[.exe]`, `pdf2opp_3d[.exe]`, or `sd2opp[.exe]` from the command line, please invoke them with the parameter `-h` (for help) to display their usage.

## Acknowledgement
CalcOPP has been inspired by work from Dr. Hans Boysen (Ludwig-Maximilians-Universität München) and Dr. Anatoliy Senyshyn (Technische Universität München).

## Citation
If you prepare data for publication with CalcOPP, please use the following citation:

D. Wiedemann, CalcOPP, Calculation of One-Particle Potentials, Technische Universität Berlin, Berlin (Germany), **2019**, [doi:XXX](https://doi.org/XXX).

## Contributing
I am not looking for contributors at the moment, but feel free to contact me for bug reports and discussion.
