#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
"""Larger string constants for CalcOPP-GUI.

CalcOPP – Calculation of Effective One-Particle Potentials
CalcOPP-GUI – The Graphical User Interface of CalcOPP

This module declares larger strings constants (explanations, annotations, etc.)
that are used for documentation purposes in CalcOPP-GUI.
"""

__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2019, Dr. Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.0'
__maintainer__ = 'Dennis Wiedemann'
__email__ = 'dennis.wiedemann@chem.tu-berlin.de'
__status__ = 'Production'


CITATION = 'D. Wiedemann, CalcOPP, Calculation of One-Particle Potentials, Technische \n' \
           'Universität Berlin, Berlin (Germany), 2019, doi:10.5281/zenodo.2530346.'

LICENSE = 'CalcOPP is distributed under the %s license (see LICENSE file). It uses the modules\n' \
          'PySimpleGUI by MikeTheWatchGuy distributed under the GNU General Public License\n' \
          'v3.0 (see LGPL-3.0.txt) and NumPy by the NumPy developers distributed under the BSD\n' \
          'License 2.0 (see BSD-2.0.txt).\n' % __license__

INTRODUCTION = 'Choose the source-data type by selecting a tab on the right. “2D PDF” and “3D PDF” can be generated ' \
               'after refinement with JANA2006, “Scatterer Density” is the result of MEM reconstruction with ' \
               'Dysnomia.\n' \
               '\n' \
               'HERE BE DRAGONS: This is not a black-box tool. Know what you are doing and how to assess the ' \
               'sensibleness of your results! If you do not, this might be a good open-access read to start: ' \
               'D. Wiedemann et al., Z. Phys. Chem. 2017, 231, 1279–1302; doi:10.1515/zpch-2016-0918.\n' \
               '\n'

ERROR_INTRO = 'An error occurred in the subroutine %s.\n\nIf your input files are valid, please report this error to ' \
              'the developer including a screenshot and the input file(s).\n\nCalcOPP Version: %s\n\n' % \
              ('%s', __version__)

ENDING = '\n' \
         'Any file with the same name as the selected output file will be overwritten! Be sure to save intermediate ' \
         'results that you are going to need.'

PDF2D = 'Prerequisites\n—————————————\n' \
        'You know how to\n' \
        '• properly refine a structure with anharmonic displacement\n' \
        '  parameters,\n' \
        '• produce a j.p.d.f. map using JANA2006, and \n' \
        '• handle the Monte-Carlo error-map generation in JANA2006.\n' \
        '\n' \
        'Input Preparation\n—————————————————\n' \
        '• In JANA2006, use the Contour tool to generate a j.p.d.f.\n' \
        '  map of the (mobile) atoms of interest.\n' \
        '• Optionally, select “Include error map”. Typically, aim for\n' \
        '  an accuracy limit of 1% and adjust the “Number of iteration\n' \
        '  steps” as needed.\n' \
        '• Define the plane of interest. For speed, especially when\n' \
        '  including an error map, set third scope parameter to zero\n' \
        '  to generate a single plane.\n' \
        '• After calculation, select “Save”, “Save this section”, “as\n' \
        '  stf file”.\n' \
        '• If you have included an error map, click “Err on” and\n' \
        '  “Save” “[…] this section” “as stf file”.\n' \
        '• For convenience, keep the corresponding *.m90 file in the\n' \
        '  same directory as the output file.\n' \
        '\n' \
        'Options\n———————\n' \
        'Via radio button, you can choose if CalcOPP shall read the temperature from the *.m90 file or use a ' \
        'user-provided custom value. The checkboxes define which data columns are written in the output file; PDF ' \
        'and OPP uncertainties require an input error map.\n' \
        '\n' \
        'Output\n——————\n' \
        'The output is an ASCII file of space-separated x, y, PDF, and OPP values (the latter two with ' \
        'uncertainties, if supplied) for each grid point. You can plot it with several applications (e.g., gnuplot, ' \
        'QtiPlot, Origin, or Igor Pro).\n' \
        '\n' \
        'Caveats\n———————\n' \
        'For grid points with a non-positive PDF or lower PDF uncertainty limit, an arbitrarily huge OPP and OPP ' \
        'uncertainty of 10^6  eV is set. Nevertheless, this physically means a potential barrier of insurmountable ' \
        'height.\n'

