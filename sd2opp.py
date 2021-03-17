#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
"""A program for the calculation of effective one-particle potentials (OPPs) from scatterer densities.

CalcOPP – Calculation of Effective One-Particle Potentials
SD2OPP – Subroutines for Calculation from Scatterer-Density Data (Dysnomia PGRID Format)

This program calculates three-dimensional OPPs from electron or scattering-length densities reconstructed via
 maximum-entropy methods (MEM) as put out by the program Dysnomia.

SD2OPP uses the module NumPy by the NumPy developers distributed under the BSD License 2.0 (see BSD-2.0.txt).
"""

__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2021, Dr. Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.5'
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

    Parameters
    ----------
    string : str
        The string to check for convertibility.

    Returns
    -------
    float
        The converted non-zero float.

    Raises
    ------
    argparse.ArgumentTypeError
        If string does not represent a non-zero float.
    """
    try:
        value = float(string)
    except ValueError:
        raise ap.ArgumentTypeError(f'"{string}" is not a decimal.')
    if value == 0.:
        raise ap.ArgumentTypeError('Argument is zero.')
    return value


def pos_float(string):
    """Define positive floats for `argparse`.

        Parameters
        ----------
        string : str
            The string to check for convertibility.

        Returns
        -------
        float
            The converted positive float.

        Raises
        ------
        argparse.ArgumentTypeError
            If string does not represent a positive float.
    """
    try:
        value = float(string)
    except ValueError:
        raise ap.ArgumentTypeError(f'"{string}" is not a decimal.')
    if value <= 0.:
        message = f'"{value!r}" is not positive.'
        raise ap.ArgumentTypeError(message)
    return value


def multibyte_truncate(string, byte_length, encoding='utf-8'):
    """Truncate a multi-byte encoded string to a given maximal byte size.

    Parameters
    ----------
    string : str
        The string to truncate.
    byte_length : int
        The length in bytes to truncate to.
    encoding : str, optional
        The encoding of the string.

    Returns
    -------
    str
        The truncated string.
    """
    encoded = string.encode(encoding)[:byte_length]
    return encoded.decode(encoding, 'ignore')


def hello():
    """Print a greeting message.
    """
    print(f'SD2OPP {__version__} - Calculation of 3D OPP from Scatterer Density')
    print('{} ({} License, see LICENSE file)\n'.format(__copyright__, __license__))


def goodbye():
    """Print a farewell message.
    """
    print('All calculations finished. Have a nice day!')
    print('“Don’t be scared. […] It really doesn’t help.” – The Doctor\n\n')


def read_grid(file):
    u"""Read the binary input grid-file depending on its header.

    Parameters
    ----------
    file : str
        The path and name of the input file.

    Returns
    -------
    header : dict[str, str or numpy.int32 or numpy.ndarray]
        The file-header values (see `Notes`_ for details on keys, value types, and their meaning).
    indices : numpy.ndarray of numpy.int32
        The indices of the data points.
    data : numpy.ndarray of numpy.float32
        The data at each point.

    Notes
    -----
    The dictionary `header` will contain the following keys with values of the type given:

    - header['version'] : numpy.ndarray[4] of numpy.int32
          The quadripartite version number of input file.
    - header['title'] : str
          The title of the data set (maximum of 79 characters).
    - header['gtype'] : numpy.int32
          The grid type (0 for general grid, *.ggrid, 1 for periodic grid, *.pgrid).
    - header['ftype'] : numpy.int32
          The file record type (0 for raw data containing values only, 1 for records containing index and value[s]).
    - header['nval'] : numpy.int32
          The number of values per record (1 for records with either positive or negative data, 2 for records with both
          positive and negative values).
    - header['ndim'] : numpy.int32
          The dimension of the unit cell (has to be 3, currently).
    - header['ngrid'] : numpy.ndarray[3] of numpy.int32
          The number of voxels/records along each principal axes.
    - header['nasym'] : numpy.int32
          The total number of records/voxels.
    - header['cell'] : numpy.ndarray[6] of numpy.float32
          The unit cell parameters (order: *a*/Å, *b*/Å, *c*/Å, *α*/°, *β*/°, *γ*/°).
    - header['npos'] : numpy.int32
          The number of considered equivalent positions/symmetry operators.
    - header['ncen'] : numpy.int32
          An indicator for consideration of centrosymmetry (0 for non-centrosymmetric data, 1 for centrosymmetric data).
    - header['nsub'] : numpy.int32
          The number of considered lattice centering operations.
    - header['symop'] : numpy.ndarray of numpy.ndarray[12] of numpy.int32
          The symmetry operators as 3 × 4 matrices (each as 3 × 3 rotation matrix followed by translation vector).
    - header['subposp'] : numpy.ndarray[3] of numpy.int32
          The centering vector.

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


