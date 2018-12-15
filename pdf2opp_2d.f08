program pdf2opp_2d

!   CalcOPP 2.0.0 - Calculation of Effective One-Particle Potentials
!   PDF2OPP_2D - Subroutines for Calculation from 2D PDF Data (JANA2006 STF Format)
!   Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)

implicit none
character(len = 256)              :: file_input, file_output, file_error, file_m90         ! Names of handled files
character(len = 256)              :: key                                                   ! Key read from input file
character(len = 256)              :: line                                                  ! Input line read from *.m90 file
character(len = 256)              :: arg                                                   ! Command-line argument
character(len = 256)              :: T_string                                              ! Temperature as string
character(len = 256)              :: comment                                               ! Header comment in output file
character(len = 256)              :: output_line                                           ! Line to write into output file
character(len = 256)              :: output_addition                                       ! Temporary store for numerical output
integer                           :: i, j                                                  ! Counters
integer                           :: data_x, data_y, err_data_x, err_data_y                ! Number of data points in x/y direction
                                                                                           !   in input/error file
integer                           :: ext_dot                                               ! Position of extension dot in file name
integer                           :: in_unit, out_unit, err_unit, m90_unit, opp_unit, &
                                     pdferr_unit                                           ! Unit number for file access
integer                           :: io_status                                             ! Status of the file I/O                             !
integer                           :: remain_vals                                           ! Number of values in incomplete set
integer, dimension(2)             :: xy_0                                                  ! Position of maximum PDF
real                              :: x_min, x_max, y_min, y_max, &                         ! Minimal/maximal x/y values in
                                     err_x_min, err_x_max, err_y_min, err_y_max            !   input/error file
real                              :: T                                                     ! Temperature in Kelvin
real                              :: pdf_0, err_pdf_0                                      ! Maximum input/error PDF
real                              :: x_inc, y_inc                                          ! Increment in x/y direction
real, dimension(:),   allocatable :: z_stack                                               ! Temporary stack for input values
real, dimension(:,:), allocatable :: z                                                     ! OPP values as x * y matrix
real, dimension(:,:), allocatable :: pdf                                                   ! PDF values as x * y matrix
logical                           :: exists_input, exists_error, exists_m90                ! Flags for existence of files
logical                           :: output_pdf, output_pdferr, output_opp, output_opperr  ! Flags controlling data output
logical                           :: is_dnd                                                ! Flag for drag and drop

character(len = *), parameter     :: SEPARATOR = ' ' // repeat('=', 40)                    ! Visual separator for standard output
character(len = *), parameter     :: version = '2.0.0'                                     ! Program version
real, parameter                   :: K_B = 8.617330E-5                                     ! Boltzmann constant in eV/K
real, parameter                   :: INFINITE_OPP = 1.0E6                                  ! Pseudo-infinite OPP in eV


! ACQUIRING NECESSARY INPUT

! Parsing command line arguments
file_input = ''
file_output = ''
file_error = ''
T = -1.
output_pdf = .false.
output_pdferr = .false.
output_opp = .false.
output_opperr = .false.
is_dnd = .false.

