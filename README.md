# CalcOPP
A suite for the calculation of one-particle potentials (OPPs)

## Author and Maintainer
Dr. Dennis Wiedemann
Technische Universität Berlin
Institut für Chemie, Sekr. C 2
Straße des 17. Juni 135
10623 Berlin, Germany

Phone:	+49 30 314-26178
Fax:	+49 30 314-79656
E-mail:	[dennis.wiedemann@chem.tu-berlin.de](mailto:dennis.wiedemann@chem.tu-berlin.de)
Web:	http://dennis.wiedemann.name

## Purpose and Scope
In the OPP approach, every atom is treated as an individual Einstein oscillator subject to Boltzmann statistics in the classical limit. The OPP itself represents the potential as experienced by an atom at a certain position and allows, *e.g.*, to assess the viability and activation barriers of migration pathways (see [K. N. Trueblood, H.-B. Bürgi, H. Burzlaff, J. D. Dunitz, C. M. Gramaccioli, H. H. Schulz, U. Shmueli, S. C. Abrahams, *Acta Crystallogr., Sect. A: Found. Crystallogr.* **1996**, *52*, 770–781](https://doi.org/10.1107/S0108767396005697) and [H. Boysen, *Z. Kristallogr.* **2003**, *218*, 123–131](https://doi.org/10.1524/zkri.218.2.123.20668)).

Depending on the problem, CalcOPP allows to calculate the OPP from a probability-density function (PDF) sampled in 2D or 3D by JANA2006 or from the MEM-reconstructed scatterer density sampled using Dysnomia—under certain additional conditions. It can also reformat 2D PDF input and handle error maps.

## Compiling
The source code adheres strictly to the specifications of Fortran2003. It has been compiled using GFortran from GCC 6.4.0 (Windows) and GCC 6.3.0 (Linux) with static linking, all symbol table and relocation information removed, and optimization level set to “O3”:

`gfortran -std=f2003 -pedantic -Wall -Wextra -O3 -static -s -m64 CalcOPP[-D].f03 -o CalcOPP[-3D].exe`

## Acknowledgement
CalcOPP has been inspired by work from Dr. Hans Boysen (Ludwig-Maximilians-Universität München).

## Citation
If you prepare data for publication with CalcOPP, please use one of the following citations:

- D. Wiedemann, CalcOPP, Calculation of 2D OPP from PDF Data, Technische Universität Berlin, Berlin (Germany), 2015, [doi:10.6084/m9.figshare.1461721](https://doi.org/10.6084/m9.figshare.1461721).
- D. Wiedemann, CalcOPP-3D, Calculation of 3D OPP from PDF Data, Technische Universität Berlin, Berlin (Germany), 2018, [doi:10.6084/m9.figshare.5798130](https://doi.org/10.6084/m9.figshare.5798130).

## Contributing
I am not looking for contributions at the moment, but feel free to contact me!