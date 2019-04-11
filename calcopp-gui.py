#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
"""A graphical user interface for the calculation of effective one-particle potentials (OPPs).

CalcOPP – Calculation of Effective One-Particle Potentials
CalcOPP-GUI – The Graphical User Interface of CalcOPP

This program provides a GUI for the different routines of CalcOPP taking scatter densities, two- or three-dimensional
 probability-density functions as input.

CalcOPP-GUI uses the module PySimpleGUI by MikeTheWatchGuy distributed under the GNU General Public License v3.0 (see
 LGPL-3.0.txt).
"""

import os
import shlex
import subprocess as sp
import traceback as tb
import PySimpleGUI as sg
import annotations as an
import sd2opp

__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2019, Dr. Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.0'
__maintainer__ = 'Dennis Wiedemann'
__email__ = 'dennis.wiedemann@chem.tu-berlin.de'
__status__ = 'Production'


def file_exists(file):
    """Check if a file exists.

    :param file: name of the file to check for
    :type file: str
    :return: existence of file
    :rtype: bool
    """
    return os.path.isfile(file)


def is_float(string):
    """Check if a string can be converted to a non-zero float.

    :param string: string to check for convertibility
    :type string: str
    :return: convertibility of string
    :rtype: bool
    """
    try:
        return True if float(string) != 0 else False
    except ValueError:
        return False


def is_pos_float(string):
    """Check if a string can be converted to a positive float.

    :param string: string to check for convertibility
    :type string: str
    :return: convertibility of string
    :rtype: bool
    """
    try:
        return True if float(string) > 0 else False
    except ValueError:
        return False


def sp_args():
    """Apply quirks for ``subprocess.Popen`` to have standard behavior in PyInstaller-frozen windows binary.

    :return: additional arguments for ``subprocess`` calls
    :rtype: kwargs
    """
    if hasattr(sp, 'STARTUPINFO'):  # True only on Windows

        # Prevent Windows from popping up a command window on subprocess calls
        startup_info = sp.STARTUPINFO()
        startup_info.dwFlags |= sp.STARTF_USESHOWWINDOW

        # Make Windows search the ``PATH``
        environment = os.environ

    else:
        startup_info = None
        environment = None

    # Avoid ``OSError`` exception by redirecting all standard handles
    return {'stdout': sp.PIPE, 'stdin': sp.PIPE, 'stderr': sp.PIPE, 'startupinfo': startup_info, 'env': environment,
            'close_fds': True}


def doc_handler():
    """Return the command for opening document files with the standard application for its type (on Windows and Linux).

    :return: filename of handler for opening documents
    :rtype: string
    """
    return 'explorer.exe' if hasattr(sp, 'STARTUPINFO') else 'xdg-open'


# ===== Menu Definition ===== #
menu_def = [['&File', 'E&xit'], ['&Help', ['&Readme', '&Changelog', '---', '&About …']]]

# ===== Left Column Definition ===== #
column_left = [
    [sg.Frame('Information and Manual', [[sg.Multiline(size=(61, 25), font=('Courier', 9), key='manual')]])],
    [sg.Frame('Citation', [
        [sg.Text('If you publish data calculated with CalcOPP, please use the following citation:')],
        [sg.Text(an.CITATION, font=(None, 10, 'italic'))]])]
]

