#!/usr/bin/python3.9
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
import subprocess as sp
from traceback import format_exc
from urllib.parse import quote, urlencode
import sys
from webbrowser import open as web_open
import PySimpleGUI as sg
import annotations as an
import sd2opp


__author__ = 'Dennis Wiedemann'
__copyright__ = 'Copyright 2021, Dr. Dennis Wiedemann'
__credits__ = ['Dennis Wiedemann']
__license__ = 'MIT'
__version__ = '2.0.5'
__maintainer__ = 'Dennis Wiedemann'
__email__ = 'dennis.wiedemann@chem.tu-berlin.de'
__status__ = 'Production'


def file_exists(file):
    """Check if a file exists.

    Parameters
    ----------
    file : str
        The file name to check.

    Returns
    -------
    bool
        True if the file exists, False if it does not.
    """
    return os.path.isfile(file)


def is_float(string):
    """Check if a string can be converted to a non-zero float.

    Parameters
    ----------
    string : str
        The string to check for convertibility.

    Returns
    -------
    bool
        True if the string can be converted, False if it cannot.
    """
    try:
        return True if float(string) != 0 else False
    except ValueError:
        return False


def is_pos_float(string):
    """Check if a string can be converted to a positive float.

    Parameters
    ----------
    string : str
        The string to check for convertibility.

    Returns
    -------
    bool
        True if the string can be converted, False if it cannot.
    """
    try:
        return True if float(string) > 0 else False
    except ValueError:
        return False


def sp_args():
    """Apply quirks for `subprocess.Popen` to have standard behavior in PyInstaller-frozen windows binary.

    Returns
    -------
    dict[str, str or bool or None]
        The additional arguments for `subprocess` calls.

    """
    if sys.platform.startswith('win32'):

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
    """Return the command for opening document files with the standard application for its type (on Windows, Linux, and
     macOS).

    Returns
    -------
    str
        The handler file name for opening documents.

    Raises
    ------
    FileNotFoundError
        If no handler is found due to an unknown operating system.

    """
    if sys.platform.startswith('win32'):
        return 'explorer.exe'
    elif sys.platform.startswith('linux'):
        return 'xdg-open'
    elif sys.platform.startswith('darwin'):
        return 'open'
    else:
        raise FileNotFoundError('Unknown operating system: File handler not found')


def subroutine_error_popup(subroutine, error, message):
    """Display a popup for errors in subroutines.

    Parameters
    ----------
    subroutine : str
        The name of the subroutine causing the error.
    error : Exception or str
        The error caused by the subroutine.
    message : str
        The additional error message to be displayed.

    """
    # ===== Error Window Definition ===== #
    error_layout = [
        [sg.Text(an.ERROR_INTRO.format(subroutine))],
        [sg.Text(message)],
        [sg.Text(an.ERROR_OUTRO, text_color='red')],
        [sg.Text('', font='default 10 italic', key='-COPY_DONE-', size=(40, 1))],
        [sg.Button('Copy to clipboard', key='-CLIPBOARD-'),
         sg.Button('Send as e-mail', key='-EMAIL-', bind_return_key=True, focus=True),
         sg.Exit('Close', key='close')]
    ]
    error_window = sg.Window('Subroutine Error', error_layout, modal=True)

    # ===== Handle Button Actions ===== #
    while True:
        event_error, values_error = error_window.Read()
        if event_error in [sg.WIN_CLOSED, 'close']:
            error_window.close()
            break

        # Copy trace to clipboard
        elif event_error == '-CLIPBOARD-':
            sg.clipboard_set('Version: {}\n\n{}\n\n{}'.format(__version__, str(error), message))
            error_window['-COPY_DONE-']('(Error message copied to clipboard.)')

        # Compose bug report as e-mail
        elif event_error == '-EMAIL-':
            query = {'subject': f'Error in {subroutine}',
                     'body': 'Version:\n{}\n\nMessage:\n{}\n\nComment:\n'.format(__version__, message)}
            web_open(f'mailto:{__email__}?{urlencode(query, quote_via=quote)}', new=1)


# ===== Global GUI Parameters ===== #
sg.theme('Dark Grey 4')
sg.set_global_icon(os.path.join('data', 'CalcOPP.ico'))

# ===== Menu Definition ===== #
menu_def = [['&File', 'E&xit'], ['&Help', ['&Readme', '&Changelog', sg.MENU_SEPARATOR_LINE, '&About …']]]

