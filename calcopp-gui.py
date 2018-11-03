#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
"""CalcOPP-GUI – A Graphical User Interface for the Calculation of One-Particle Potentials

This program provides a GUI for the different routines of CalcOPP taking scatter densities,
two- or three-dimensional probability-density functions as input. It relies on PySimpleGUI.

Author: Dr. Dennis Wiedemann
Contact: dennis.wiedemann@chem.tu-berlin.de
License:
"""
import PySimpleGUI as sg
import Annotations as Annot
import os
import platform


def file_exists(file_name):
    return os.path.isfile(file_name)


def is_float(string_variable):
    global window
    try:
        float(string_variable)
        return True
    except ValueError:
        return False


def os_is_64bit():
    return platform.machine().endswith('64')


# ====== Menu Definition ====== #
menu_def = [['&File', '&Exit'], ['&Help', '&About …']]

# ====== Left Column Definition ====== #
column_left = [
    [sg.Frame('Information and Manual', [[sg.Multiline(size=(61, None), do_not_clear=True, key='manual')]])],
    [sg.Frame('Citation', [
        [sg.Text('If you publish data calculated with CalcOPP, please use the following citation:')],
        [sg.Text(Annot.CITATION, font=(None, 10, 'italic'))]])]
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
         sg.InputText(do_not_clear=True, key='2d_file_out'),
         sg.FileSaveAs(file_types=(("ASCII Text", "*_opp.asc"),))
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006’s *.m40 file', "TEMP2D", change_submits=True, default=True, key='2d_temp_source_m40'),
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
         sg.InputText(do_not_clear=True, key='3d_file_out'),
         sg.FileSaveAs(file_types=(("XCrySDen Structure", "*_opp.xsf"),))
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006’s *.m40 file', "TEMP3D", change_submits=True, default=True, key='3d_temp_source_m40'),
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
         sg.InputText(do_not_clear=True, key='sd_file_out'),
         sg.FileSaveAs(file_types=(("Periodic Grid", "*_opp.pgrid"),))
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
        sg.Text('(fm) Å\u207B³')
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
    [sg.Frame('Output', [[sg.Output(size=(77, 12))]])]
]

# ====== "About" Window Definition ===== #
layout_about = [
    [sg.Image(filename='logo.png')],
    [sg.Text('\nCalcOPP – Calculation of One-Particle Potentials', font=('None', 18))],
    [sg.Text('Version 2.0.0\n', font=('None', 14))],
    [sg.Text(Annot.CITATION + '\n')],
    [sg.CloseButton('Done')]
]

# ====== Window Invocation ===== #
layout = [[sg.Menu(menu_def), sg.Column(column_left), sg.Column(column_right)]]
window = sg.Window('CalcOPP – Calculation of One-Particle Potentials',
                   default_element_size=(40, 1),
                   icon='logo.ico',
                   grab_anywhere=False).Layout(layout)

