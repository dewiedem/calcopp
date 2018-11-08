#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
"""Larger string constants for CalcOPP-GUI.

CalcOPP – Calculation of One-Particle Potentials
CalcOPP-GUI – The Graphical User Interface of CalcOPP

This module declares larger strings constants (explanations, annotations, etc.)
that are used for documentation purposes in CalcOPP-GUI.
"""

__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2019, Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.0'
__maintainer__ = 'Dennis Wiedemann'
__email__ = 'dennis.wiedemann@chem.tu-berlin.de'
__status__ = 'Development'


CITATION = 'D. Wiedemann, CalcOPP, Calculation of One-Particle Potentials, Technische\n' \
           'Universität Berlin, Berlin (Germany), 2019, doi:XXX.'

INTRODUCTION = 'Please chose the kind of source data for OPP calculation by selecting the corresponding tab on the ' \
               'right. “2D PDF” and “3D PDF” data can be generated after refinement with JANA2006, “Scatterer ' \
               'Density” data is the result of MEM reconstruction with Dysnomia.\n\n' \
               'HERE BE DRAGONS: This is neither a black- nor an out-of-the-box tool. You have to know what you are ' \
               'doing and how to assess the sensibleness of your results. If you do not, this might be a good ' \
               'open-access read to start: D. Wiedemann et al., Z. Phys. Chem. 2017, ' \
               '231, 1279–1302; doi:10.1515/zpch-2016-0918.\n\n'

MANUAL_PDF2D = INTRODUCTION + \
               'PDF2D: How to prepare input from JANA2006 and optional error files (anharmonic) and what to do with ' \
               'the output (plot in gnuplot, QtiPlot, Origin, Igor Pro, etc.). Options to the right. Check output of ' \
               'old CalcOPP.'

MANUAL_PDF3D = INTRODUCTION + \
               'PDF3D: How to prepare input from JANA2006 (anharmonic) and what to do with the output (visualize ' \
               'with VESTA). Options to the right. Check output of old CalcOPP-3D.'

MANUAL_SD = INTRODUCTION + \
            'SD: How to prepare input from Dysnomia and what to do with the output (visualize with VESTA).\n\n' \
            '•  MEM-filtered\n' \
            '•  Minimum for Li, H (or even Ti or Mn) diffusion from neutron data if only one negative scatterer is ' \
            ' present\n' \
            '•  Maximum for all other atoms from neutron data if only one positive scatterer is present\n' \
            '•  Custom value (manually evaluated extremum in sensible, accessible area) for X-ray diffraction or ' \
            'other cases'