# ===== Left Column Definition ===== #
column_left = [
    [sg.Frame('Information and Manual', [[sg.Multiline(write_only=True, auto_refresh=True, size=(61, 25), key='manual',
                                                       font='Courier 9', reroute_cprint=True, autoscroll=False,
                                                       pad=((7, 11), 6))]])],
    [sg.Frame('Citation', [
        [sg.Text('If you publish data calculated with CalcOPP, please use the following citation:')],
        [sg.Text(an.CITATION, font='default 10 italic')]])]
]

# ===== Right Column Definition ===== #
# ----- Tab for 2D PDF Data Sources ----- #
tab_pdf2d = [
    [sg.Frame('Files', [
        [sg.Text('Input PDF file', size=(14, 1)),
         sg.Input(key='2d_file_in'),
         sg.FileBrowse(file_types=(('Structured File', '*.stf'),), pad=((5, 81), 3))
         ],
        [sg.Text('Input error file', size=(14, 1)),
         sg.Input(disabled=True, key='2d_file_err'),
         sg.FileBrowse(disabled=True, key='2d_file_err_button', file_types=(('Structured File', '*.stf'),))
         ],
        [sg.Text('Output file', size=(14, 1)),
         sg.Input(key='2d_file_out'),
         sg.SaveAs(file_types=(('ASCII Text', '*_opp.asc'),), default_extension='asc')
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006’s *.m90 file', 'TEMP2D', enable_events=True, default=True, key='2d_temp_source_m90'),
        sg.Radio('Custom value:', 'TEMP2D', enable_events=True, key='2d_temp_source_custom'),
        sg.Input(size=(8, 1), disabled=True, key='2d_temp'),
        sg.Text('K', pad=((5, 152), 3))
    ]])],
    [sg.Frame('Include in Output', [[
        sg.Checkbox('PDF (source)', key='2d_output_pdf'),
        sg.Checkbox('PDF error (source)', enable_events=True, key='2d_output_pdf_err'),
        sg.Checkbox('OPP', default=True, key='2d_output_opp'),
        sg.Checkbox('OPP error', enable_events=True, key='2d_output_opp_err', pad=((5, 146), 3)),
    ]])],
    [sg.OK('Make it so!', key='2d_okay'), sg.OK('Reset', key='2d_reset')]
]

# ----- Tab for 3D PDF Data Sources ----- #
tab_pdf3d = [
    [sg.Frame('Files', [
        [sg.Text('Input PDF file', size=(14, 1)),
         sg.Input(key='3d_file_in'),
         sg.FileBrowse(file_types=(('XCrySDen Structure', '*_tmp.xsf'),), pad=((5, 81), 3))
         ],
        [sg.Text('Output file', size=(14, 1)),
         sg.Input(key='3d_file_out'),
         sg.SaveAs(file_types=(('XCrySDen Structure', '*_opp.xsf'),), default_extension='xsf')
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Radio('From JANA2006’s *.m90 file', 'TEMP3D', enable_events=True, default=True, key='3d_temp_source_m90'),
        sg.Radio('Custom value:', 'TEMP3D', enable_events=True, key='3d_temp_source_custom'),
        sg.Input(size=(8, 1), disabled=True, key='3d_temp'),
        sg.Text('K', pad=((5, 152), 3))
    ]])],
    [sg.OK('Engage!', key='3d_okay'), sg.OK('Reset', key='3d_reset')]
]

# ----- Tab for Scatterer-Density Data Source ----- #
tab_sd = [
    [sg.Frame('Files', [
        [sg.Text('Input density file', size=(14, 1)),
         sg.Input(key='sd_file_in'),
         sg.FileBrowse(file_types=(('Periodic Grid', '*.pgrid'),), pad=((5, 81), 3))
         ],
        [sg.Text('Output density file', size=(14, 1)),
         sg.Input(key='sd_file_out'),
         sg.SaveAs(file_types=(('Periodic Grid', '*_opp.pgrid'),), default_extension='pgrid')
         ]
    ])],
    [sg.Frame('Temperature', [[
        sg.Input(size=(8, 1), key='sd_temp'),
        sg.Text('K', pad=((5, 471), (3, 7)))
    ]])],
    [sg.Frame('Extremal Value', [[
        sg.Radio('Negative minimum', 'EXTREMUM', default=True, enable_events=True, key='sd_extremum_source_minimum'),
        sg.Radio('Positive maximum', 'EXTREMUM', enable_events=True, key='sd_extremum_source_maximum'),
        sg.Radio('Custom value:', 'EXTREMUM', enable_events=True, key='sd_extremum_source_custom'),
        sg.Input(size=(8, 1), disabled=True, key='sd_extremum'),
        sg.Text('(fm) Å⁻³', pad=((5, 29), 3))
    ]])],
    [sg.OK('Go already!', key='sd_okay'), sg.OK('Reset', key='sd_reset')]
]

