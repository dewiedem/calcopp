#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
"""A graphical user interface for the calculation of one-particle potentials (OPPs).

CalcOPP â€“ Calculation of One-Particle Potentials
CalcOPP-GUI â€“ The Graphical User Interface of CalcOPP

This program provides a GUI for the different routines of CalcOPP taking scatter densities, two- or three-dimensional
 probability-density functions as input.

CalcOPP-GUI uses the module PySimpleGUI by MikeTheWatchGuy distributed under the GNU General Public License v3.0 (see
 LGPL-3.0.txt).
"""

import os
import platform
import shlex
import subprocess as sp
import PySimpleGUI as sg
import annotations as an

__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2019, Dr. Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.0'
__maintainer__ = 'Dennis Wiedemann'
__email__ = 'dennis.wiedemann@chem.tu-berlin.de'
__status__ = 'Development'


def file_exists(file):
    """Check if a file exists. # TODO: rework all docstrings

    Args:
        file (str): name of the file to check for
    """
    return os.path.isfile(file)


def is_float(string):
    """Check if a string can be converted to a non-zero float.

    Args:
        string (str): string to check for convertibility
    """
    try:
        return True if float(string) != 0 else False
    except ValueError:
        return False


def is_pos_float(string):
    """Check if a string can be converted to a positive float.

    Args:
        string (str): string to check for convertibility
    """
    try:
        return True if float(string) > 0 else False
    except ValueError:
        return False


def os_is_64bit():
    """Check if the operating system is of the 64-bit type.

    Note: checks the machine type, because other methods return the
    capability of the CPU or the bitness of the interpreter/compiled executable.
    """
    return platform.machine().endswith('64')


# ====== Menu Definition ====== #
menu_def = [['&File', '&Exit'], ['&Help', '&About â€¦']]

# ====== Left Column Definition ====== #
column_left = [
    [sg.Frame('Information and Manual', [[sg.Multiline(size=(61, None), font=('Courier', 9),
                                                       do_not_clear=True, key='manual')]])],
    [sg.Frame('Citation', [
        [sg.Text('If you publish data calculated with CalcOPP, please use the following citation:')],
        [sg.Text(an.CITATION, font=(None, 10, 'italic'))]])]
]