# ====== Event Loop for Persistent Window (Main Program) ===== #
while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break

    # ------ Toggle Explanations According to Tab ----- #
    if event == 'data_source':
        if values['data_source'] == '2D PDF':
            window.FindElement('manual').Update(value=Annot.MANUAL_PDF2D)
        elif values['data_source'] == '3D PDF':
            window.FindElement('manual').Update(value=Annot.MANUAL_PDF3D)
        else:
            window.FindElement('manual').Update(value=Annot.MANUAL_SD)

    # ------ Toggle Custom Temperature/Extremum Fields ----- #
    elif '_source_' in event:

        if values['2d_temp_source_custom']:
            window.FindElement('2d_temp').Update(disabled=False)
        else:
            window.FindElement('2d_temp').Update(disabled=True)

        if values['3d_temp_source_custom']:
            window.FindElement('3d_temp').Update(disabled=False)
        else:
            window.FindElement('3d_temp').Update(disabled=True)

        if values['sd_extremum_source_custom']:
            window.FindElement('sd_extremum').Update(disabled=False)
        else:
            window.FindElement('sd_extremum').Update(disabled=True)

    # ------ Toggle Error Processing for 2D PDF ----- #
    elif event.startswith('2d_output'):
        if values['2d_output_opp_err'] or values['2d_output_pdf_err']:
            window.FindElement('2d_file_err').Update(disabled=False)
            window.FindElement('2d_file_err_button').Update(disabled=False)
        else:
            window.FindElement('2d_file_err').Update(disabled=True)
            window.FindElement('2d_file_err_button').Update(disabled=True)

    # ------ Empty Tab on Reset Button ----- #
    elif event.endswith('reset'):

        # ····· Empty 2D PDF Tab on Reset Button ····· #
        if event == '2d_reset':
            window.FindElement('2d_file_in').Update('')
            window.FindElement('2d_file_err').Update('')
            window.FindElement('2d_file_out').Update('')
            window.FindElement('2d_temp_source_m40').Update(value=True)
            window.FindElement('2d_temp').Update('', disabled=True)
            window.FindElement('2d_output_pdf').Update(value=False)
            window.FindElement('2d_output_pdf_err').Update(value=False)
            window.FindElement('2d_output_opp').Update(value=True)
            window.FindElement('2d_output_opp_err').Update(value=False)
            window.FindElement('manual').Update(value=Annot.MANUAL_PDF2D)

        # ····· Empty 3D PDF Tab on Reset Button ····· #
        elif event == '3d_reset':
            window.FindElement('3d_file_in').Update('')
            window.FindElement('3d_file_out').Update('')
            window.FindElement('3d_temp_source_m40').Update(value=True)
            window.FindElement('3d_temp').Update('', disabled=True)
            window.FindElement('manual').Update(value=Annot.MANUAL_PDF3D)

        # ····· Empty Scatterer Density Tab on Reset Button ····· #
        else:
            window.FindElement('sd_file_in').Update('')
            window.FindElement('sd_file_out').Update('')
            window.FindElement('sd_temp').Update('')
            window.FindElement('sd_extremum_source_minimum').Update(value=True)
            window.FindElement('sd_extremum').Update('', disabled=True)
            window.FindElement('manual').Update(value=Annot.MANUAL_SD)

    # ------ Open "About" Window ----- #
    elif event == 'About …':
        window_about = sg.Window('About …', grab_anywhere=False, icon='logo.ico').Layout(layout_about)
        window_about.Read()

    # ------ Start Calculations ----- #
    else:

        # ····· Check 2D PDF Input Values for Errors ····· #
        error_message = ''
        if event == '2d_okay':
            if not file_exists(values['2d_file_in']):
                error_message += '\nInput file does not exist.'
            if (values['2d_output_opp_err'] or values['2d_output_pdf_err']) and not file_exists(values['2d_file_err']):
                error_message += '\nError file does not exist.'
            if values['2d_file_out'] == '':
                error_message += '\nNo output file is given.'
            if values['2d_temp_source_m40'] and not file_exists(values['2d_file_in'][:-4] + '.m40'):
                error_message += '\nFile *.m40 does not exist in the same directory.'
            if values['2d_temp_source_custom'] and not is_float(values['2d_temp']):
                error_message += '\nTemperature has to be a decimal.'
            if not (values['2d_output_opp'] or values['2d_output_pdf']
                    or values['2d_output_opp_err'] or values['2d_output_pdf_err']):
                error_message += '\nNo data to include in output selected.'

        # ····· Check 3D PDF Input Values for Errors ····· #
        elif event == '3d_okay':
            if not file_exists(values['3d_file_in']):
                error_message += '\nInput file does not exist.'
            if values['3d_file_out'] == '':
                error_message += '\nNo output file is given.'
            if values['3d_temp_source_m40'] and not file_exists(values['3d_file_in'][:-8] + '.m40'):
                error_message += '\nFile *.m40 does not exist in the same directory.'
            if values['3d_temp_source_custom'] and not is_float(values['3d_temp']):
                error_message += '\nTemperature has to be a decimal.'

        # ····· Check Scatterer Density Input Values for Errors ····· #
        elif event == 'sd_okay':
            if not file_exists(values['sd_file_in']):
                error_message += '\nInput file does not exist.'
            if values['sd_file_out'] == '':
                error_message += '\nNo output file is given.'
            if not is_float(values['sd_temp']):
                error_message += '\nTemperature has to be a decimal.'
            if values['sd_extremum_source_custom'] and not is_float(values['sd_extremum']):
                error_message += '\nExtremal value has to be a decimal.'

        if error_message != '':
            # ····· Display Error Message ····· #
            sg.PopupError('Error', error_message[1:]+'\n', icon='logo.ico')

        else:
            # ····· Spawn 2D OPP Calculation Routine ····· #
            if event == '2d_okay':
                command_line = 'CalcOPP64' if os_is_64bit() else 'CalcOPP32'
                command_line += ' -i ' + values['2d_file_in'] + ' -o ' + values['2d_file_out']
                if values['2d_output_opp_err'] or values['2d_output_pdf_err']:
                    command_line += ' -e ' + values['2d_file_err']
                command_line += ' -t ' + values['2d_temp']  # TODO: make CalcOPP read from *.m40
                command_line += ' -pdf' if values['2d_output_pdf'] else ''
                command_line += ' -pdferr' if values['2d_output_pdf_err'] else ''
                command_line += ' -opp' if values['2d_output_opp'] else ''
                command_line += ' -opperr' if values['2d_output_opp_err'] else ''
                print(command_line)        # TODO: debug
                # os.system(command_line)  # TODO: debug

            # ····· Spawn 3D OPP Calculation Routine ····· #
            elif event == '3d_okay':
                command_line = 'CalcOPP-3D' if os_is_64bit() else 'CalcOPP-3D_32'  # TODO: compile 32-bit version
                command_line += ' -i ' + values['2d_file_in'] + ' -o ' + values['2d_file_out']
                # TODO: make CalcOPP-3D accept input and output file names
                command_line += ' -t ' + values['2d_temp'] if values['3d_temp_source_custom'] else ''
                # TODO: make CalcOPP-3D accept custom temperatures
                print(command_line)        # TODO: debug
                # os.system(command_line)  # TODO: debug

            # ····· Call OPP Calculation from Scatterer Density ····· #
            elif event == 'sd_okay':
                pass  # TODO: write and call sd2opp.py

# TODO Wishlist: Title of error window, multiline read-only
# TODO: annotations