# ===== Right Column Definition ===== #
# ----- Tab for 2D PDF Data Sources ----- #
tab_pdf2d = [
    [sg.Frame('Files', [
        [sg.Text('Input PDF file', size=(14, 1)),
         sg.InputText(key='2d_file_in'),
         sg.FileBrowse(file_types=(("Structured File", "*.stf"),))
         ],
        [sg.Text('Input error file', size=(14, 1)),
         sg.InputText(disabled=True, key='2d_file_err'),
         sg.FileBrowse(disabled=True, key='2d_file_err_button', file_types=(("Structured File", "*.stf"),))
         ],
        [sg.Text('Output file', size=(14, 1)),
         sg.InputText(key='2d_file_out'),
         sg.FileSaveAs(file_types=(("ASCII Text", "*_opp.asc"),))
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006’s *.m90 file', "TEMP2D", change_submits=True, default=True, key='2d_temp_source_m90'),
        sg.Radio('Custom value:', "TEMP2D", change_submits=True, key='2d_temp_source_custom'),
        sg.InputText(size=(8, 1), disabled=True, key='2d_temp'),
        sg.Text('K')
    ]])],
    [sg.Frame('Include in Output', [[
        sg.Checkbox('PDF (source)', key='2d_output_pdf'),
        sg.Checkbox('PDF error (source)', change_submits=True, key='2d_output_pdf_err'),
        sg.Checkbox('OPP', default=True, key='2d_output_opp'),
        sg.Checkbox('OPP error', change_submits=True, key='2d_output_opp_err')
    ]])],
    [sg.ReadButton('Make it so!', key='2d_okay'), sg.ReadButton('Reset', key='2d_reset')]
]

# ----- Tab for 3D PDF Data Sources ----- #
tab_pdf3d = [
    [sg.Frame('Files', [
        [sg.Text('Input PDF file', size=(14, 1)),
         sg.InputText(key='3d_file_in'),
         sg.FileBrowse(file_types=(("XCrySDen Structure", "*_tmp.xsf"),))
         ],
        [sg.Text('Output file', size=(14, 1)),
         sg.InputText(key='3d_file_out'),
         sg.FileSaveAs(file_types=(("XCrySDen Structure", "*_opp.xsf"),))
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006’s *.m90 file', "TEMP3D", change_submits=True, default=True, key='3d_temp_source_m90'),
        sg.Radio('Custom value:', "TEMP3D", change_submits=True, key='3d_temp_source_custom'),
        sg.InputText(size=(8, 1), disabled=True, key='3d_temp'),
        sg.Text('K')
    ]])],
    [sg.ReadButton('Engage!', key='3d_okay'), sg.ReadButton('Reset', key='3d_reset')]
]

# ----- Tab for Scatterer-Density Data Source ----- #
tab_sd = [
    [sg.Frame('Files', [
        [sg.Text('Input density file', size=(14, 1)),
         sg.InputText(key='sd_file_in'),
         sg.FileBrowse(file_types=(("Periodic Grid", "*.pgrid"),))
         ],
        [sg.Text('Output density file', size=(14, 1)),
         sg.InputText(key='sd_file_out'),
         sg.FileSaveAs(file_types=(("Periodic Grid", "*_opp.pgrid"),))
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.InputText(size=(8, 1), key='sd_temp'),
        sg.Text('K')
    ]])],
    [sg.Frame('Extremal Value', [[
        sg.Radio('Negative minimum', "EXTREMUM", default=True, change_submits=True, key='sd_extremum_source_minimum'),
        sg.Radio('Positive maximum', "EXTREMUM", change_submits=True, key='sd_extremum_source_maximum'),
        sg.Radio('Custom value:', "EXTREMUM", change_submits=True, key='sd_extremum_source_custom'),
        sg.InputText(size=(8, 1), disabled=True, key='sd_extremum'),
        sg.Text('(fm) Å⁻³')
    ]])],
    [sg.ReadButton('Go already!', key='sd_okay'), sg.ReadButton('Reset', key='sd_reset')]
]

# ----- Assembly of Right Column ----- #
column_right = [
    [sg.TabGroup([[
        sg.Tab('2D PDF', tab_pdf2d),
        sg.Tab('3D PDF', tab_pdf3d),
        sg.Tab('Scatterer Density', tab_sd)]],
        change_submits=True, key='data_source')],
    [sg.Frame('Output', [[sg.Output(size=(77, 12), font=('Courier', 9), key='output')]])]
]

# ===== Window Invocation ===== #
layout = [[sg.Menu(menu_def), sg.Column(column_left), sg.Column(column_right)]]
window = sg.Window('CalcOPP – Calculation of One-Particle Potentials', default_element_size=(40, 1),
                   icon=os.path.join('data', 'CalcOPP.ico')).Layout(layout)