# ====== Right Column Definition ====== #
# ------ Tab for 2D PDF Data Sources ----- #
tab_pdf2d = [
    [sg.Frame('Files', [
        [sg.Text('Input PDF file', size=(14, 1)),
         sg.InputText(do_not_clear=True, key='2d_file_in'),
         sg.FileBrowse(file_types=(("Structured File", "*.stf"),))
         ],
        [sg.Text('Input error file', size=(14, 1)),
         sg.InputText(do_not_clear=True, disabled=True, key='2d_file_err'),
         sg.FileBrowse(disabled=True, file_types=(("Structured File", "*.stf"),), key='2d_file_err_button')
         ],
        [sg.Text('Output file', size=(14, 1)),
         sg.InputText(do_not_clear=True, change_submits=True, key='2d_file_out'),
         sg.FileSaveAs(file_types=(("ASCII Text", "*_opp.asc"),))
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006â€™s *.m90 file', "TEMP2D", change_submits=True, default=True, key='2d_temp_source_m90'),
        sg.Radio('Custom value:', "TEMP2D", change_submits=True, key='2d_temp_source_custom'),
        sg.InputText(size=(8, 1), do_not_clear=True, disabled=True, key='2d_temp'),
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

# ------ Tab for 3D PDF Data Sources ----- #
tab_pdf3d = [
    [sg.Frame('Files', [
        [sg.Text('Input PDF file', size=(14, 1)),
         sg.InputText(do_not_clear=True, key='3d_file_in'),
         sg.FileBrowse(file_types=(("XCrySDen Structure", "*_tmp.xsf"),))
         ],
        [sg.Text('Output file', size=(14, 1)),
         sg.InputText(do_not_clear=True, change_submits=True, key='3d_file_out'),
         sg.FileSaveAs(file_types=(("XCrySDen Structure", "*_opp.xsf"),))
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006â€™s *.m90 file', "TEMP3D", change_submits=True, default=True, key='3d_temp_source_m90'),
        sg.Radio('Custom value:', "TEMP3D", change_submits=True, key='3d_temp_source_custom'),
        sg.InputText(size=(8, 1), disabled=True, do_not_clear=True, key='3d_temp'),
        sg.Text('K')
    ]])],
    [sg.ReadButton('Engage!', key='3d_okay'), sg.ReadButton('Reset', key='3d_reset')]
]

# ------ Tab for Scatterer-Density Data Source ----- #
tab_sd = [
    [sg.Frame('Files', [
        [sg.Text('Input density file', size=(14, 1)),
         sg.InputText(do_not_clear=True, key='sd_file_in'),
         sg.FileBrowse(file_types=(("Periodic Grid", "*.pgrid"),))
         ],
        [sg.Text('Output density file', size=(14, 1)),
         sg.InputText(do_not_clear=True, key='sd_file_out', change_submits=True),
         sg.FileSaveAs(file_types=(("Periodic Grid", "*_opp.pgrid"),), key='sd_file_out_button')
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.InputText(size=(8, 1), do_not_clear=True, key='sd_temp'),
        sg.Text('K')
    ]])],
    [sg.Frame('Extremal Value', [[
        sg.Radio('Negative minimum', "EXTREMUM", default=True, change_submits=True, key='sd_extremum_source_minimum'),
        sg.Radio('Positive maximum', "EXTREMUM", change_submits=True, key='sd_extremum_source_maximum'),
        sg.Radio('Custom value:', "EXTREMUM", change_submits=True, key='sd_extremum_source_custom'),
        sg.InputText(size=(8, 1), disabled=True, do_not_clear=True, key='sd_extremum'),
        sg.Text('(fm) Ã…\u207BÂ³')
    ]])],
    [sg.ReadButton('Go already!', key='sd_okay'), sg.ReadButton('Reset', key='sd_reset')]
]

# ------ Assembly of Right Column ----- #
column_right = [
    [sg.TabGroup([[
        sg.Tab('2D PDF', tab_pdf2d),
        sg.Tab('3D PDF', tab_pdf3d),
        sg.Tab('Scatterer Density', tab_sd)]],
        change_submits=True, key='data_source')],
    [sg.Frame('Output', [[sg.Output(size=(77, 12), key='output')]])]
]

# ====== "About" Window Definition ===== #
layout_about = [
    [sg.Image(filename='logo.png')],
    [sg.Text('\nCalcOPP â€“ Calculation of One-Particle Potentials', font=('None', 18))],
    [sg.Text('Version %s\n' % __version__, font=('None', 14))],
    [sg.Text(an.CITATION)],
    [sg.Text('Export Citation:'),
     sg.Radio('RIS format', "FORMAT", default=True, key='format_ris'),
     sg.Radio('BibTeX format', "FORMAT", key='format_bib'),
     sg.ReadButton('Export', key='citation_export')],
    [sg.Text('\n' + an.LICENSE)],
    [sg.CloseButton('Done')]
]

# ====== Window Invocation ===== #
layout = [[sg.Menu(menu_def), sg.Column(column_left), sg.Column(column_right)]]
window = sg.Window('CalcOPP â€“ Calculation of One-Particle Potentials',
                   default_element_size=(40, 1),
                   icon='CalcOPP.ico',
                   grab_anywhere=False).Layout(layout)

# ====== Event Loop for Persistent Window (Main Program) ===== #
while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break

    # ------ Toggle Explanations According to Tab ----- #
    if event == 'data_source':
        if values['data_source'] == '2D PDF':
            window.Element('manual').Update(value=an.MANUAL_PDF2D)
        elif values['data_source'] == '3D PDF':
            window.Element('manual').Update(value=an.MANUAL_PDF3D)
        else:
            window.Element('manual').Update(value=an.MANUAL_SD)

    # ------ Add Extension to Output File Names ----- #
    elif event.endswith('_file_out'):

        # Â·Â·Â·Â·Â· Add Extension to 2D OPP Output File Name Â·Â·Â·Â·Â· #
        if (event == '2d_file_out') and (not values['2d_file_out'].endswith('_opp.asc')):
            window.Element('2d_file_out').Update(values['2d_file_out'] + '_opp.asc')

        # Â·Â·Â·Â·Â· Add Extension to 3D OPP Output File Name Â·Â·Â·Â·Â· #
        elif (event == '3d_file_out') and (not values['3d_file_out'].endswith('_opp.xsf')):
            window.Element('3d_file_out').Update(values['3d_file_out'] + '_opp.xsf')

        # Â·Â·Â·Â·Â· Add Extension to Scatterer Density OPP Output File Name Â·Â·Â·Â·Â· #
        elif (event == 'sd_file_out') and (not values['sd_file_out'].endswith('_opp.pgrid')):
            window.Element('sd_file_out').Update(values['sd_file_out'] + '_opp.pgrid')

    # ------ Toggle Custom Temperature/Extremum Fields ----- #
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

    # ------ Toggle Error Processing for 2D PDF ----- #
    elif event.startswith('2d_output'):
        if values['2d_output_opp_err'] or values['2d_output_pdf_err']:
            window.Element('2d_file_err').Update(disabled=False)
            window.Element('2d_file_err_button').Update(disabled=False)
        else:
            window.Element('2d_file_err').Update(disabled=True)
            window.Element('2d_file_err_button').Update(disabled=True)

    # ------ Empty Tab on Reset Button ----- #
    elif event.endswith('reset'):

        # Â·Â·Â·Â·Â· Empty 2D PDF Tab on Reset Button Â·Â·Â·Â·Â· #
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

        # Â·Â·Â·Â·Â· Empty 3D PDF Tab on Reset Button Â·Â·Â·Â·Â· #
        elif event == '3d_reset':
            window.Element('3d_file_in').Update('')
            window.Element('3d_file_out').Update('')
            window.Element('3d_temp_source_m90').Update(value=True)
            window.Element('3d_temp').Update('', disabled=True)
            window.Element('manual').Update(value=an.MANUAL_PDF3D)
            window.Element('output').Update('')

        # Â·Â·Â·Â·Â· Empty Scatterer Density Tab on Reset Button Â·Â·Â·Â·Â· #
        else:
            window.Element('sd_file_in').Update('')
            window.Element('sd_file_out').Update('')
            window.Element('sd_temp').Update('')
            window.Element('sd_extremum_source_minimum').Update(value=True)
            window.Element('sd_extremum').Update('', disabled=True)
            window.Element('manual').Update(value=an.MANUAL_SD)
            window.Element('output').Update('')

    # ------ Open "About" Window ----- #
    elif event == 'About â€¦':
        window_about = sg.Window('About â€¦', grab_anywhere=False, icon='CalcOPP.ico').Layout(layout_about)

        # Â·Â·Â·Â·Â· Handle Citation Exports Â·Â·Â·Â·Â· #
        while True:
            event_about, values_about = window_about.Read()
            if event_about is None or event_about == 'Exit':
                break
            elif event_about == 'citation_export':
                if values_about['format_ris']:
                    sp.run('citation.ris', shell=True)
                else:
                    sp.run('citation.bib', shell=True)

    # ------ Start Calculations ----- #
    else:

        # Â·Â·Â·Â·Â· Check 2D PDF Input Values for Errors Â·Â·Â·Â·Â· #
        error_message = ''
        if event == '2d_okay':
            if not file_exists(values['2d_file_in']):
                error_message += '\nInput file does not exist.'
            if (values['2d_output_opp_err'] or values['2d_output_pdf_err']) and not file_exists(values['2d_file_err']):
                error_message += '\nError file does not exist.'
            if values['2d_file_out'] == '':
                error_message += '\nNo output file is given.'
            if values['2d_temp_source_m90'] and not file_exists(values['2d_file_in'][:-4] + '.m90'):
                error_message += '\nFile *.m90 does not exist in the same directory.'
            if values['2d_temp_source_custom'] and not is_pos_float(values['2d_temp']):
                error_message += '\nTemperature has to be a positive decimal.'
            if not (values['2d_output_opp'] or values['2d_output_pdf']
                    or values['2d_output_opp_err'] or values['2d_output_pdf_err']):
                error_message += '\nNo data to include in output selected.'

        # Â·Â·Â·Â·Â· Check 3D PDF Input Values for Errors Â·Â·Â·Â·Â· #
        elif event == '3d_okay':
            if not file_exists(values['3d_file_in']):
                error_message += '\nInput file does not exist.'
            if values['3d_file_out'] == '':
                error_message += '\nNo output file is given.'
            if values['3d_temp_source_m90'] and not file_exists(values['3d_file_in'][:-8] + '.m90'):
                error_message += '\nFile *.m90 does not exist in the same directory.'
            if values['3d_temp_source_custom'] and not is_pos_float(values['3d_temp']):
                error_message += '\nTemperature has to be a positive decimal.'

        # Â·Â·Â·Â·Â· Check Scatterer Density Input Values for Errors Â·Â·Â·Â·Â· #
        elif event == 'sd_okay':
            if not file_exists(values['sd_file_in']):
                error_message += '\nInput file does not exist.'
            if values['sd_file_out'] == '':
                error_message += '\nNo output file is given.'
            if not is_pos_float(values['sd_temp']):
                error_message += '\nTemperature has to be a positive decimal.'
            if values['sd_extremum_source_custom'] and not is_float(values['sd_extremum']):
                error_message += '\nExtremal value has to be a decimal.'

        if error_message != '':
            # Â·Â·Â·Â·Â· Display Error Message Â·Â·Â·Â·Â· #
            sg.PopupError(error_message[1:] + '\n', grab_anywhere=False, title='Error', icon='CalcOPP.ico')

        else:

            # Â·Â·Â·Â·Â· Spawn 2D OPP Calculation Routine Â·Â·Â·Â·Â· #
            if event == '2d_okay':

                #       Assemble Command Line       #
                command_line = 'pdf2opp_2d-x64' if os_is_64bit() else 'pdf2opp_2d-x86'
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
                    pdf2opp = sp.Popen(shlex.split(command_line), stderr=sp.PIPE, stdout=sp.PIPE, text=True)
                    for line in pdf2opp.stdout:
                        print(line.rstrip())
                        window.Refresh()

                    #       Show Popup on Error       #
                    _, error_message = pdf2opp.communicate()
                    print(error_message)
                    if error_message != '':
                        error_message = error_message[11:] if error_message.startswith('ERROR STOP ') else error_message
                        sg.PopupError(error_message, grab_anywhere=False, title='Subroutine Error', icon='CalcOPP.ico')

                except FileNotFoundError:
                    error_message = 'PDF2OPP executable not found in program directory.'
                    sg.PopupError(error_message, grab_anywhere=False, title='Program Error', icon='CalcOPP.ico')

                window.Element('2d_okay').Update(disabled=False)

            # Â·Â·Â·Â·Â· Spawn 3D OPP Calculation Routine Â·Â·Â·Â·Â· #
            elif event == '3d_okay':

                #       Assemble Command Line       #
                command_line = 'pdf2opp_3d-x64' if os_is_64bit() else 'pdf2opp_3d-x86'
                command_line += ' -i ' + values['3d_file_in']
                command_line += ' -o ' + values['3d_file_out']
                # TODO: make CalcOPP-3D accept input and output file names
                command_line += ' -t ' + values['3d_temp'] if values['3d_temp_source_custom'] else ''
                # TODO: make CalcOPP-3D accept custom temperatures
                print(command_line)        # TODO: debug

                #       Execute Command       #
                # os.system(command_line)  # TODO: write subroutine for spawning

            # Â·Â·Â·Â·Â· Call OPP Calculation from Scatterer Density Â·Â·Â·Â·Â· #
            elif event == 'sd_okay':
                pass  # TODO: write and call sd2opp.py

# TODO: wait in pdf2opp before closing window, if invoked via drag and drop
