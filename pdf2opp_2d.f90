program pdf2opp_2d

!   CalcOPP 2.0.2 - Calculation of Effective One-Particle Potentials
!   PDF2OPP_2D - Subroutines for Calculation from 2D PDF Data (JANA2006 STF Format)
!   Copyright (c) 2020  Dr. Dennis Wiedemann (MIT License, see LICENSE file)

implicit none
character(len = 256)               :: file_input, file_output, file_error, file_m90         ! Names of handled files
character(len = 256)               :: key                                                   ! Key read from input file
character(len = 256)               :: line                                                  ! Input line read from *.m90 file
character(len = 256)               :: cmd_arg                                               ! Command-line argument
character(len = 256)               :: temp_string                                           ! Temperature as string
integer                            :: i, j                                                  ! Counters
integer                            :: in_unit, out_unit, err_unit, m90_unit, opp_unit, &
                                      pdferr_unit                                           ! Unit numbers for file access
integer                            :: io_status                                             ! Status of the file I/O                             !
integer, dimension(2)              :: pos_0                                                 ! Position of maximum PDF
integer, dimension(2)              :: data_num, err_data_num                                ! Number of data points in x/y direction
                                                                                            !   in input/error file
real                               :: temp                                                  ! Temperature in Kelvin
real                               :: pdf_0, err_pdf_0                                      ! Maximum input/error PDF
real, dimension(2)                 :: range_min, range_max, err_range_min, err_range_max    ! Minimal/maximal x/y values in
                                                                                            !   input/error file
real, dimension(2)                 :: inc                                                   ! Increment in x/y direction
real, dimension(:, :), allocatable :: z, opp_low_err                                        ! (Error) PDF/OPP values as x * y matrix
real, dimension(:, :), allocatable :: pdf                                                   ! PDF values as x * y matrix
logical                            :: exists_input, exists_error, exists_m90                ! Flags for existence of files
logical                            :: output_pdf, output_pdferr, output_opp, output_opperr  ! Flags controlling data output
logical                            :: is_dnd                                                ! Flag for drag and drop

character(len = *), parameter      :: SEPARATOR = ' ' // repeat('=', 50)                    ! Visual separator for standard output
character(len = *), parameter      :: VERSION = '2.0.1'                                     ! Program version
real, parameter                    :: K_B = 1.380649E-23 / 1.602176634E-19                  ! Boltzmann constant in eV/K (according
                                                                                            !   to CODATA 2018)
real, parameter                    :: INFINITE_OPP = 1.0E6                                  ! Pseudo-infinite OPP in eV


! ACQUIRING NECESSARY INPUT

! Parsing command line arguments
file_input = ''
file_output = ''
file_error = ''
temp = -1.0
output_pdf = .false.
output_pdferr = .false.
output_opp = .false.
output_opperr = .false.
is_dnd = .false.
opp_unit = -1
pdferr_unit = -1

