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

import argparse as ap
import sys
import numpy as np


def non_zero_float(string):
    """Define non-zero floats for `argparse`.

    :param string: string to check for convertibility
    :type string: str
    :return: converted non-zero float
    :rtype: float
    """
    try:
        value = float(string)
    except ValueError:
        raise ap.ArgumentTypeError('"%s" is not a decimal.' % string)
    if value == 0.:
        raise ap.ArgumentTypeError('Argument is zero.')
    return value


def pos_float(string):
    """Define positive floats for `argparse`.

    :param string: string to check for convertibility
    :type string: str
    :return: converted positive float
    :rtype: float
    """
    try:
        value = float(string)
    except ValueError:
        raise ap.ArgumentTypeError('"%s" is not a decimal.' % string)
    if value <= 0.:
        message = '"%r" is not positive.' % value
        raise ap.ArgumentTypeError(message)
    return value


def parse_arguments():
    """Parse and check the command-line arguments.

    :return: object holding the command-line arguments
    :rtype: argparse.namespace
    """
    parser = ap.ArgumentParser(
        description='Calculate 3D OPP from MEM-reconstructed electron/scattering-length density',
        epilog='SD2OPP uses the module NumPy by the NumPy developers distributed under the BSD License 2.0'
               '(see BSD-2.0.txt).')
    parser.add_argument('input', type=ap.FileType('rb'), help='specifies the PGRID input file')
    parser.add_argument('output', type=ap.FileType('wb'), help='specifies the PGRID output file')
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
    """Print greeting text."""
    print('SD2OPP %s - Calculation of 3D OPP from Scatterer Density (Dysnomia PGRID Format)' % __version__)
    print('%s (%s License, see LICENSE file)\n' % (__copyright__, __license__))


def read_grid(file):
    u"""Read the binary input grid-file depending on its header.

    :param file: path and name of the input file
    :type file: str
    :return: dictionary of header values, 1D array of data points  # TODO: check if these are lists or numpy.ndarry
             - ``'version'``: quadripartite version number of input file (`list`[`int`*4]).
             - ``'title'``: title of the data set (`str`). Maximum of 79 characters.
             - ``'gtype'``: grid type (`int`). `0` for general grid (*.ggrid), `1` for periodic grid (*.pgrid).
             - ``'ftype'``: file type (`int`). `0` for raw data (values only), `1` for records with index and value(s).
             - ``'nval'``: number of values per record (`int`). `1` for records with either positive or negative data,
                           `2` for records with both positive and negative value.
             - ``'ndim'``: Dimension of unit cell (`int`). Has to be `3` currently.
             - ``'ngrid'``: Number of voxels/records along principal axes (`list`[`int`*3]).
             - ``'nasym'``: Total number of records/voxels (`int`).
             - ``'cell'``: Unit cell parameters (`list`[`int`*6]). Order: a/Å, b/Å, c/Å, α/°, β/°, γ/°.
             - ``'npos'``: Number of considered equivalent positions/symmetry operators (`int`).
             - ``'ncen'``: Indicator for consideration of centrosymmetry (`int`). `0` for non-centrosymmetric data,
                           `1` for centrosymmetric data.
             - ``'nsub'``: Number of considered lattice centering operations (`int`).
             - ``'symop'``: Symmetry operators as 3 × 4 matrices (`list`[`list`(`int`*12)]). Each a rotation matrix
                            followed by a translation vector.
             - ``'subposp'``: Centering vector (`list`[`int`*3]).
    :rtype: tuple[dict(str, int, float, list[float], list[int]), numpy.ndarray(numpy.float32)]
    """
    with open(file, 'rb') as read_file:
        header = {'version': np.fromfile(read_file, dtype=np.dtype('4i4'), count=1)[0]}
        if (header['version'] != [3, 0, 0, 0]).any():
            print('Input file version not supported.\nTrying to read anyway ... ', end='', flush=True)
        title_raw = read_file.read(80)
        header['title'] = title_raw[:title_raw.find(b'\x00')].decode(encoding='utf-8', errors='replace')
        header['gtype'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
        header['ftype'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
        if header['ftype'] not in [0, 1]:
            print('Failed.')
            sys.exit('File record type not supported.')
        header['nval'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
        if header['nval'] not in [1, 2]:
            print('Failed.')
            sys.exit('Unable to handle number of values per voxel.')
        header['ndim'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
        if header['ndim'] != 3:
            print('Failed.')
            sys.exit('Unit cell must be three-dimensional in this version.')
        header['ngrid'] = np.fromfile(read_file, dtype=np.dtype('3i4'), count=1)[0]
        header['nasym'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
        header['cell'] = np.fromfile(read_file, dtype=np.dtype('6f4'), count=1)[0]
        if header['ftype'] == 1:
            header['npos'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
            header['ncen'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
            header['nsub'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
            header['symop'] = np.fromfile(read_file, dtype=np.dtype('12i4'), count=header['npos'])
            header['subposp'] = np.fromfile(read_file, dtype=np.dtype('3i4'), count=1)[0]
            data = np.fromfile(read_file, dtype=np.dtype('i4'+', f4'*header['nval']))
        else:
            header['npos'] = None
            header['ncen'] = None
            header['nsub'] = None
            header['symop'] = None
            header['subposp'] = None
            data = np.fromfile(read_file, dtype=np.float32)
        if len(data) != header['nasym']:
            print('Number of found records differs from statement in header.\nContinuing with found data ...')

        print(header)
        # print(np.count_nonzero(np.isnan(data)))
        print(data[1:])
        # print(np.argwhere(np.isnan(data)))
    return header, data  # TODO: separate data and indices, calculate one data point per voxel


def calc_opp(input_file, output_file, temp, source, extr=None):
    """Start main routine for calculating the OPP from scatterer density.

    :param input_file:  path and name of the input file
    :type input_file: str
    :param output_file:  path and name of the output file
    :type output_file: str
    :param temp: temperature in Kelvin
    :type temp: float
    :param source: identifier for the source of the extremal value ('min': negative minimum, 'max': positive maximum,
                   'custom': user-provided value in parameter extr)
    :type source: str
    :param extr: user-provided extremal value
    :type extr: float
    """
    hello()
    print('Opening input file and reading data ... ', end='', flush=True)
    input_header, input_data = read_grid(input_file)
    print('Done.')

    # extr = find_extremum(input_data)
    # extr = find_extremum(input_data)
    # output_header = set_title(input_header, new_title)
    # output_data = opp(input_data, temperature, extremum)
    # write_grid(output_header, output_data)
    # transform_vesta(output_filename, new_title)
    # goodbye()

    # TODO: print maximum/minimum with fractional position ("e.g., at ca." for extracted values)


# ===== Routine for Running as Standalone Program ===== #
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
    calc_opp(cmd_args.input.name, cmd_args.output.name, cmd_args.temperature, extr_source, extremum)