PDF3D = 'Prerequisites\n—————————————\n' \
        'You know how to\n' \
        '• properly refine a structure with anharmonic displacement\n' \
        '  parameters and\n' \
        '• produce a j.p.d.f. map using JANA2006.\n' \
        '\n' \
        'Input Preparation\n—————————————————\n' \
        '• In JANA2006, use the Contour tool to generate a j.p.d.f.\n' \
        '  map of the (mobile) atoms of interest.\n' \
        '• Define the volume element of interest, possibly an\n' \
        '  orthogonalized unit cell.\n' \
        '• After calculation, select “Run 3d maps”.\n' \
        '• Without closing the visualization program (possibly VESTA),\n' \
        '  copy the *_tmp.xsf file to another directory.\n' \
        '• For convenience, copy the corresponding *.m90 file to the\n' \
        '  same directory.\n' \
        '\n' \
        'Options\n———————\n' \
        'Via radio button, you can choose if CalcOPP shall read the temperature from the *.m90 file or use a ' \
        'user-provided custom value.\n' \
        '\n' \
        'Output\n——————\n' \
        'The output is an *_opp.xsf file. All lines before and after the first 3D data grid are copied into it ' \
        'from the input verbatim. In addition, the file *_opp.vesta, which can be used to open the volumetric data ' \
        'in VESTA, is provided. Both files must be in the same directory for this to work.\n' \
        '\n' \
        'In VESTA, you should switch off the displaying of sections, as the high OPP in most of the unit cell ' \
        'would obscure any area of interest. Choose the isosurface level (given in electronvolt) reasonably.\n' \
        '\n' \
        'Caveats\n———————\n' \
        'For grid points with a non-positive PDF, the highest finite OPP in the data (derived from the lowest ' \
        'positive PDF) is set to make the fringes of visualized isosurfaces less spiky after treatment with VESTA’s ' \
        'interpolation algorithm. If you further process the data or extract values directly, be aware that the ' \
        'potential barrier is insurmountably (infinitely) high at these points.\n'

SD = 'Prerequisites\n—————————————\n' \
     'You know how to\n' \
     '• reconstruct scattering-length or electron densities via\n' \
     '  maximum-entropy methods (MEM) using Dysnomia and\n' \
     '• assess the results.\n' \
     '\n' \
     'Input Preparation\n—————————————————\n' \
     'Dysnomia writes the necessary *.pgrid file as output.\n' \
     '\n' \
     'Options\n———————\n' \
     'Via radio button, you can choose the source of extremal density (i.e., the highest absolute density) for the ' \
     'mobile atom under scrutiny. The choice depends on the problem at hand:\n' \
     '• Select “Negative minimum” if you are dealing with neutron\n' \
     '  diffraction and the atom is the only crystallographically\n' \
     '  unique negative scatterer (e.g., a single Li or H).\n' \
     '• Select “Positive maximum” if you are dealing with neutron\n' \
     '  diffraction and the atom is the only crystallographically\n' \
     '  unique positive scatterer.\n' \
     '• Select “Custom value” for X-ray diffraction and all other\n' \
     '  cases. You must provide a sensible extremal value from the\n' \
     '  area accessible to the atom (i.e., around the migration\n' \
     '  path). For electron densities from X-ray diffraction,\n' \
     '  you must also consider deformation due to bonding, lone\n' \
     '  pairs, etc.\n' \
     '\n' \
     'Output\n——————\n' \
     'The output is a binary *_opp.pgrid file. Additionally, an *_opp.vesta file is provided to easily open the ' \
     'volumetric data in VESTA. You should switch off the displaying of sections, as the high OPP in most of the ' \
     'unit cell would obscure any area of interest. Choose the isosurface level (given in electronvolt) reasonably.\n' \
     '\n' \
     'Caveat\n——————\n' \
     'For grid points with a non-positive PDF, the highest finite OPP in the data (derived from the lowest positive ' \
     'PDF) is set to make the fringes of visualized isosurfaces less spiky after treatment with VESTA’s ' \
     'interpolation algorithm. If you further process the data or extract values directly, be aware that the ' \
     'potential barrier is insurmountably (infinitely) high at these points.\n'

MANUAL_PDF2D = INTRODUCTION + PDF2D + ENDING
MANUAL_PDF3D = INTRODUCTION + PDF3D + ENDING
MANUAL_SD = INTRODUCTION + SD + ENDING