i = 1
do while (i <= command_argument_count())
    call get_command_argument(i, arg)
    select case (arg)
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
                call get_command_argument(i, T_string)
                read(T_string, '(E12.5)') T
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
            write(*, *) version
            call finish('', is_dnd)
        case default
            if (index(arg, '-') == 1) then
                call print_help()
                call finish('Unrecognized command-line option: ' // trim(arg), is_dnd)
            else
                if (file_input == '') then
                    call get_command_argument(i, file_input)
                    is_dnd = .true.
                end if
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

call print_greeting(version)
write(*, fmt = '(/, A, /)') SEPARATOR  ! separates greeting from checking

! Check if input file name is valid (vital)
if (file_input == '') then
    call print_help()
    call finish('No input file name provided.', is_dnd)
else
    exists_input = .false.
    inquire(file = file_input, exist = exists_input)
    if (.not. exists_input) then
        call finish('No valid input file name provided.', is_dnd)
    end if
end if

! Automatically set output file name, if not provides
if (file_output == '') then
    file_output = file_input
    ext_dot = index(file_output, '.', .true.)  ! check for file extension
    if (ext_dot > 0) then  ! crop file extension, if existing
        file_output(ext_dot:len_trim(file_output)) = repeat(' ', len_trim(file_output) - ext_dot)
    end if
    file_output = trim(file_output) // '_opp.asc'
end if

! Automatically set error map name, if not provided and necessary, and check existence
if ((output_pdferr) .or. (output_opperr)) then
    if (file_error == '') then
        file_error = file_input
        ext_dot = index(file_error, '.', .true.)  ! check for file extension
        if (ext_dot > 0) then  ! crop file extension, if existing
            file_error(ext_dot:len_trim(file_error)) = repeat(' ', len_trim(file_error) - ext_dot)
        end if
        file_error = trim(file_error) // '_err.stf'
    end if
    exists_error = .false.
    inquire(file = file_error, exist = exists_error)
    if (.not. exists_error) then
        write(*, *) 'Error map not found. PDF/OPP error will not be included in output.'
        output_pdferr = .false.
        output_opperr = .false.
    end if
end if

! Temperature extraction from *.m90
if ((T <= 0.) .and. (output_opp .or. output_opperr)) then
    write(*, fmt = '(A)', advance = 'no') ' Temperature not given. Probing *.m90 ...'

    ! Construct file name of *.m90
    file_m90 = file_input
    ext_dot = index(file_m90, '.', .true.)  ! check for file extension
    if (ext_dot > 0) then  ! crop file extension, if existing
        file_m90(ext_dot:len_trim(file_m90)) = repeat(' ', len_trim(file_m90) - ext_dot)
    end if
    file_m90 = trim(file_m90) // '.m90'

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
            line = line(index(line, 'datcolltemp'):)
            read(line(12:), *) T
            write(*, *)
            write(*, fmt = '(A, F0.4, A)') ' Temperature: T = ', T, ' K'
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
read(in_unit, *, iostat = io_status) key, data_x, data_y
write(*, fmt = '(A, 3X, I0, 3X, I0)') ' Numbers of data points (x, y):', data_x, data_y
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
read(in_unit, *, iostat = io_status) key, x_min, x_max, y_min, y_max
write(*, fmt = '(A, 3X, F0.8, A, 3X, F0.8, A)') ' Limits of x (min, max):', x_min, ' A', x_max, ' A'
write(*, fmt = '(A, 3X, F0.8, A, 3X, F0.8, A)') ' Limits of y (min, max):', y_min, ' A', y_max, ' A'
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
    read(err_unit, *, iostat = io_status) key, err_data_x, err_data_y
    if ((err_data_x /= data_x) .or. (err_data_y /= data_y)) then
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
    read(err_unit, *, iostat = io_status) key, err_x_min, err_x_max, err_y_min, err_y_max
    if ((abs(err_x_min - x_min) > epsilon(x_min)) .or. (abs(err_x_max - x_max) > epsilon(x_max)) .or. &
       (abs(err_y_min - y_min) > epsilon(y_min)) .or. (abs(err_y_max - y_max) > epsilon(y_max))) then
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
x_inc = (x_max - x_min) / (data_x - 1)
y_inc = (y_max - y_min) / (data_y - 1)
remain_vals = mod(data_x * data_y, 8)

! Reading of PDF data into temporary stack
allocate(z_stack(1:data_x * data_y))
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
do i = 1, int((data_x * data_y) / 8.0)  ! Reading lines with eight data points
    read(in_unit, *, iostat = io_status) z_stack(8 * i - 7:8 * i)
end do
if (remain_vals > 0) then  ! Reading remaining incomplete line if present
    read(in_unit, *, iostat = io_status) z_stack(8 * i - 7:8 * i - 8 + remain_vals)
end if
write(*, *) 'done.'
write(*, fmt = '(A, I0)') ' Total number of PDF data points: ', 8 * (i - 1) + remain_vals
close(in_unit)

! Transfer of PDF data from stack to ordered matrix
allocate(pdf(1:data_x, 1:data_y))
pdf = reshape(z_stack, (/ data_x, data_y /))
deallocate(z_stack)

! CALCULATION OF OPP

if (output_pdf .or. output_opp) write(*, fmt = '(/, A, /)') SEPARATOR  ! separates PDF from OPP

! Norm of PDF
pdf_0 = maxval(pdf)
xy_0 = maxloc(pdf)
if (output_opp .or. output_pdf) then
    write(*, fmt = '(A, 3X, F0.8, A)') ' Maximum of PDF:', pdf_0, ' A^-3'
end if

! Calculation of OPP for every data point
if (output_opp) then
    write(*, *)
    write(*, fmt = '(A)', advance = 'no') ' Calculating OPP data ...'
    allocate(z(1:data_x, 1:data_y))
    z = -1 * K_B * T * log(pdf / pdf_0)
    where (isnan(z)) z = INFINITE_OPP
    write(*, *) 'done.'

    ! Store OPP in temporary file to reduce memory usage
    open(newunit = opp_unit, status = 'scratch', access = 'sequential', action = 'readwrite')
    write(*, fmt = '(A)', advance = 'no') ' Temporarily storing OPP data ...'
    do j = 1, data_y
        do i = 1, data_x
            write(opp_unit, fmt = '(2X, ES13.6)') z(i, j)
        end do
    end do
    deallocate(z)
    write(*, *) 'done.'
end if

! CALCULATION OF ERROR DATA

! Reading of error map into temporary stack
if (output_pdferr .or. output_opperr) then
    write(*, fmt = '(/, A, /)') SEPARATOR  ! separating error map part
    allocate(z_stack(1:data_x * data_y))
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
    do i = 1, int((data_x * data_y)/8.)  ! Reading lines with eight data points
        read(err_unit, *, iostat = io_status) z_stack(8 * i - 7:8 * i)
    end do
    if (remain_vals > 0) then  ! Reading remaining incomplete line if present
        read(err_unit, *, iostat = io_status) z_stack(8 * i - 7:8 * i - 8 + remain_vals)
    end if
    write(*, *) 'done.'
    write(*, fmt = '(A, I0)') ' Total number of error data points: ', 8 * (i - 1) + remain_vals
    write(*, *)
    close(err_unit)
end if

! Transfer of PDF error data from stack to ordered matrix
if (output_pdferr .or. output_opperr) then
    allocate(z(1:data_x, 1:data_y))
    z = reshape(z_stack, (/ data_x, data_y /))  ! z filled with PDF error data
    deallocate(z_stack)
end if

! Store PDF error in temporary file to reduce memory usage
if (output_pdferr) then
    open(newunit = pdferr_unit, status = 'scratch', access = 'sequential', action = 'readwrite')
    write(*, fmt = '(A)', advance = 'no') ' Temporarily storing PDF error data ...'
    do j = 1, data_y
        do i = 1, data_x
            write(pdferr_unit,fmt = '(ES13.6)') z(i, j)
        end do
    end do
    write(*, *) 'done.'
end if

! Error of maximum
if (output_opperr) then
    err_pdf_0 = z(xy_0(1), xy_0(2))
    write(*, fmt = '(A, 3X, F0.8, A)') ' Error at maximum of PDF:', err_pdf_0, ' A^-3'
end if

! Calculation of error in OPP for every data point
if (output_opperr) then
    write(*, fmt = '(A)', advance = 'no') ' Calculating OPP error data ...'
    do j = 1, data_y
        do i = 1, data_x
            if (pdf(i, j) > 0) then
                z(i, j) = K_B * T * sqrt((err_pdf_0 / pdf_0) ** 2 + (z(i, j) / pdf(i, j)) ** 2)
            else
                z(i, j) = INFINITE_OPP
            end if
        end do
    end do  ! z filled with error in OPP
    write(*, *) 'done.'
end if

! WRITING OF OUTPUT FILE

! Writing introductory comment
comment = '# Format: x/A, y/A'
if (output_pdf) then
    comment = trim(comment) // ', PDF/A^-3'
end if
if (output_pdferr) then
    comment = trim(comment) // ', sigma(PDF)/A^-3'
end if
if (output_opp) then
    comment = trim(comment) // ', OPP/eV'
end if
if (output_opperr) then
    comment = trim(comment) // ', sigma(OPP)/eV'
end if
write(*, fmt = '(/, A, /)') SEPARATOR  ! separates calculation from output information
write(*, fmt = '(A)', advance = 'no') ' Writing output file ...'
open(newunit = out_unit, file = file_output, status = 'replace', action = 'write')
write(out_unit, *) '# ASCII output generated by CalcOPP'
write(out_unit, *) trim(comment)

! Preparing scratch data
if (output_opp) then
    rewind(opp_unit)
end if
if (output_pdferr) then
    rewind(pdferr_unit)
end if

! Writing actual data lines
do j = 1, data_y
    do i = 1, data_x
        write(output_line, fmt = '(2X, ES13.6, 2X, ES13.6)') x_min + (i - 1) * x_inc, y_min + (j - 1) * y_inc
        if (output_pdf) then
            write(output_addition, fmt = '(2X, ES13.6)') pdf(i, j)
            output_line = trim(output_line) // output_addition
        end if
        if (output_pdferr) then
            read(pdferr_unit, *) output_addition
            output_line = trim(output_line) // '  ' // output_addition
        end if
        if (output_opp) then
            read(opp_unit, *) output_addition
            output_line = trim(output_line) // '  ' // output_addition
        end if
        if (output_opperr) then
            write(output_addition, fmt = '(2X, ES13.6)') z(i, j)
            output_line = trim(output_line) // output_addition
        end if
        write(out_unit, *) trim(output_line)
    end do
end do
endfile(out_unit)
close(out_unit)
write(*, *) 'done.'
write(*, *) 'Output written to: ', trim(file_output)

! Clean exit
deallocate(pdf)
if (allocated(z)) then
    deallocate(z)
end if
if (output_opp) then
    close(opp_unit)
end if
if (output_pdferr) then
    close(pdferr_unit)
end if

write(*, fmt = '(/, A, /)') SEPARATOR ! separates output from goodbye
write(*, *) '"This *does* compute!" - BMO'
call finish('', is_dnd)

contains

elemental function nan_to_finite(x, finite_value)

    implicit none
    real              :: nan_to_finite  ! finite value
    real, intent(in)  :: x              ! variable to make finite
    real, intent(in)  :: finite_value   ! value to assign to NaNs

    if (isnan(x)) then
        nan_to_finite = finite_value
    else
        nan_to_finite = x
    end if

end function nan_to_finite

end program pdf2opp_2d


! Exiting program
subroutine finish(error_message, is_drag_and_drop)

    implicit none
    character(*), intent(in) :: error_message     ! Error message (empty for no error)
    logical,      intent(in) :: is_drag_and_drop  ! True if program invoked via drag and drop
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
    character(*), intent(in) :: ver  ! Program version

    write(*, *) 'PDF2OPP_2D ' // ver // ' - Calculation of 2D OPP from PDF Data (JANA2006 STF Format)'
    write(*, *) 'Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)'

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


! TODO (Dennis#1#): Use elemental subroutines for array (also error processing, mask?)
! TODO (Dennis#1#): Make both scratch files binary, if possible (store z, then read sequentially)
! TODO (Dennis#1#): Check nifty possibility to read directly into z instead of z_stack
! TODO (Dennis#1#): Delete elemental subroutine(s)
! TODO (Dennis#1#): Conversion function instead of extra variable for str-to-num