# ===== Event Loop for Persistent Window (Main Program) ===== #
while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break

    # ----- Toggle Explanations According to Tab ----- #
    if event == 'data_source':
        window.Element('manual').Update(disabled=False)
        if values['data_source'] == '2D PDF':
            window.Element('manual').Update(value=an.MANUAL_PDF2D)
        elif values['data_source'] == '3D PDF':
            window.Element('manual').Update(value=an.MANUAL_PDF3D)
        else:
            window.Element('manual').Update(value=an.MANUAL_SD)
        window.Element('manual').Update(disabled=True)

    # ----- Toggle Custom Temperature/Extremum Fields ----- #
    elif '_source_' in event:

        if values['2d_temp_source_custom']:
            window.Element('2d_temp').Update(disabled=False)
        else:
            window.Element('2d_temp').Update(disabled=True)

        if values['3d_temp_source_custom']:
            window.Element('3d_temp').Update(disabled=False)
        else:
            window.Element('3d_temp').Update(disabled=True)

        if values['sd_extremum_source_custom']:
            window.Element('sd_extremum').Update(disabled=False)
        else:
            window.Element('sd_extremum').Update(disabled=True)

    # ----- Toggle Error Processing for 2D PDF ----- #
    elif event.startswith('2d_output'):
        if values['2d_output_opp_err'] or values['2d_output_pdf_err']:
            window.Element('2d_file_err').Update(disabled=False)
            window.Element('2d_file_err_button').Update(disabled=False)
        else:
            window.Element('2d_file_err').Update(disabled=True)
            window.Element('2d_file_err_button').Update(disabled=True)

    # ----- Empty Tab on Reset Button ----- #
    elif event.endswith('reset'):

        # ····· Empty 2D PDF Tab on Reset Button ····· #
        if event == '2d_reset':
            window.Element('2d_file_in').Update('')
            window.Element('2d_file_err').Update('')
            window.Element('2d_file_out').Update('')
            window.Element('2d_temp_source_m90').Update(value=True)
            window.Element('2d_temp').Update('', disabled=True)
            window.Element('2d_output_pdf').Update(value=False)
            window.Element('2d_output_pdf_err').Update(value=False)
            window.Element('2d_output_opp').Update(value=True)
            window.Element('2d_output_opp_err').Update(value=False)
            window.Element('manual').Update(value=an.MANUAL_PDF2D)
            window.Element('output').Update('')

        # ····· Empty 3D PDF Tab on Reset Button ····· #
        elif event == '3d_reset':
            window.Element('3d_file_in').Update('')
            window.Element('3d_file_out').Update('')
            window.Element('3d_temp_source_m90').Update(value=True)
            window.Element('3d_temp').Update('', disabled=True)
            window.Element('manual').Update(value=an.MANUAL_PDF3D)
            window.Element('output').Update('')

        # ····· Empty Scatterer Density Tab on Reset Button ····· #
        else:
            window.Element('sd_file_in').Update('')
            window.Element('sd_file_out').Update('')
            window.Element('sd_temp').Update('')
            window.Element('sd_extremum_source_minimum').Update(value=True)
            window.Element('sd_extremum').Update('', disabled=True)
            window.Element('manual').Update(value=an.MANUAL_SD)
            window.Element('output').Update('')

    # ----- Open README or CHANGELOG ----- #
    elif event in ['Readme', 'Changelog']:
        sp.run([doc_handler(), os.path.join('docs', '%s.html' % event.upper())], **sp_args())

    # ----- Open "About" Window ----- #
    elif event == 'About …':

        # ····· "About" Window Definition ····· #  (keep in the same control structure as call to not retain state)
        layout_about = [
            [sg.Image(filename=os.path.join('data', 'logo.png'))],
            [sg.Text('\nCalcOPP – Calculation of One-Particle Potentials', font=(None, 18))],
            [sg.Text('Version %s\n' % __version__, font=(None, 14))],
            [sg.Text(an.CITATION)],
            [sg.Text('Export Citation:'),
             sg.Radio('RIS format', "FORMAT", default=True, key='format_ris'),
             sg.Radio('BibTeX format', "FORMAT", key='format_bib'),
             sg.ReadButton('Export', key='citation_export')],
            [sg.Text('\n' + an.LICENSE)],
            [sg.CloseButton('Done')]
        ]
        window.Hide()
        window_about = sg.Window('About …', icon=os.path.join('data', 'CalcOPP.ico')).Layout(layout_about)

        # ····· Handle Citation Exports ····· #
        while True:
            event_about, values_about = window_about.Read()
            if event_about is None or event_about == 'Exit':
                window.UnHide()
                break
            elif event_about == 'citation_export':
                if values_about['format_ris']:
                    sp.run([doc_handler(), os.path.join('data', 'citation.ris')], **sp_args())
                else:
                    sp.run([doc_handler(), os.path.join('data', 'citation.bib')], **sp_args())

    # ----- Start Calculations ----- #
    else:

        # ····· Check 2D PDF Input Values for Errors ····· #
        error_message = ''
        if event == '2d_okay':
            if values['2d_file_in'] == '':
                error_message += '\nNo input file is given.'
            elif not file_exists(values['2d_file_in']):
                error_message += '\nInput file does not exist.'
            if values['2d_output_opp_err'] or values['2d_output_pdf_err']:
                if values['2d_file_err'] == '':
                    error_message += '\nNo error file is given.'
                elif not file_exists(values['2d_file_err']):
                    error_message += '\nError file does not exist.'
                if values['2d_file_err'] == values['2d_file_in'] and values['2d_file_in'] != '':
                    error_message += '\nInput and error file are the same.'
                if values['2d_file_out'] == values['2d_file_err'] and values['2d_file_out'] != '':
                    error_message += '\nError and output file are the same.'
            if values['2d_file_out'] == '':
                error_message += '\nNo output file is given.'
            elif values['2d_file_out'] == values['2d_file_in']:
                error_message += '\nInput and output file are the same.'
            if values['2d_temp_source_m90'] and not file_exists(values['2d_file_in'][:-4] + '.m90'):
                error_message += '\nFile *.m90 does not exist in the same directory.'
            if values['2d_temp_source_custom'] and not is_pos_float(values['2d_temp']):
                error_message += '\nTemperature has to be a positive decimal.'
            if not (values['2d_output_opp'] or values['2d_output_pdf']
                    or values['2d_output_opp_err'] or values['2d_output_pdf_err']):
                error_message += '\nNo data to include in output selected.'

        # ····· Check 3D PDF Input Values for Errors ····· #
        elif event == '3d_okay':
            if values['3d_file_in'] == '':
                error_message += '\nNo input file is given.'
            elif not file_exists(values['3d_file_in']):
                error_message += '\nInput file does not exist.'
            if values['3d_file_out'] == '':
                error_message += '\nNo output file is given.'
            elif values['3d_file_out'] == values['3d_file_in']:
                error_message += '\nInput and output file are the same.'
            if values['3d_temp_source_m90'] and not file_exists(values['3d_file_in'][:-8] + '.m90'):
                error_message += '\nFile *.m90 does not exist in the same directory.'
            if values['3d_temp_source_custom'] and not is_pos_float(values['3d_temp']):
                error_message += '\nTemperature has to be a positive decimal.'

        # ····· Check Scatterer Density Input Values for Errors ····· #
        elif event == 'sd_okay':
            if values['sd_file_in'] == '':
                error_message += '\nNo input file is given.'
            elif not file_exists(values['sd_file_in']):
                error_message += '\nInput file does not exist.'
            if values['sd_file_out'] == '':
                error_message += '\nNo output file is given.'
            elif values['sd_file_out'] == values['sd_file_in']:
                error_message += '\nInput and output file are the same.'
            if not is_pos_float(values['sd_temp']):
                error_message += '\nTemperature has to be a positive decimal.'
            if values['sd_extremum_source_custom'] and not is_float(values['sd_extremum']):
                error_message += '\nExtremal value has to be a decimal.'

        if error_message != '':
            # ····· Display Error Message ····· #
            sg.PopupError(error_message[1:] + '\n', title='Error', icon=os.path.join('data', 'CalcOPP.ico'))

        else:

            # ····· Spawn 2D OPP Calculation Routine ····· #
            if event == '2d_okay':

                #       Assemble Command Line       #
                command_line = './pdf2opp_2d'
                command_line += ' -i ' + values['2d_file_in']
                command_line += ' -o ' + values['2d_file_out']
                if values['2d_output_opp_err'] or values['2d_output_pdf_err']:
                    command_line += ' -e ' + values['2d_file_err']
                command_line += ' -t ' + values['2d_temp'] if values['2d_temp_source_custom'] else ''
                command_line += ' -pdf' if values['2d_output_pdf'] else ''
                command_line += ' -pdferr' if values['2d_output_pdf_err'] else ''
                command_line += ' -opp' if values['2d_output_opp'] else ''
                command_line += ' -opperr' if values['2d_output_opp_err'] else ''

                window.Element('2d_okay').Update(disabled=True)

                try:
                    #       Execute Command       #
                    pdf2opp = sp.Popen(shlex.split(command_line), text=True, **sp_args())
                    for line in pdf2opp.stdout:
                        print(line.rstrip())
                        window.Refresh()

                    #       Show Popup on Error       #
                    _, error_message = pdf2opp.communicate()
                    print(error_message)
                    if error_message != '':
                        error_message = error_message[11:] if error_message.startswith('ERROR STOP ') else error_message
                        error_message = (an.ERROR_INTRO % 'PDF2OPP_2D') + error_message
                        sg.PopupError(error_message, title='Subroutine Error', icon=os.path.join('data', 'CalcOPP.ico'))

                except FileNotFoundError:
                    error_message = 'PDF2OPP_2D executable not found in program directory.'
                    sg.PopupError(error_message, title='Program Error', icon=os.path.join('data', 'CalcOPP.ico'))

                window.Element('2d_okay').Update(disabled=False)

            # ····· Spawn 3D OPP Calculation Routine ····· #
            elif event == '3d_okay':

                #       Assemble Command Line       #
                command_line = './pdf2opp_3d'
                command_line += ' -i ' + values['3d_file_in']
                command_line += ' -o ' + values['3d_file_out']
                command_line += ' -t ' + values['3d_temp'] if values['3d_temp_source_custom'] else ''

                window.Element('3d_okay').Update(disabled=True)

                try:
                    #       Execute Command       #
                    pdf3opp = sp.Popen(shlex.split(command_line), text=True, **sp_args())
                    for line in pdf3opp.stdout:
                        print(line.rstrip())
                        window.Refresh()

                    #       Show Popup on Error       #
                    _, error_message = pdf3opp.communicate()
                    print(error_message)
                    if error_message != '':
                        error_message = error_message[11:] if error_message.startswith('ERROR STOP ') else error_message
                        error_message = (an.ERROR_INTRO % 'PDF2OPP_3D') + error_message
                        sg.PopupError(error_message, title='Subroutine Error', icon=os.path.join('data', 'CalcOPP.ico'))

                except FileNotFoundError:
                    error_message = 'PDF2OPP_3D executable not found in program directory.'
                    sg.PopupError(error_message, title='Program Error', icon=os.path.join('data', 'CalcOPP.ico'))

                window.Element('3d_okay').Update(disabled=False)

            # ····· Call OPP Calculation from Scatterer Density ····· #
            elif event == 'sd_okay':

                window.Element('sd_okay').Update(disabled=True)

                #       Construct String for Extremum Source       #
                if values['sd_extremum_source_minimum']:
                    source = 'min'
                elif values['sd_extremum_source_maximum']:
                    source = 'max'
                else:
                    source = 'custom'

                try:
                    #       Call Calculation Routine       #
                    sd2opp.calc_opp(values['sd_file_in'], values['sd_file_out'], float(values['sd_temp']),
                                    source, float(values['sd_extremum']) if source == 'custom' else None)
                except Exception:
                    #       Show Popup on Error       #
                    error_message = (an.ERROR_INTRO % 'SD2OPP') + tb.format_exc()
                    sg.PopupError(error_message, title='Subroutine Error', icon=os.path.join('data', 'CalcOPP.ico'))

                window.Element('sd_okay').Update(disabled=False)
