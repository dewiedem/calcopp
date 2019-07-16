#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
"""A program for the calculation of effective one-particle potentials (OPPs) from scatterer densities.

CalcOPP – Calculation of Effective One-Particle Potentials
SD2OPP – Subroutines for Calculation from Scatterer-Density Data (Dysnomia PGRID Format)

This program calculates three-dimensional OPPs from electron or scattering-length densities reconstructed via
 maximum-entropy methods (MEM) as put out by the program Dysnomia.

SD2OPP uses the module NumPy by the NumPy developers distributed under the BSD License 2.0 (see BSD-2.0.txt).
"""

__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2019, Dr. Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.1'
__maintainer__ = 'Dennis Wiedemann'
__email__ = 'dennis.wiedemann@chem.tu-berlin.de'
__status__ = 'Production'

import argparse as ap
import os
import sys
import numpy as np

K_B = 1.380649e-23 / 1.602176634e-19  # Boltzmann constant in eV/K (according to CODATA 2018)


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


def mbyte_truncate(string, byte_length, encoding='utf-8'):
    """Truncate a multi-byte encoded string to a given maximal byte size.

    :param string: string to truncate
    :type string: str
    :param byte_length: length in byte to truncate to
    :type byte_length: int
    :param encoding: encoding of the string (default: 'utf-8')
    :type encoding: str
    :return: truncated string
    :rtype: str
    """
    encoded = string.encode(encoding)[:byte_length]
    return encoded.decode(encoding, 'ignore')


def parse_arguments():
    """Parse and check the command-line arguments.

    :return: object holding the command-line arguments
    :rtype: argparse.namespace
    """
    parser = ap.ArgumentParser(
        description='Calculate 3D OPP from MEM-reconstructed electron/scattering-length density',
        epilog='SD2OPP uses the module NumPy by the NumPy developers distributed under the BSD License 2.0 '
               '(see BSD-2.0.txt).')
    parser.add_argument('input', type=ap.FileType('rb'), help='specifies the PGRID input file')
    parser.add_argument('output', type=ap.FileType('wb'), help='specifies the PGRID output file')
    parser.add_argument('temperature', type=pos_float, help='specifies the temperature in K')
    extremum_group = parser.add_mutually_exclusive_group(required=True)
    extremum_group.add_argument('-min', '--minimum', action='store_true',
                                help='set extremal value to minimal negative input density')
    extremum_group.add_argument('-max', '--maximum', action='store_true',
                                help='set extremal value to maximal positive input density')
    extremum_group.add_argument('-ext', '--extremum', type=non_zero_float, help=u'set a custom extremal value in (fm) '
                                                                                u'Å⁻³')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    return parser.parse_args()


def hello():
    """Print greeting message."""
    print('SD2OPP %s - Calculation of 3D OPP from Scatterer Density' % __version__)
    print('%s (%s License, see LICENSE file)\n' % (__copyright__, __license__))


def goodbye():
    """Print farewell message."""
    print('All calculations finished. Have a nice day!')
    print('“Don’t be scared. […] It really doesn’t help.” – The Doctor\n\n')


