# CalcOPP
A Program for the Calculation of Effective One-Particle Potentials (OPPs)

<img src="https://img.shields.io/github/release/dewiedem/calcopp/all.svg" alt="GitHub Release" data-external="1" /> <img src="https://img.shields.io/github/release-date/dewiedem/calcopp.svg" alt="GitHub Release Date" data-external="1" /> [<img src="https://img.shields.io/github/license/dewiedem/calcopp.svg" alt="GitHub License" data-external="1" />](./LICENSE) [![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.2530345-blue.svg)](https://doi.org/10.5281/zenodo.2530345)

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
### Purpose
In the OPP approach, every atom is treated as an individual Einstein oscillator subject to Boltzmann statistics in the classical limit. The effective OPP itself represents the potential as experienced by an atom at a certain position and allows, *e.g.*, to assess the viability and activation barriers of migration pathways (see [K. N. Trueblood *et al.*, *Acta Crystallogr., Sect. A: Found. Crystallogr.* **1996**, *52*, 770–781](https://doi.org/10.1107/S0108767396005697)).

The OPP *V*(***u***) experienced by an atom displaced from its reference position by a vector ***u*** can be calculated from any probability-density function (PDF) *p*(***u***) adequately describing it (*cf.* [H. Boysen, *Z. Kristallogr.* **2003**, *218*, 123–131](https://doi.org/10.1524/zkri.218.2.123.20668)): 

![Equation 1](./images/equation_1.svg)

Depending on the problem, CalcOPP allows to calculate the effective OPP from a PDF sampled in 2D or 3D by [JANA2006](http://jana.fzu.cz/) or from the MEM-reconstructed scatterer density sampled using [Dysnomia](https://jp-minerals.org/dysnomia/en/)—under certain additional conditions. It can also reformat 2D PDF input and handle the associated error maps.

### Calculation from Scatterer Density 
A PDF has to be non-negative, Lebesgue-integrable, and normalized to an integral of unity over the whole space.

Although it is far from mathematically rigorous, the following rationale suggests that a ratio of scattering-length or electron densities within carefully chosen limits has the properties of a probability-density ratio:
- *Adequacy:* If the negative/positive scattering-length density is solely generated by the unique atom under scrutiny, the former is an adequate measure for the distribution of the latter. In all other cases (another static negative/positive scatterer, investigation of electron density, *etc.*), it is adequate if the scope is limited to areas accessible for the atom (*i.e.*, the environment of the migration pathways).
- *Non-Negativity:* Only non-negative ratios, in which both probability density values are either negative or positive, are taken into account.
- *Integrability:* Scattering-length and electron densities are Lebesgue-integrable.
- *Normalization:* For ratios of probability density values, normalization is unnecessary (the normalizing constant cancels).

### Uncertainty Estimation
CalcOPP can estimate the OPP uncertainty if a suitable PDF error map (as calculated by JANA2006 using a Monte-Carlo method) is provided. Unfortunately, there some problems prohibit the use of common progression approaches:
1. In areas of high probability density (*e.g.*, the atomic positions), correlations between uncertainties of maximal and local probability density occur, leading to an overestimation of OPP uncertainty.
2. In areas of low probability density (*e.g.*, the bottleneck positions), the uncertainties often may be far too high to warrant a treatment *via* Taylor series, let alone linear approximation.
3. The value distributions depend on the problem but are, in general, neither normal nor log-normal.
4. The range of uncertainty for the PDF is supposed to be symmetric around the central value, while the one for the (logarithmic) OPP is asymmetric.

As CalcOPP is unaware of the covariance of maximal and local probability density, it cannot overcome the first problem; keep this in mind if you evaluate the OPP near its minima. To cope with the other problems, CalcOPP does not propagate uncertainties but calculates the OPP differences Δ<sub>±</sub>*V*(***u***) from the upper and lower PDF uncertainty limits:

![Equation 2](./images/equation_2.svg)

## Compiling
### Modules *calcopp-gui* and *sd2opp*
The source code adheres to the specifications of Python 3.7 and heeds [*PEP 8 – Style Guide for Python Code*](https://www.python.org/dev/peps/pep-0008/). It has been compiled against Python X.X.X/X.X.X (Windows/Linux) and frozen using [PyInstaller](https://www.pyinstaller.org/) X.X.X with assert statements and any code conditional on the value of `__debug__` removed. The modules *calcopp-gui* and *sd2opp* were frozen including [PySimpleGUI](https://pypi.org/project/PySimpleGUI/) X.X.X and [NumPy](https://www.numpy.org/) X.X.X, respectively.

Options are detailed in the build scripts `build.cmd` (Windows) and `build.sh` (Linux) shipped with the source code.

### Modules *pdf2opp_2d* and *pdf2opp_3d*
The source code adheres the specifications of Fortran 2008 with GNU-specific extensions. It has been compiled using GFortran X.X.X/X.X.X (Windows/Linux) with static linking, all symbol table and relocation information removed, and optimization level set to “O3”.

Options are detailed in the build scripts `build.cmd` (Windows) and `build.sh` (Linux) shipped with the source code.

## Installation
- On Windows versions earlier than Windows 10, install the [Visual C++ Redistributable für Visual Studio 2015](https://www.microsoft.com/en-US/download/details.aspx?id=48145) with the same bitness as CalcOPP if necessary.
- Unpack one of the archives (64-/32-bit version for Windows/Linux) into any user-writable directory. For the graphical user interface (GUI) to work correctly, the executables must be in a common directory.
- On Unix-like systems, it may be necessary to set execute permissions for the executables `CalcOPP`, `pdf2opp_2d`, `pdf2opp_3d`, and `sd2opp`.

## Usage
### GUI
Start the application `CalcOPP[.exe]` *via* desktop environment or shell. Further instructions are displayed in the box on the left. 

### Drag and Drop
For `pdf2opp_2d[.exe]`, you can drag and drop the icon of an appropriate `*.stf` file on the executable’s icon. It will then try to read the measurement temperature from a JANA2006 `*.m90` file in the working directory and, if the file is found, automatically write the output to `*_opp.asc`. If an error map with the name `*_err.stf` is also present, it will be processed, too.

For `pdf2opp_3d[.exe]`, you can drag and drop the icon of an appropriate `*_tmp.xsf` file on the executable’s icon. It will then try to read the measurement temperature from a JANA2006 `*.m90` file in the working directory and, if the file is found, automatically write the output to `*_opp.xsf` and `*_opp.vesta`.

### Command Line
If you want to use `pdf2opp_2d[.exe]`, `pdf2opp_3d[.exe]`, or `sd2opp[.exe]` from the command line (*e.g.*, in custom scripts), please invoke them with the parameter `-h` (for help) to display their usage. The former two are stand-alone executables.

## Acknowledgement
CalcOPP has been inspired by work from Dr. Hans Boysen (Ludwig-Maximilians-Universität München) and Dr. Anatoliy Senyshyn (Technische Universität München).

## Citation
If you prepare data for publication with CalcOPP, please use the following citation:

D. Wiedemann, CalcOPP, Calculation of Effective One-Particle Potentials, Technische Universität Berlin, Berlin (Germany), **2019**, [doi:10.5281/zenodo.2530345](https://doi.org/10.5281/zenodo.2530345).

## Contributing
It is much appreciated if you report any bugs, typos, or suggestions for improvement to [dennis.wiedemann@chem.tu-berlin.de](mailto:dennis.wiedemann@chem.tu-berlin.de).