i = 1
do while (i <= command_argument_count())
    call get_command_argument(i, cmd_arg)
    select case (cmd_arg)
        case ('-i')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_input)
            else
                call print_help()
                call finish('Used -i, but no input file name provided.', is_dnd)
            end if
            i = i + 1
        case ('-o')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_output)
            else
                call print_help()
                call finish('Used -o, but no output file name provided.', is_dnd)
            end if
            i = i + 1
        case ('-e')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_error)
            else
                call print_help()
                call finish('Used -e, but no error map name provided.', is_dnd)
            end if
            i = i + 1
        case ('-t')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, temp_string)
                read(temp_string, *, iostat = io_status) temp
                if (io_status /= 0) call finish('Used -t, but no valid temperature as decimal value provided.', is_dnd)
            else
                call print_help()
                call finish('Used -t, but no temperature provided.', is_dnd)
            end if
            i = i + 1
        case ('-pdf')
            output_pdf = .true.
            i = i + 1
        case ('-pdferr')
            output_pdferr = .true.
            i = i + 1
        case ('-opp')
            output_opp = .true.
            i = i + 1
        case ('-opperr')
            output_opperr = .true.
            i = i + 1
        case ('-h')
            call print_help()
            call finish('', is_dnd)
        case ('-v')
            write(*, fmt = '(A)') VERSION
            call finish('', is_dnd)
        case default
            if (index(cmd_arg, '-') == 1) then
                call print_help()
                call finish('Unrecognized command-line option: ' // trim(cmd_arg), is_dnd)
            else if (file_input == '') then
                file_input = cmd_arg
                is_dnd = .true.
            else
                write(*, *) 'Ignoring unexpected input: ' // trim(cmd_arg)
            end if
            i = i + 1
    end select
end do

if (.not.(output_pdf .or. output_pdferr .or. output_opp .or. output_opperr)) then
    output_pdf = .true.
    output_pdferr = .true.
    output_opp = .true.
    output_opperr = .true.
end if

call print_greeting(VERSION)
write(*, fmt = '(/, A, /)') SEPARATOR  ! separates greeting from checking

! Check if input file name is valid (vital)
if (file_input == '') then
    call print_help()
    call finish('No input file name provided.', is_dnd)
else
    exists_input = .false.
    inquire(file = file_input, exist = exists_input)
    if (.not. exists_input) call finish('No valid input file name provided.', is_dnd)
end if

! Automatically set output file name, if not provided
if (file_output == '') file_output = new_ext(file_input, '_opp.asc')

! Automatically set error map name, if not provided and necessary, and check existence
if (output_pdferr .or. output_opperr) then
    if (file_error == '') file_error = new_ext(file_input, '_err.stf')
    exists_error = .false.
    inquire(file = file_error, exist = exists_error)
    if (.not. exists_error) then
        write(*, *) 'Error map not found. PDF/OPP uncertainty will not be included in output.'
        output_pdferr = .false.
        output_opperr = .false.
    end if
end if

! Temperature extraction from *.m90
if ((temp <= 0.0) .and. (output_opp .or. output_opperr)) then
    write(*, fmt = '(A)', advance = 'no') ' Temperature not given. Probing *.m90 ...'

    ! Construct file name of *.m90
    file_m90 = new_ext(file_input, '.m90')

    ! Try automatic extraction from *.m90
    exists_m90 = .false.
    inquire(file = file_m90, exist = exists_m90)
    if (exists_m90) then
        write(*, fmt = '(A)', advance = 'no') ' found.'
        open(newunit = m90_unit, file = file_m90, status = 'old', action = 'read')
        line = ''

        ! Search for keyword "datcolltemp"
        io_status = 0
        do while ((io_status == 0) .and. (index(line, 'datcolltemp ') == 0))
            read(m90_unit, fmt = '(A256)', iostat = io_status) line
        end do
        close(m90_unit)

        ! Try to read in following value
        if (io_status == 0) then
            read(line(12:), *, iostat = io_status) temp
            if (io_status /= 0) call finish('No valid temperature found in *.m90.', is_dnd)
            write(*, *)
            write(*, fmt = '(A, F0.4, A)') ' Temperature: T = ', temp, ' K'
        else
            call finish('No valid temperature found in *.m90.', is_dnd)
        end if
    else
        write(*, *) 'failed.'
        call finish('Temperature not given and *.m90 not found.', is_dnd)
    end if
end if

write(*, *) 'Necessary input data acquired.'
write(*, fmt = '(/, A, /)') SEPARATOR  ! separates checking from calculation

! PARSING INPUT FILE(S)

! Search for DIMENSIONS
open(newunit = in_unit, file = file_input, status = 'old', action = 'read')
io_status = 0
key = ''
do while ((io_status == 0) .and. (key /= 'DIMENSIONS'))
    read(in_unit, *, iostat = io_status) key
end do
if (io_status /= 0) then
    close(in_unit)
    call finish('Unable to find grid dimensions in input file.', is_dnd)
end if
backspace(in_unit)
read(in_unit, *, iostat = io_status) key, data_num
if (io_status /= 0) then
    close(in_unit)
    call finish('Unable to read grid dimensions from input file.', is_dnd)
end if
write(*, fmt = '(A, 3X, I0, 3X, I0)') ' Numbers of data points (x, y):', data_num
write(*, *)

! Search for BOUNDS
rewind(in_unit)
io_status = 0
key = ''
do while ((io_status == 0) .and. (key /= 'BOUNDS'))
    read(in_unit, *, iostat = io_status) key
end do
if (io_status /= 0) then
    close(in_unit)
    call finish('Unable to find limits in input file.', is_dnd)
end if
backspace(in_unit)
read(in_unit, *, iostat = io_status) key, range_min(1), range_max(1), range_min(2), range_max(2)
if (io_status /= 0) then
    close(in_unit)
    call finish('Unable to read limits from input file.', is_dnd)
end if
write(*, fmt = '(A, 2X, F0.6, A, 2X, F0.6, A)') ' Limits of x (min, max):', range_min(1), ' A', range_max(1), ' A'
write(*, fmt = '(A, 2X, F0.6, A, 2X, F0.6, A)') ' Limits of y (min, max):', range_min(2), ' A', range_max(2), ' A'
write(*, *)

! Test conformance of error map DIMENSIONS
if (output_pdferr .or. output_opperr) then
    write(*, fmt = '(A)', advance = 'no') ' Validating error map dimensions ...'
    open(newunit = err_unit, file = file_error, status = 'old', action = 'read')
    io_status = 0
    key = ''
    do while ((io_status == 0) .and. (key /= 'DIMENSIONS'))
        read(err_unit, *, iostat = io_status) key
    end do
    if (io_status /= 0) then
        write(*, *) 'failed.'
        write(*, *) 'Unable to find grid DIMENSIONS. Ignoring error map.'
        write(*, *)
        output_pdferr = .false.
        output_opperr = .false.
        close(err_unit)
    end if
end if
if (output_pdferr .or. output_opperr) then
    backspace(err_unit)
    read(err_unit, *, iostat = io_status) key, err_data_num
    if (io_status /= 0) then
        write(*, *) 'failed.'
        write(*, *) 'Unable to read number of data points. Ignoring error map.'
        write(*, *)
        output_pdferr = .false.
        output_opperr = .false.
        close(err_unit)
    else if (any(err_data_num /= data_num)) then
        write(*, *) 'failed.'
        write(*, *) 'Mismatching number of data points. Ignoring error map.'
        write(*, *)
        output_pdferr = .false.
        output_opperr = .false.
        close(err_unit)
    end if
end if

! Test conformance of error map BOUNDS
if (output_pdferr .or. output_opperr) then
    rewind(err_unit)
    io_status = 0
    key = ''
    do while ((io_status == 0) .and. (key /= 'BOUNDS'))
        read(err_unit, *, iostat = io_status) key
    end do
    if (io_status /= 0) then
        write(*, *) 'failed.'
        write(*, *) 'Unable to find BOUNDS. Ignoring error map.'
        write(*, *)
        output_pdferr = .false.
        output_opperr = .false.
        close(err_unit)
    end if
end if
if (output_pdferr .or. output_opperr) then
    backspace(err_unit)
    read(err_unit, *, iostat = io_status) key, err_range_min(1), err_range_max(1), err_range_min(2), err_range_max(2)
    if (io_status /= 0) then
        write(*, *) 'failed.'
        write(*, *) 'Unable to read limits. Ignoring error map.'
        write(*, *)
        output_pdferr = .false.
        output_opperr = .false.
        close(err_unit)
    else if (any(abs(err_range_min - range_min) > epsilon(range_min)) &
            .or. any(abs(err_range_max - range_max) > epsilon(range_max))) then
        write(*, *) 'failed.'
        write(*, *) 'Mismatching limits. Ignoring error map.'
        write(*, *)
        output_pdferr = .false.
        output_opperr = .false.
        close(err_unit)
    end if
end if

! Check if error map is vital to job
if (.not. (output_pdf .or. output_pdferr .or. output_opp .or. output_opperr)) then
    write(*, *) 'No job to do. Exiting.'
    close(in_unit)
    call finish('', is_dnd)
end if

if (output_pdferr .or. output_opperr) then
    write(*, *) 'done.'
    write(*, *)
end if

! Calculation of constructing variables
inc = (range_max - range_min) / (data_num - 1)

! Reading of PDF data
rewind(in_unit)
io_status = 0
key = ''
write(*, fmt = '(A)', advance = 'no') ' Reading PDF data ...'
do while ((io_status == 0) .and. (key /= 'DATA'))
    read(in_unit, *, iostat = io_status) key
end do
if (io_status /= 0) then
    write(*, *) 'failed.'
    close(in_unit)
    call finish('Unable to find data in input file.', is_dnd)
end if
allocate(pdf(1:data_num(1), 1:data_num(2)))
read(in_unit, *, iostat = io_status) pdf
if (io_status /= 0) then
    write(*, *) 'failed.'
    call finish('Unable to read correct number of PDF data.', is_dnd)
end if
write(*, *) 'done.'
write(*, fmt = '(A, I0)') ' Total number of PDF data points: ', product(data_num)
close(in_unit)

! CALCULATION OF OPP

if (output_pdf .or. output_opp) write(*, fmt = '(/, A, /)') SEPARATOR  ! separates PDF from OPP

! Norm of PDF
pdf_0 = maxval(pdf)
pos_0 = maxloc(pdf)
if (output_opp .or. output_pdf) write(*, fmt = '(A, 1X, ES13.6, A)') ' Maximum of PDF:', pdf_0, ' A^-3'

if (output_opp) then
    ! Calculation of OPP for every data point
    write(*, *)
    write(*, fmt = '(A)', advance = 'no') ' Calculating OPP data ...'
    allocate(z(1:data_num(1), 1:data_num(2)))
    z = abs(K_B * temp * log(pdf / pdf_0))  ! z filled with OPP (absolute value to avoid negative zero)
    where (isnan(z)) z = INFINITE_OPP
    write(*, *) 'done.'

    ! Store OPP in temporary file to reduce memory usage
    open(newunit = opp_unit, status = 'scratch', access = 'stream', action = 'readwrite')
    write(*, fmt = '(A)', advance = 'no') ' Temporarily storing OPP data ...'
    write(opp_unit) z
    deallocate(z)
    write(*, *) 'done.'
end if

! CALCULATION OF ERROR DATA

! Reading of error map
if (output_pdferr .or. output_opperr) then
    write(*, fmt = '(/, A, /)') SEPARATOR  ! separating error map part
    rewind(err_unit)
    io_status = 0
    key = ''
    write(*, fmt = '(A)', advance = 'no') ' Reading error map ...'
    do while ((io_status == 0) .and. (key /= 'DATA'))
        read(err_unit, *, iostat = io_status) key
    end do
    if (io_status /= 0) then
        write(*, *) 'failed.'
        write(*, *) 'Unable to find DATA statement. Ignoring error map.'
        write(*, *)
        close(err_unit)
        output_pdferr = .false.
        output_opperr = .false.
    end if
end if

! Check if error map is vital to job
if (.not. (output_pdf .or. output_pdferr .or. output_opp .or. output_opperr)) then
    write(*, *) 'No job to do. Exiting.'
    call finish('', is_dnd)
end if

if (output_pdferr .or. output_opperr) then
    allocate(z(1:err_data_num(1), 1:err_data_num(2)))
    allocate(opp_low_err(1:err_data_num(1), 1:err_data_num(2)))
    read(err_unit, *, iostat = io_status) z  ! z filled with PDF error
    if (io_status /= 0) then
        write(*, *) 'failed.'
        write(*, *) 'Unable to read correct number of PDF error data.'
        write(*, *) 'Ignoring error map.'
        output_pdferr = .false.
        output_opperr = .false.

        ! Check if error map is vital to job
        if (.not. (output_pdf .or. output_pdferr .or. output_opp .or. output_opperr)) then
            write(*, *)
            write(*, *) 'No job to do. Exiting.'
            call finish('', is_dnd)
        end if
    else
        z = abs(z)  ! errors from Monte-Carlo approach may be negative
        write(*, *) 'done.'
        write(*, *)
    end if
    close(err_unit)
end if

! Store PDF error in temporary file to reduce memory usage
if (output_pdferr) then
    open(newunit = pdferr_unit, status = 'scratch', access = 'stream', action = 'readwrite')
    write(*, fmt = '(A)', advance = 'no') ' Temporarily storing PDF uncertainty data ...'
    write(pdferr_unit) z
    write(*, *) 'done.'
end if

if (output_opperr) then

    ! Error of maximum
    err_pdf_0 = z(pos_0(1), pos_0(2))
    write(*, fmt = '(A, 1X, ES13.6, A)') ' Uncertainty at maximum of PDF:', err_pdf_0, ' A^-3'

    ! Calculation of error in OPP for every data point
    write(*, fmt = '(A)', advance = 'no') ' Calculating OPP uncertainties ...'
    opp_low_err = -1 * K_B * temp * log((1 + z/pdf) / (1 - err_pdf_0/pdf_0))
    z = -1 * K_B * temp * log((1 - z/pdf) / (1 + err_pdf_0/pdf_0))  ! z filled with upper OPP error
    where (.not. (pdf > 0.0) .or. isnan(z)) z = INFINITE_OPP
    where (.not. (pdf > 0.0) .or. isnan(opp_low_err)) opp_low_err = -1 * INFINITE_OPP
    write(*, *) 'done.'
end if

! WRITING OF OUTPUT FILE

! Writing introductory comment
write(*, fmt = '(/, A, /)') SEPARATOR  ! separates calculation from output information
write(*, fmt = '(A)', advance = 'no') ' Writing output file ...'
open(newunit = out_unit, file = file_output, status = 'replace', action = 'write')
write(out_unit, fmt = '(A)') '# ASCII output generated by CalcOPP (PDF2OPP_2D) ' // VERSION
write(out_unit, fmt = '(A)', advance = 'no') '# A: Angstrom'
if (output_pdferr) write(out_unit, fmt = '(A)', advance = 'no') '; s: standard deviation'
if (output_opperr) write(out_unit, fmt = '(A)', advance = 'no') '; u+, u-: upper and lower uncertainty'
write(out_unit, *)
write(out_unit, fmt = '(A)', advance = 'no') '#    x/A           y/A     '
if (output_pdf) write(out_unit, fmt = '(A)', advance = 'no') '    PDF/A^-3  '
if (output_pdferr) write(out_unit, fmt = '(A)', advance = 'no') '  s(PDF)/A^-3 '
if (output_opp) write(out_unit, fmt = '(A)', advance = 'no') '     OPP/eV   '
if (output_opperr) write(out_unit, fmt = '(A)', advance = 'no') '   u+(OPP)/eV    u-(OPP)/eV '
write(out_unit, *)

! Preparing scratch data
if (output_opp) rewind(opp_unit)
if (output_pdferr) rewind(pdferr_unit)

! Writing actual data lines
do j = 1, data_num(2)
    do i = 1, data_num(1)
        write(out_unit, fmt = '(ES13.6, 1X, ES13.6)', advance = 'no') range_min(1) + (i - 1) * inc(1), &
                                                                      range_min(2) + (j - 1) * inc(2)
        if (output_pdf) write(out_unit, fmt = '(1X, ES13.6)', advance = 'no') pdf(i, j)
        if (output_pdferr) write(out_unit, fmt = '(1X, ES13.6)', advance = 'no') get_scratch(pdferr_unit, is_dnd)
        if (output_opp) write(out_unit, fmt = '(1X, ES13.6)', advance = 'no') get_scratch(opp_unit, is_dnd)
        if (output_opperr) write(out_unit, fmt = '(2(1X, ES13.6))', advance = 'no') z(i, j), opp_low_err(i, j)
        write(out_unit, *)
    end do
end do
endfile(out_unit)
close(out_unit)
write(*, *) 'done.'

! Clean exit
deallocate(pdf)
if (allocated(z)) deallocate(z)
if (allocated(opp_low_err)) deallocate(opp_low_err)
if (output_opp) close(opp_unit)
if (output_pdferr) close(pdferr_unit)

write(*, fmt = '(/, A, /)') SEPARATOR ! separates output from goodbye
write(*, *) '"This *does* compute!" - BMO'
call finish('', is_dnd)


contains


! Get a value from a stream-mode scratch file
function get_scratch(unit_number, is_dnd)

    implicit none
    integer, intent(in) :: unit_number  ! Number of input unit to get data from
    logical, intent(in) :: is_dnd       ! True if program invoked via drag and drop
    real                :: get_scratch  ! Value got from scratch file
    integer             :: io_status    ! Status of file I/O

    read(unit_number, iostat = io_status) get_scratch
    if (io_status /= 0) call finish('Unable to read from scratch.', is_dnd)

end function get_scratch


! Add a different extension to a file name
function new_ext(file_name, extension)

    implicit none
    character(len = *), intent(in)  :: file_name  ! File to add new extension to
    character(len = *), intent(in)  :: extension  ! New extension to add
    character(len = 256)            :: new_ext    ! File name with new extension
    integer                         :: dot_pos    ! Position of extension dot

    dot_pos = scan(trim(file_name), '.', back = .true.)
    if (dot_pos > 0) then
        new_ext = file_name(1:dot_pos - 1) // extension
    else
        new_ext = trim(file_name) // extension
    end if

end function new_ext


end program pdf2opp_2d


! Exit program
subroutine finish(error_message, is_drag_and_drop)

    implicit none
    character(len = *), intent(in) :: error_message     ! Error message (empty for no error)
    logical,            intent(in) :: is_drag_and_drop  ! True if program invoked via drag and drop
    intrinsic sleep

    write(*, *)
    if (error_message /= '') then
        write(*, *) error_message
        write(*, *)
    end if
    if (is_drag_and_drop) then
        write(*, *) 'Terminating in 5 s ...'
        call sleep(5)
        write(*, *)
    end if
    if (error_message /= '') then
        error stop error_message
    else
        stop
    end if

end subroutine finish


! Greeting text
subroutine print_greeting(ver)

    implicit none
    character(len = *), intent(in) :: ver  ! Program version

    write(*, *) 'PDF2OPP_2D ' // ver // ' - Calculation of 2D OPP from PDF Data (JANA2006 STF Format)'
    write(*, *) 'Copyright (c) 2020  Dr. Dennis Wiedemann (MIT License, see LICENSE file)'

end subroutine print_greeting


! Help text
subroutine print_help()

    write(*, *) 'Usage: pdf2opp_2d [OPTIONS]'
    write(*, *)
    write(*, *) 'Options:'
    write(*, *)
    write(*, *) '-h                Prints this usage information and exits.'
    write(*, *) '-v                Prints the version number and exits.'
    write(*, *) '-i <file name>    Specifies the input file.'
    write(*, *) '-o <file name>    Specifies the output file.'
    write(*, *) '-e <file name>    Specifies the error map file.'
    write(*, *) '-t <T/K>          Specifies the temperature in Kelvin'
    write(*, *) '                  (if not provided, extraction from *.m90 will be tried).'
    write(*, *) '-pdf              Includes PDF data in output.'
    write(*, *) '-pdferr           Includes PDF error map in output.'
    write(*, *) '-opp              Calculates and includes OPP data in output.'
    write(*, *) '-opperr           Calculates and includes OPP error map in output.'
    write(*, *)
    write(*, *) 'If none of the last four options is included, all data will be calculated'
    write(*, *) 'and put out.'

end subroutine print_help
