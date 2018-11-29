#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
"""A program for the calculation of one-particle potentials (OPPs) from scatterer densities.

CalcOPP – Calculation of One-Particle Potentials
SD2OPP – Subroutines for Calculation from Scatterer-Density Data (Dysnomia PGRID Format)

This program calculates three-dimensional OPPs from electron or scattering-length densities reconstructed via
 maximum-entropy methods (MEM) as put out by the program Dysnomia.

SD2OPP uses the module NumPy by the NumPy developers distributed under the BSD License 2.0 (see BSD-2.0.txt).
"""

__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2019, Dr. Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.0'
__maintainer__ = 'Dennis Wiedemann'
__email__ = 'dennis.wiedemann@chem.tu-berlin.de'
__status__ = 'Development'

import argparse
import os
import numpy as np


def non_zero_float(string):
    """Type definition for non-zero floats in argparse.

    :param string: string to check for convertibility
    :return float: converted non-zero float
    """
    try:
        value = float(string)
    except ValueError:
        raise argparse.ArgumentTypeError('"%s" is not a decimal.' % string)
    if value == 0.:
        raise argparse.ArgumentTypeError('Argument is zero.')
    return value


def pos_float(string):
    """Type definition for positive floats in argparse.

    :param string: string to check for convertibility
    :return float: converted positive float
    """
    try:
        value = float(string)
    except ValueError:
        raise argparse.ArgumentTypeError('"%s" is not a decimal.' % string)
    if value <= 0.:
        message = '"%r" is not positive.' % value
        raise argparse.ArgumentTypeError(message)
    return value


def parse_arguments():
    """Parses and checks the command-line arguments.

    :return argparse.namespace: object holding the command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Calculate 3D OPP from MEM-reconstructed electron/scattering-length density',
        epilog='SD2OPP uses the module NumPy by the NumPy developers distributed under the BSD License 2.0'
               '(see BSD-2.0.txt).')
    parser.add_argument('input', type=argparse.FileType('rb'), help='specifies the PGRID input file')
    parser.add_argument('output', type=argparse.FileType('wb'), help='specifies the PGRID output file')
    parser.add_argument('temperature', type=pos_float, help='specifies the temperature in K')
    extremum_group = parser.add_mutually_exclusive_group(required=True)
    extremum_group.add_argument('-min', '--minimum', action='store_true',
                                help='set extremal value to minimal negative input density')
    extremum_group.add_argument('-max', '--maximum', action='store_true',
                                help='set extremal value to maximal positive input density')
    extremum_group.add_argument('-ext', '--extremum', type=non_zero_float, help='set a custom extremal value '
                                                                                'in (fm) Å\u207B³')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    return parser.parse_args()


def hello():
    """Prints greeting text.

    :return: none
    """
    print('SD2OPP %s - Calculation of 3D OPP from Scatterer Density (Dysnomia PGRID Format)' % __version__)
    print('%s (%s License, see LICENSE file)' % (__copyright__, __license__))


def calculate_opp(input_file, output_file, temp, source, extr=None):
    print(hello())
    print(input_file, output_file, temp, source, extr)
    # input_header, input_data = read_pgrid(file_name)
    # extr = find_minimum(input_file)
    # extr = find_maximum(input_file)
    # output_header = set_title(input_header, new_title)
    # output_data = opp(input_data, temperature, extremum)
    # write_pgrid(output_header, output_data)
    # transform_vesta(output_filename, new_title)
    # goodbye()
    """
    with open('./test/Li2Ti3O7_600C.pgrid', 'rb') as input_file:
        input_header = input_file.read(152)
        input_data = np.fromfile(input_file, dtype=np.float32)

    # TODO: chose min/max/custom
    extremum = min(input_data)
    output_data = np.log10(input_data)

    print(input_header)

    with open('./test/outtest.txt', 'w') as out:
        out.write(str(input_data[0:]))

    print(extremum)
    print(np.count_nonzero(np.isnan(input_data)))
    print(input_data[1:])
    print(output_data[1:])
    print(np.argwhere(np.isnan(input_data)))
    """
    # TODO: print maximum/minimum with fractional position ("e.g., at ca." for extracted values)


# ===== Main Routine for Running as Standalone Program ===== #
if __name__ == '__main__':

    cmd_args = parse_arguments()

    # ----- Set Parameters for Extremum Choice ----- #
    if cmd_args.minimum:
        extr_source = 'min'
        extremum = None
    elif cmd_args.maximum:
        extr_source = 'max'
        extremum = None
    else:
        extr_source = 'custom'
        extremum = cmd_args.extremum

    # ----- Call Actual Calculation ----- #
    calculate_opp(cmd_args.input, cmd_args.output, cmd_args.temperature, extr_source, extremum)