def read_grid(file):
    u"""Read the binary input grid-file depending on its header.

    :param file: path and name of the input file
    :type file: str
    :return: dictionary of header values, 1D array of indices, 1D array of data points
             - ``'version'``: quadripartite version number of input file
             - ``'title'``: title of the data set. Maximum of 79 characters
             - ``'gtype'``: grid type. `0` for general grid (*.ggrid), `1` for periodic grid (*.pgrid)
             - ``'ftype'``: file record type. `0` for raw data (values only), `1` for records with index and value(s)
             - ``'nval'``: number of values per record. `1` for records with either positive or negative data, `2` for
                           records with both positive and negative value
             - ``'ndim'``: dimension of unit cell. Has to be `3` currently
             - ``'ngrid'``: number of voxels/records along principal axes
             - ``'nasym'``: total number of records/voxels
             - ``'cell'``: unit cell parameters. Order: a/Å, b/Å, c/Å, α/°, β/°, γ/°
             - ``'npos'``: number of considered equivalent positions/symmetry operators
             - ``'ncen'``: indicator for consideration of centrosymmetry. `0` for non-centrosymmetric data, `1` for
                           centrosymmetric data
             - ``'nsub'``: number of considered lattice centering operations
             - ``'symop'``: symmetry operators as 3 × 4 matrices (3 × 3 rotation matrices followed by translation
                            vector)
             - ``'subposp'``: centering vector
    :rtype: tuple[
                dict(
                    - ``'version'``: numpy.ndarray[numpy.int32 * 4]
                    - ``'title'``: str
                    - ``'gtype'``: numpy.int32
                    - ``'ftype'``: numpy.int32
                    - ``'nval'``: numpy.int32
                    - ``'ndim'``: numpy.int32
                    - ``'ngrid'``: numpy.ndarray[numpy.int32 * 3]
                    - ``'nasym'``: numpy.int32
                    - ``'cell'``: numpy.ndarray[numpy.float32 * 6]
                    - ``'npos'``: numpy.int32
                    - ``'ncen'``: numpy.int32
                    - ``'nsub'``: numpy.int32
                    - ``'symop'``: numpy.ndarray[numpy.ndarray[numpy.int32 * 12]]
                    - ``'subposp'``: numpy.ndarray[numpy.int32 * 3]
                    ),
                numpy.ndarray(numpy.int32),
                numpy.ndarray(numpy.float32)
                ]
    """
    with open(file, 'rb') as read_file:

        # ----- Read and check header values ----- #
        header = {'version': np.fromfile(read_file, dtype=np.dtype('4i4'), count=1)[0]}
        if (header['version'] != [3, 0, 0, 0]).any():
            print('Input file version not supported.\nTrying to read anyway ... ', end='')
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

            # ----- Read remaining header values and data for indexed (symmetry-dependent) file ----- #
            header['npos'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
            header['ncen'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
            header['nsub'] = np.fromfile(read_file, dtype=np.int32, count=1)[0]
            header['symop'] = np.fromfile(read_file, dtype=np.dtype('12i4'), count=header['npos'])
            header['subposp'] = np.fromfile(read_file, dtype=np.dtype('3i4'), count=1)[0]

            if header['nval'] == 2:
                data_raw = np.fromfile(read_file, dtype=[('index', 'i4'), ('pos_value', 'f4'), ('neg_value', 'f4')])
                if data_raw.size != header['nasym']:
                    print('Number of found records differs from statement in header.\nContinuing with found data ...')
                indices = data_raw['index']
                data = data_raw['pos_value'] + data_raw['neg_value']
            else:
                data_raw = np.fromfile(read_file, dtype=[('index', 'i4'), ('value', 'f4')])
                if data_raw.size != header['nasym']:
                    print('Number of found records differs from statement in header.\nContinuing with found data ...')
                indices = data_raw['index']
                data = data_raw['value']

        else:

            # ----- Read remaining header values and data for raw (symmetry-independent) file ----- #
            header['npos'] = None
            header['ncen'] = None
            header['nsub'] = None
            header['symop'] = None
            header['subposp'] = None
            indices = None

            if header['nval'] == 2:
                data_raw = np.fromfile(read_file, dtype=[('pos_value', 'f4'), ('neg_value', 'f4')])
                if data_raw.size != header['nasym']:
                    print('Number of found records differs from statement in header.\nContinuing with found data ...')
                data = data_raw['pos_value'] + data_raw['neg_value']
            else:
                data = np.fromfile(read_file, dtype=np.float32)
                if data.size != header['nasym']:
                    print('Number of found records differs from statement in header.\nContinuing with found data ...')

    return header, indices, data


def write_grid(file, header, indices, data):
    u"""Write the binary output grid-file depending on its header.

    :param file: path and name of the output file
    :type file: str
    :param header: dictionary of header values
                   - ``'version'``: quadripartite version number of input file
                   - ``'title'``: title of the data set. Maximum of 79 characters
                   - ``'gtype'``: grid type. `0` for general grid (*.ggrid), `1` for periodic grid (*.pgrid)
                   - ``'ftype'``: file record type. `0` for raw data (values only), `1` for records with index and
                                  value(s)
                   - ``'ndim'``: dimension of unit cell. Has to be `3` currently
                   - ``'ngrid'``: number of voxels/records along principal axes
                   - ``'cell'``: unit cell parameters. Order: a/Å, b/Å, c/Å, α/°, β/°, γ/°
                   - ``'npos'``: number of considered equivalent positions/symmetry operators
                   - ``'ncen'``: indicator for consideration of centrosymmetry. `0` for non-centrosymmetric data, `1`
                                 for centrosymmetric data
                   - ``'nsub'``: number of considered lattice centering operations
                   - ``'symop'``: symmetry operators as 3 × 4 matrices (3 × 3 rotation matrices followed by translation
                                  vector)
                   - ``'subposp'``: centering vector
    :type header: dict(
                       - ``'version'``: numpy.ndarray[numpy.int32 * 4]
                       - ``'title'``: str
                       - ``'gtype'``: numpy.int32
                       - ``'ftype'``: numpy.int32
                       - ``'ndim'``: numpy.int32
                       - ``'ngrid'``: numpy.ndarray[numpy.int32 * 3]
                       - ``'cell'``: numpy.ndarray[numpy.float32 * 6]
                       - ``'npos'``: numpy.int32
                       - ``'ncen'``: numpy.int32
                       - ``'nsub'``: numpy.int32
                       - ``'symop'``: numpy.ndarray[numpy.ndarray[numpy.int32 * 12]]
                       - ``'subposp'``: numpy.ndarray[numpy.int32 * 3]
                       )
    :param indices: indices of the data points. Must have same size as `data`
    :type indices: numpy.ndarray(numpy.int32)
    :param data: OPP data points.
    :type data: numpy.ndarray(numpy.float32)
    """
    header['nval'] = np.int32(1)   # OPP is a single value
    header['nasym'] = np.int32(data.size)  # Set total number of data points (in case the input header was wrong)
    with open(file, 'wb') as write_file:

        # ----- Write header ----- #
        write_file.write(header['version'])
        write_file.write(header['title'].encode('utf-8').ljust(80, b'\x00'))  # Pad title field with b'\x00'
        write_file.write(header['gtype'])
        write_file.write(header['ftype'])
        write_file.write(header['nval'])
        write_file.write(header['ndim'])
        write_file.write(header['ngrid'])
        write_file.write(header['nasym'])
        write_file.write(header['cell'])

        if header['ftype'] == 1:

            # ----- Write remaining header values and data for indexed (symmetry-dependent) file ----- #
            write_file.write(header['npos'])
            write_file.write(header['ncen'])
            write_file.write(header['nsub'])
            write_file.write(header['symop'])
            write_file.write(header['subposp'])
            write_file.write(np.fromiter(zip(indices, data), dtype=[('index', indices.dtype), ('value', data.dtype)]))

        else:

            # ----- Write data for raw (symmetry-independent) file ----- #
            write_file.write(data)


def create_vesta(output_file, title, isovalue, record_type):
    """Create a *.vesta file to display grid in VESTA.

    :param output_file: path and name of the output grid-file
    :type output_file: str
    :param title: title of the grid file
    :type title: str
    :param isovalue: isosurface value to display (will be rounded)
    :type isovalue: float
    :param record_type: type of record in the grid file (`header['nval']` · `header['ftype']`)
    :type record_type: int
    """
    with open(os.path.splitext(output_file)[0] + '.vesta', 'w') as file:
        file.write('#VESTA_FORMAT_VERSION 3.3.0\n\n\n')
        file.write('CRYSTAL\n\n')
        file.write('TITLE\n%s\n\n' % title)
        file.write('IMPORT_DENSITY 1\n+1.000000 %s\n\n' % os.path.split(output_file)[1])
        file.write('STYLE\n')
        file.write('SECTS  96  0\n')
        file.write('ISURF\n')
        file.write('  1 %3d        %.2f 255 255   0 127 255\n' % (record_type, isovalue))
        file.write('  0   0   0   0\n')


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

    # ----- Read in data and display information ----- #
    print('Opening input file and reading data ... ', end='')
    header, indices, input_data = read_grid(input_file)
    print('Done.')
    print('Number of voxels: %d × %d × %d' % tuple(header['ngrid']))
    print('Unit cell dimensions: a = %f Å, b = %f Å, c = %f Å,\n   α = %f°, β = %f°, γ = %f°' % tuple(header['cell']))
    print('%symmetry information recorded.' % ('S' if header['ftype'] == 1 else 'No s'))

    # ----- Find extremal density ----- #
    if source == 'custom':
        print('Extremal density given: %f (fm) Å⁻³\n' % extr)
    elif source == 'min':
        extr = input_data.min()
        print('Minimum density found: %f (fm) Å⁻³\n' % extr)
    else:
        extr = input_data.max()
        print('Maximum density found: %f (fm) Å⁻³\n' % extr)

    # ----- The real magic happens here ----- #
    print('Calculating OPP ... ', end='')
    old_err = np.seterr(invalid='ignore')  # Suppress warnings for processing non-positive values (yields NaN/-inf)
    output_data = -K_B * temp * np.log(input_data/extr)
    np.seterr(**old_err)  # Restore old error settings
    max_opp = np.nanmax(output_data)
    output_data[np.logical_not(np.isfinite(output_data))] = max_opp  # Set NaN/-inf to highest OPP
    print('Done.')
    print('Maximal finite OPP: %f eV\n' % max_opp)

    # ----- Write out data ----- #
    print('Opening output file and writing data ... ', end='')
    header['title'] = mbyte_truncate('OPP from ' + header['title'], 79, 'utf-8')  # Crop title to 79 bytes
    write_grid(output_file, header, indices, output_data)
    print('Done.')

    # ----- Build VESTA file for easy visualization ----- #
    print('Creating VESTA file ... ', end='')
    create_vesta(output_file, header['title'], 0.5*max_opp, header['ftype'])
    print('Done.\n')

    goodbye()


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