def write_grid(file, header, data, indices=None):
    """Write the binary output grid-file depending on its header.

    Parameters
    ----------
    file : str
        The path and name of the output file.
    header : dict [str, str or numpy.int32 or numpy.ndarray]
        The file-header values (see `Notes`_ for details on keys, value types, and their meaning).
    data : numpy.ndarray of numpy.float32
        The OPP data points to put out.
    indices : numpy.ndarray of numpy.int32, optional
        The indices of the data points (array must have same size as `data`).

    Notes
    -----
    The dictionary `header` must contain the following keys with valid values associated: 'version', 'title', 'gtype',
    'ftype', 'ndim', 'ngrid', 'cell', 'npos', 'ncen', 'nsub', 'symop', and 'subposp'. Refer to `read_grid` for full
    documentation.

    See Also
    --------
    read_grid : description of the meaning and type of the values in the dictionary `header`
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
            write_file.write(data.tobytes())


def create_vesta(output_file, title, isovalue, record_type):
    """Create a *.vesta file for displaying grid in VESTA.

    Parameters
    ----------
    output_file : str
        The path and name of the output grid-file.
    title : str
        The title of the grid file.
    isovalue : float
        The isosurface value to display (will be rounded).
    record_type : int
        The type of record in the grid file (`header['nval']` * `header['ftype']`).
    """
    with open(os.path.splitext(output_file)[0] + '.vesta', 'w') as file:
        file.write('#VESTA_FORMAT_VERSION 3.3.0\n\n\n')
        file.write('CRYSTAL\n\n')
        file.write('TITLE\n{}\n\n'.format(title))
        file.write('IMPORT_DENSITY 1\n+1.000000 {}\n\n'.format(os.path.split(output_file)[1]))
        file.write('STYLE\n')
        file.write('SECTS  96  0\n')
        file.write('ISURF\n')
        file.write('  1 {:3d}        {:.2f} 255 255   0 127 255\n'.format(record_type, isovalue))
        file.write('  0   0   0   0\n')


def calc_opp(input_file, output_file, temp, source, extr=None):
    """Start main routine for calculating the OPP from scatterer density.

    Parameters
    ----------
    input_file : str
        The path and name of the input file.
    output_file : str
        The path and name of the output file.
    temp : float
        The absolute temperature in Kelvin.
    source : {'min', 'max', 'custom'}
        An identifier for the source of the extremal value ('min': negative minimum, 'max': positive maximum, 'custom':
        user-provided value in parameter `extr`).
    extr : float, optional
        A user-provided extremal value.
    """
    hello()

    # ----- Read in data and display information ----- #
    print('Opening input file and reading data ... ', end='')
    header, indices, input_data = read_grid(input_file)
    print('Done.')
    print(header['ngrid'])
    print('Number of voxels: {} × {} × {}'.format(*header['ngrid']))
    print('Unit cell dimensions: a = {:f} Å, b = {:f} Å, c = {:f} Å,\n'
          '   α = {:f}°, β = {:f}°, γ = {:f}°'.format(*header['cell']))
    print(f"{'S' if header['ftype'] == 1 else 'No s'}ymmetry information recorded.")

    # ----- Find extremal density ----- #
    if source == 'custom':
        print('Extremal density given: {:f} (fm) Å⁻³\n'.format(extr))
    elif source == 'min':
        extr = input_data.min(initial=np.finfo(input_data.dtype).max)
        print('Minimum density found: {:f} (fm) Å⁻³\n'.format(extr))
    else:
        extr = input_data.max(initial=np.finfo(input_data.dtype).min)
        print('Maximum density found: {:f} (fm) Å⁻³\n'.format(extr))

    # ----- The real magic happens here ----- #
    print('Calculating OPP ... ', end='')
    old_err = np.seterr(invalid='ignore')  # Suppress warnings for processing non-positive values (yields NaN/-inf)
    output_data = -K_B * temp * np.log(input_data/extr)
    np.seterr(**old_err)  # Restore old error settings
    max_opp = np.nanmax(output_data)
    output_data[np.logical_not(np.isfinite(output_data))] = max_opp  # Set NaN/-inf to highest OPP
    print('Done.')
    print('Maximal finite OPP: {:f} eV\n'.format(max_opp))

    # ----- Write out data ----- #
    print('Opening output file and writing data ... ', end='')
    header['title'] = multibyte_truncate('OPP from ' + header['title'], 79, 'utf-8')  # Crop title to 79 bytes
    write_grid(output_file, header, output_data, indices)
    print('Done.')

    # ----- Build VESTA file for easy visualization ----- #
    print('Creating VESTA file ... ', end='')
    create_vesta(output_file, header['title'], 0.5*max_opp, header['ftype'])
    print('Done.\n')

    goodbye()


# ===== Routine for Running as Standalone Program ===== #
if __name__ == '__main__':

    # ----- Parse command-line arguments ----- #
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
    extremum_group.add_argument('-ext', '--extremum', type=non_zero_float,
                                help=u'set a custom extremal value in (fm) '
                                     u'Å⁻³')
    parser.add_argument('-v', '--version', action='version', version=__version__)

    cmd_args = parser.parse_args()

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