# ----- Assembly of Right Column ----- #
column_right = [
    [sg.TabGroup([[sg.Tab('2D PDF', tab_pdf2d), sg.Tab('3D PDF', tab_pdf3d), sg.Tab('Scatterer Density', tab_sd)]],
                 enable_events=True, key='data_source')],
    [sg.Frame('Output', [[sg.Multiline(size=(77, 12), font='Courier 9', key='output', autoscroll=True, write_only=True,
                                       auto_refresh=True, reroute_stderr=True, reroute_stdout=True, disabled=True)]])]
]

# ===== Window Invocation ===== #
layout_main = [[sg.Menu(menu_def), sg.Column(column_left), sg.Column(column_right)]]
window_main = sg.Window('CalcOPP – Calculation of One-Particle Potentials', layout_main, default_element_size=(40, 1))

# ===== Event Loop for Persistent Window (Main Program) ===== #
while True:
    event_main, values_main = window_main.read()
    if event_main in [sg.WIN_CLOSED, 'Exit']:
        window_main.close()
        break

    # ----- Toggle Explanations According to Tab ----- #
    if event_main == 'data_source':
        if values_main['data_source'] == '2D PDF':
            manual = an.MANUAL_PDF2D
        elif values_main['data_source'] == '3D PDF':
            manual = an.MANUAL_PDF3D
        else:
            manual = an.MANUAL_SD
        window_main['manual']('')
        for section in manual:
            kwargs = section.copy()
            text = kwargs.pop('text')
            sg.cprint(text, **kwargs, autoscroll=False)
        window_main['manual'](disabled=True)

    # ----- Toggle Custom Temperature/Extremum Fields ----- #
    elif '_source_' in event_main:

        if values_main['2d_temp_source_custom']:
            window_main['2d_temp'](disabled=False)
        else:
            window_main['2d_temp'](disabled=True)

        if values_main['3d_temp_source_custom']:
            window_main['3d_temp'](disabled=False)
        else:
            window_main['3d_temp'](disabled=True)

        if values_main['sd_extremum_source_custom']:
            window_main['sd_extremum'](disabled=False)
        else:
            window_main['sd_extremum'](disabled=True)

    # ----- Toggle Error Processing for 2D PDF ----- #
    elif event_main.startswith('2d_output'):
        if values_main['2d_output_opp_err'] or values_main['2d_output_pdf_err']:
            window_main['2d_file_err'](disabled=False)
            window_main['2d_file_err_button'](disabled=False)
        else:
            window_main['2d_file_err'](disabled=True)
            window_main['2d_file_err_button'](disabled=True)

    # ----- Empty Tab on Reset Button ----- #
    elif event_main.endswith('reset'):

        # ····· Empty 2D PDF Tab on Reset Button ····· #
        if event_main == '2d_reset':
            window_main['2d_file_in']('')
            window_main['2d_file_err']('')
            window_main['2d_file_out']('')
            window_main['2d_temp_source_m90'](True)
            window_main['2d_temp']('', disabled=True)
            window_main['2d_output_pdf'](False)
            window_main['2d_output_pdf_err'](False)
            window_main['2d_output_opp'](True)
            window_main['2d_output_opp_err'](False)
            window_main['manual'](an.MANUAL_PDF2D)
            window_main['output']('')

        # ····· Empty 3D PDF Tab on Reset Button ····· #
        elif event_main == '3d_reset':
            window_main['3d_file_in']('')
            window_main['3d_file_out']('')
            window_main['3d_temp_source_m90'](True)
            window_main['3d_temp']('', disabled=True)
            window_main['manual'](an.MANUAL_PDF3D)
            window_main['output']('')

        # ····· Empty Scatterer Density Tab on Reset Button ····· #
        else:
            window_main['sd_file_in']('')
            window_main['sd_file_out']('')
            window_main['sd_temp']('')
            window_main['sd_extremum_source_minimum'](True)
            window_main['sd_extremum']('', disabled=True)
            window_main['manual'](an.MANUAL_SD)
            window_main['output']('')

    # ----- Open README or CHANGELOG ----- #
    elif event_main in ['Readme', 'Changelog']:
        sp.run([doc_handler(), os.path.join('docs', f'{event_main.upper()}.html')], **sp_args())

    # ----- Open "About" Window ----- #
    elif event_main == 'About …':

        # ····· "About" Window Definition ····· #  (keep in the same control structure as call to not retain state)
        layout_about = [
            [sg.Image(os.path.join('data', 'logo.png'))],
            [sg.Text('\nCalcOPP – Calculation of One-Particle Potentials', font='default 18')],
            [sg.Text('Version {}\n'.format(__version__), font='default 14')],
            [sg.Text(an.CITATION)],
            [sg.Text('Export Citation:'),
             sg.Radio('RIS format', 'FORMAT', default=True, key='-FORMAT_RIS-'),
             sg.Radio('BibTeX format', 'FORMAT', key='-FORMAT_BIB-'),
             sg.OK('Export', key='-CITATION_EXPORT-')],
            [sg.Text(' ')],
            *[[sg.Text(link, font='default 10 underline', key=f'-LINK_{an.LINKS.index(link)}-', enable_events=True)]
              for link in an.LINKS],
            [sg.Text('\n' + an.LICENSE)],
            [sg.Exit('Done')]
        ]

        window_about = sg.Window('About …', layout_about, modal=True)

        # ····· Handle Citation Exports and Link Clicks ····· #
        while True:
            event_about, values_about = window_about.read()
            if event_about in [sg.WIN_CLOSED, 'Done']:
                window_about.close()
                break
            elif event_about == '-CITATION_EXPORT-':
                if values_about['-FORMAT_RIS-']:
                    sp.run([doc_handler(), os.path.join('data', 'citation.ris')], **sp_args())
                else:
                    sp.run([doc_handler(), os.path.join('data', 'citation.bib')], **sp_args())
            elif event_about.startswith('-LINK_'):
                web_open(an.LINKS[int(event_about.removeprefix('-LINK_').removesuffix('-'))], new=1)

    # ----- Start Calculations ----- #
    else:

        # ····· Check 2D PDF Input Values for Errors ····· #
        error_message = ''
        if event_main == '2d_okay':
            if not values_main['2d_file_in']:
                error_message += '\nNo input file is given.'
            elif not file_exists(values_main['2d_file_in']):
                error_message += '\nInput file does not exist.'
            if values_main['2d_output_opp_err'] or values_main['2d_output_pdf_err']:
                if not values_main['2d_file_err']:
                    error_message += '\nNo error file is given.'
                elif not file_exists(values_main['2d_file_err']):
                    error_message += '\nError file does not exist.'
                if values_main['2d_file_err'] == values_main['2d_file_in'] and values_main['2d_file_in']:
                    error_message += '\nInput and error file are the same.'
                if values_main['2d_file_out'] == values_main['2d_file_err'] and values_main['2d_file_out']:
                    error_message += '\nError and output file are the same.'
            if not values_main['2d_file_out']:
                error_message += '\nNo output file is given.'
            elif values_main['2d_file_out'] == values_main['2d_file_in']:
                error_message += '\nInput and output file are the same.'
            if values_main['2d_temp_source_m90'] and not file_exists(values_main['2d_file_in'][:-4] + '.m90'):
                error_message += '\nFile *.m90 does not exist in the same directory.'
            if values_main['2d_temp_source_custom'] and not is_pos_float(values_main['2d_temp']):
                error_message += '\nTemperature must be a positive decimal.'
            if not (values_main['2d_output_opp'] or values_main['2d_output_pdf']
                    or values_main['2d_output_opp_err'] or values_main['2d_output_pdf_err']):
                error_message += '\nNo data to include in output selected.'

        # ····· Check 3D PDF Input Values for Errors ····· #
        elif event_main == '3d_okay':
            if not values_main['3d_file_in']:
                error_message += '\nNo input file is given.'
            elif not file_exists(values_main['3d_file_in']):
                error_message += '\nInput file does not exist.'
            if not values_main['3d_file_out']:
                error_message += '\nNo output file is given.'
            elif values_main['3d_file_out'] == values_main['3d_file_in']:
                error_message += '\nInput and output file are the same.'
            if values_main['3d_temp_source_m90'] and not file_exists(values_main['3d_file_in'][:-8] + '.m90'):
                error_message += '\nFile *.m90 does not exist in the same directory.'
            if values_main['3d_temp_source_custom'] and not is_pos_float(values_main['3d_temp']):
                error_message += '\nTemperature must be a positive decimal.'

        # ····· Check Scatterer Density Input Values for Errors ····· #
        elif event_main == 'sd_okay':
            if not values_main['sd_file_in']:
                error_message += '\nNo input file is given.'
            elif not file_exists(values_main['sd_file_in']):
                error_message += '\nInput file does not exist.'
            if not values_main['sd_file_out']:
                error_message += '\nNo output file is given.'
            elif values_main['sd_file_out'] == values_main['sd_file_in']:
                error_message += '\nInput and output file are the same.'
            if not is_pos_float(values_main['sd_temp']):
                error_message += '\nTemperature must be a positive decimal.'
            if values_main['sd_extremum_source_custom'] and not is_float(values_main['sd_extremum']):
                error_message += '\nExtremal value must be a decimal.'

        if error_message:
            # ····· Display Error Message ····· #
            sg.popup_error(error_message[1:] + '\n', title='Error')

        else:

            # ····· Spawn 2D OPP Calculation Routine ····· #
            if event_main == '2d_okay':

                #       Assemble Command Line       #
                command_line = [os.path.join('.', 'pdf2opp_2d')]
                command_line.extend(['-i', values_main['2d_file_in']])
                command_line.extend(['-o', values_main['2d_file_out']])
                if values_main['2d_output_opp_err'] or values_main['2d_output_pdf_err']:
                    command_line.extend(['-e', values_main['2d_file_err']])
                if values_main['2d_temp_source_custom']:
                    command_line.extend(['-t', values_main['2d_temp']])
                if values_main['2d_output_pdf']:
                    command_line.append('-pdf')
                if values_main['2d_output_pdf_err']:
                    command_line.append('-pdferr')
                if values_main['2d_output_opp']:
                    command_line.append('-opp')
                if values_main['2d_output_opp_err']:
                    command_line.append('-opperr')

                window_main['2d_okay'](disabled=True)

                try:
                    #       Execute Command       #
                    pdf2opp = sp.Popen(command_line, text=True, **sp_args())
                    for line in pdf2opp.stdout:
                        print(line.rstrip())
                        window_main.refresh()

                    #       Show Popup on Error       #
                    _, error_message = pdf2opp.communicate()
                    print(error_message)
                    if error_message.startswith('ERROR STOP '):
                        subroutine_error_popup('PDF2OPP_2D', 'ERROR STOP', error_message[11:])
                    elif error_message:
                        subroutine_error_popup('PDF2OPP_2D', 'Unknown error', error_message)

                except FileNotFoundError:
                    error_message = 'PDF2OPP_2D executable not found in program directory.'
                    sg.popup_error(error_message, title='Program Error')

                window_main['2d_okay'](disabled=False)

            # ····· Spawn 3D OPP Calculation Routine ····· #
            elif event_main == '3d_okay':

                #       Assemble Command Line       #
                command_line = [os.path.join('.', 'pdf2opp_3d')]
                command_line.extend(['-i', values_main['3d_file_in']])
                command_line.extend(['-o', values_main['3d_file_out']])
                if values_main['3d_temp_source_custom']:
                    command_line.extend(['-t', values_main['3d_temp']])

                window_main['3d_okay'](disabled=True)

                try:
                    #       Execute Command       #
                    pdf3opp = sp.Popen(command_line, text=True, **sp_args())
                    for line in pdf3opp.stdout:
                        print(line.rstrip())
                        window_main.refresh()

                    #       Show Popup on Error       #
                    _, error_message = pdf3opp.communicate()
                    print(error_message)
                    if error_message.startswith('ERROR STOP '):
                        subroutine_error_popup('PDF2OPP_3D', 'ERROR STOP', error_message[11:])
                    elif error_message:
                        subroutine_error_popup('PDF2OPP_3D', 'Unknown error', error_message)

                except FileNotFoundError:
                    error_message = 'PDF2OPP_3D executable not found in program directory.'
                    sg.popup_error(error_message, title='Program Error')

                window_main['3d_okay'](disabled=False)

            # ····· Call OPP Calculation from Scatterer Density ····· #
            elif event_main == 'sd_okay':

                window_main['sd_okay'](disabled=True)

                #       Construct String for Extremum Source       #
                if values_main['sd_extremum_source_minimum']:
                    source = 'min'
                elif values_main['sd_extremum_source_maximum']:
                    source = 'max'
                else:
                    source = 'custom'

                try:
                    #       Call Calculation Routine       #
                    sd2opp.calc_opp(values_main['sd_file_in'], values_main['sd_file_out'],
                                    float(values_main['sd_temp']), source,
                                    float(values_main['sd_extremum']) if source == 'custom' else None)
                except Exception as exc:
                    subroutine_error_popup('SD2OPP', exc, format_exc())

                window_main['sd_okay'](disabled=False)
