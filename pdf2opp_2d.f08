program pdf2opp_2d

!   CalcOPP 2.0.0 - Calculation of Effective One-Particle Potentials
!   PDF2OPP_2D - Subroutines for Calculation from 2D PDF Data (JANA2006 STF Format)
!   Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)

implicit none
character(256)                      :: file_input, file_output, file_error, file_m90, key, line
character(256)                      :: arg, T_string, comment, output_line, output_addition
character(51), parameter            :: separator = ' ======================================='
integer                             :: i, j, data_x, data_y, ext_dot, io_status
integer                             :: remain_vals, err_data_x, err_data_y
integer, dimension(2)               :: xy_0
real                                :: x_min, x_max, y_min, y_max, T, pdf_0, x_inc, y_inc
real                                :: err_x_min, err_x_max, err_y_min, err_y_max, err_pdf_0
real, dimension(:), allocatable     :: z_stack
real, dimension(:,:), allocatable   :: z, pdf
logical                             :: exists_input, exists_error, exists_m90
logical                             :: output_pdf, output_pdferr, output_opp, output_opperr
real, parameter                     :: k = 8.6173332621451774336636593340806E-2     ! Boltzmann constant in meV/K

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

i = 1
do while (i <= command_argument_count())
    call get_command_argument(i, arg)
    select case (arg)
        case ('-i')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_input)
            else
                error stop 'Used -i, but no input file name provided.'
            end if
            i = i + 1
        case ('-o')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_output)
            else
                error stop 'Used -o, but no output file name provided.'
            end if
            i = i + 1
        case ('-e')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_error)
            else
                error stop 'Used -e, but no error map name provided.'
            end if
            i = i + 1
        case ('-t')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, T_string)
                read(T_string, '(E12.5)') T
            else
                error stop 'Used -t, but no temperature provided.'
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
            stop
        case default
            if (index(arg, '-') == 1) then
                write(*,*) 'Unrecognized command-line option: ', arg
                call print_help()
                stop
            else
                if (file_input == '') then
                    call get_command_argument(i, file_input)
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

call print_greeting()
write(*, fmt = '(/,A,/)') separator   ! separates greeting from checking

! Check if input file name is valid (vital)
if (file_input == '') then
    error stop 'No input file name provided.'
else
    exists_input = .false.
    inquire(file = file_input, exist = exists_input)
    if (.not. exists_input) then
        error stop 'No valid input file name provided.'
    end if
end if

! Automatically set output file name, if not provides
if (file_output == '') then
    file_output = file_input
    ext_dot = index(file_output, '.', .true.)    ! check for file extension
    if (ext_dot > 0) then                        ! crop file extension, if existing
        file_output(ext_dot:len_trim(file_output)) = repeat(' ', len_trim(file_output) - ext_dot)
    end if
    file_output = trim(file_output) // '_opp.asc'
end if

! Automatically set error map name, if not provided and necessary, and check existence
if ((output_pdferr) .or. (output_opperr)) then
    if (file_error == '') then
        file_error = file_input
        ext_dot = index(file_error, '.', .true.)     ! check for file extension
        if (ext_dot > 0) then                        ! crop file extension, if existing
            file_error(ext_dot:len_trim(file_error)) = repeat(' ', len_trim(file_error) - ext_dot)
        end if
        file_error = trim(file_error) // '_err.stf'
    end if
    exists_error = .false.
    inquire(file = file_error, exist = exists_error)
    if (.not. exists_error) then
        write(*,*) 'Error map not found. PDF/OPP error will not be included in output.'
        output_pdferr = .false.
        output_opperr = .false.
    end if
end if

! Temperature extraction from *.m90
if ((T <= 0.) .and. (output_opp .or. output_opperr)) then
    write(*,fmt='(A)',advance='no') 'Temperature not given. Probing *.m90 ...'

    ! Construct file name of *.m90
    file_m90 = file_input
    ext_dot = index(file_m90, '.', .true.)     ! check for file extension
    if (ext_dot > 0) then                      ! crop file extension, if existing
        file_m90(ext_dot:len_trim(file_m90)) = repeat(' ', len_trim(file_m90) - ext_dot)
    end if
    file_m90 = trim(file_m90) // '.m90'

    ! Try automatic extraction from *.m90
    exists_m90 = .false.
    inquire(file = file_m90, exist = exists_m90)
    if (exists_m90) then
        write(*, fmt = '(A)', advance = 'no') ' found.'
        open(90, file = file_m90, status = 'old', action = 'read')
        line = ''

        ! Search for keyword "datcolltemp"
        io_status = 0
        do while ((io_status == 0) .and. (index(line, 'datcolltemp ') == 0))
            read(90, fmt = '(A256)', iostat = io_status) line
        end do
        close(90)

        ! Try to read in following value
        if (io_status == 0) then
            line = line(index(line, 'datcolltemp'):)
            read(line(12:),*) T
            write(*,*) 'Temperature: T = ', T, ' K.'
        else
            error stop 'No valid temperature found in *.m90.'
        end if
    else
        error stop '*.m90 not found.'
    end if
end if

write(*,*) 'Necessary input data acquired.'
write(*, fmt = '(/,A,/)') separator    ! separates checking from calculation

! PARSING INPUT FILE(S)

! Search for DIMENSIONS
open(20,file = file_input,status = 'old',action = 'read')
io_status = 0
key = ''
do while ((io_status == 0) .and. (key /= 'DIMENSIONS'))
    read(20,*,iostat=io_status) key
end do
if (io_status /= 0) then
    close(20)
    error stop 'Unable to find grid dimensions in input file.'
end if
backspace(20)
read(20,*,iostat=io_status) key, data_x, data_y
write(*,*) 'Number of data points (x, y): ', data_x, data_y; write(*,*);

! Search for BOUNDS
rewind(20)
io_status = 0
key = ''
do while ((io_status == 0) .and. (key /= 'BOUNDS'))
    read(20,*,iostat=io_status) key
end do
if (io_status /= 0) then
    close(20)
    error stop 'Unable to find limits in input file.'
end if
backspace(20)
read(20,*,iostat=io_status) key, x_min, x_max, y_min, y_max
write(*,*) 'Limits of x (min, max): ', x_min, x_max
write(*,*) 'Limits of y (min, max): ', y_min, y_max; write(*,*)

! Test conformance of error map DIMENSIONS
if (output_pdferr .or. output_opperr) then
    write(*, fmt = '(A)', advance = 'no') ' Validating error map dimensions ...'
    open(25,file = file_error,status = 'old',action = 'read')
    io_status = 0
    key = ''
    do while ((io_status == 0) .and. (key /= 'DIMENSIONS'))
        read(25,*,iostat=io_status) key
    end do
    if (io_status /= 0) then
        write(*,*) 'failed.'
        write(*,*) 'Unable to find grid dimensions as defined by DIMENSIONS. Ignoring error map.'; write(*,*)
        output_pdferr = .false.
        output_opperr = .false.
        close(25)
    end if
end if
if (output_pdferr .or. output_opperr) then
    backspace(25)
    read(25,*,iostat=io_status) key, err_data_x, err_data_y
    if ((err_data_x /= data_x) .or. (err_data_y /= data_y)) then
        write(*,*) 'failed.'
        write(*,*) 'Mismatching number of data points. Ignoring error map.'; write(*,*)
        output_pdferr = .false.
        output_opperr = .false.
        close(25)
    end if
end if

! Test conformance of error map BOUNDS
if (output_pdferr .or. output_opperr) then
    rewind(25)
    io_status = 0
    key = ''
    do while ((io_status == 0) .and. (key /= 'BOUNDS'))
        read(25,*,iostat=io_status) key
    end do
    if (io_status /= 0) then
        write(*,*) 'failed.'
        write(*,*) 'Unable to find limits as defined by BOUNDS. Ignoring error map.'; write(*,*)
        output_pdferr = .false.
        output_opperr = .false.
        close(25)
    end if
end if
if (output_pdferr .or. output_opperr) then
    backspace(25)
    read(25,*,iostat=io_status) key, err_x_min, err_x_max, err_y_min, err_y_max
    if ((abs(err_x_min - x_min) > epsilon(x_min)) .or. (abs(err_x_max - x_max) > epsilon(x_max)) .or. &
       (abs(err_y_min - y_min) > epsilon(y_min)) .or. (abs(err_y_max - y_max) > epsilon(y_max))) then
        write(*,*) 'failed.'
        write(*,*) 'Mismatching limits. Ignoring error map.'; write(*,*)
        output_pdferr = .false.
        output_opperr = .false.
        close(25)
    end if
end if

! Check if error map is vital to job
if (.not. (output_pdf .or. output_pdferr .or. output_opp .or. output_opperr)) then
    write(*,*); write(*,*) 'No job to do. Exiting.'
    close(20)
    stop
end if

if (output_pdferr .or. output_opperr) then
    write(*,*) 'done.'; write(*,*)
end if

! Calculation of constructing variables
x_inc = (x_max - x_min) / (data_x - 1)
y_inc = (y_max - y_min) / (data_y - 1)
remain_vals = mod(data_x * data_y,8)

! Reading of PDF data into temporary stack
allocate(z_stack(1:data_x * data_y))
rewind(20)
io_status = 0
key = ''
write(*, fmt = '(A)', advance = 'no') ' Reading PDF data ...'
do while ((io_status == 0) .and. (key /= 'DATA'))
    read(20,*,iostat=io_status) key
end do
if (io_status /= 0) then
    write(*,*) 'failed.'
    close(20)
    error stop 'Unable to find data in input file.'
end if
do i = 1, int((data_x * data_y)/8.)    ! Reading lines with eight data points
    read(20,*,iostat=io_status) z_stack(8 * i - 7:8 * i)
end do
if (remain_vals > 0) then              ! Reading remaining incomplete line if present
    read(20,*,iostat=io_status) z_stack(8 * i - 7:8 * i - 8 + remain_vals)
end if
write(*,*) 'done.'
write(*,*) 'Total of PDF data points found: ', 8 * i - 8 + remain_vals
close(20)

! Transfer of PDF data from stack to ordered matrix
allocate(pdf(1:data_x,1:data_y))
pdf = reshape(z_stack, (/ data_x, data_y /))
deallocate(z_stack)

! CALCULATION OF OPP

write(*, fmt = '(/,A,/)') separator  ! separates PDF from OPP

! Norm of PDF
pdf_0 = maxval(pdf)
xy_0 = maxloc(pdf)
if (output_opp .or. output_pdf) then
    write(*,*) 'Maximum of PDF: ', pdf_0; write(*,*)
end if

! Calculation of OPP for every data point
if (output_opp) then
    write(*, fmt = '(A)', advance = 'no') ' Calculating OPP data ...'
    allocate(z(1:data_x,1:data_y))
    z = pdf/pdf_0       ! z filled with normalized PDF data
    do i = 1, data_x
        do j = 1, data_y
            if (z(i,j) > 0) then
                z(i,j) = -1 * k * T * log(z(i,j))
            else
                z(i,j) = 1.0E+9    ! huge OPP for zero or negative PDF
            end if
        end do
    end do          ! z filled with OPP data
    write(*,*) 'done.'

    ! Store OPP in temporary file to reduce memory usage
    open(40,status = 'scratch',access = 'sequential',action = 'readwrite')
    write(*, fmt = '(A)', advance = 'no') ' Temporarily storing OPP data ...'
    do i = 1, data_x
        do j = 1, data_y
            write(40,fmt = '(2X,ES13.6)') z(i,j)
        end do
    end do
    deallocate(z)
    write(*,*) 'done.'
end if

! CALCULATION OF ERROR DATA

! Reading of error map into temporary stack
if (output_pdferr .or. output_opperr) then
    write(*, fmt = '(/,A,/)') separator   ! separating error map part
    allocate(z_stack(1:data_x * data_y))
    rewind(25)
    io_status = 0
    key = ''
    write(*, fmt = '(A)', advance = 'no') ' Reading error map ...'
    do while ((io_status == 0) .and. (key /= 'DATA'))
        read(25,*,iostat=io_status) key
    end do
    if (io_status /= 0) then
        write(*,*) 'failed.'
        write(*,*) 'Unable to find DATA statement. Ignoring error map.'; write(*,*)
        close(25)
        output_pdferr = .false.
        output_opperr = .false.
    end if
end if

! Check if error map is vital to job
if (.not. (output_pdf .or. output_pdferr .or. output_opp .or. output_opperr)) then
    write(*,*); write(*,*) 'No job to do. Exiting.'
    stop
end if

if (output_pdferr .or. output_opperr) then
    do i = 1, int((data_x * data_y)/8.)    ! Reading lines with eight data points
        read(25,*,iostat=io_status) z_stack(8 * i - 7:8 * i)
    end do
    if (remain_vals > 0) then              ! Reading remaining incomplete line if present
        read(25,*,iostat=io_status) z_stack(8 * i - 7:8 * i - 8 + remain_vals)
    end if
    write(*,*) 'done.'
    write(*,*) 'Total of error data points found: ', 8 * i - 8 + remain_vals; write(*,*)
    close(25)
end if

! Transfer of PDF error data from stack to ordered matrix
if (output_pdferr .or. output_opperr) then
    allocate(z(1:data_x,1:data_y))
    z = reshape(z_stack, (/ data_x, data_y /))  ! z filled with PDF error data
    deallocate(z_stack)
end if

! Store PDF error in temporary file to reduce memory usage
if (output_pdferr) then
    open(41,status = 'scratch',access = 'sequential',action = 'readwrite')
    write(*, fmt = '(A)', advance = 'no') ' Temporarily storing PDF error data ...'
    do i = 1, data_x
        do j = 1, data_y
            write(41,fmt = '(ES13.6)') z(i,j)
        end do
    end do
    write(*,*) 'done.'
end if

! Error of maximum
if (output_opperr) then
    err_pdf_0 = z(xy_0(1),xy_0(2))
    write(*,*) 'Error at maximum of PDF: ', err_pdf_0
end if

! Calculation of error in OPP for every data point
if (output_opperr) then
    write(*, fmt = '(A)', advance = 'no') ' Calculating OPP error data ...'
    do i = 1, data_x
        do j = 1, data_y
            if (pdf(i,j) > 0) then
                z(i,j) = k * T * sqrt((err_pdf_0/pdf_0)**2 + (z(i,j)/pdf(i,j))**2)
            else
                z(i,j) = 1.0E+9    ! huge OPP error for zero or negative PDF
            end if
        end do
    end do          ! z filled with error in OPP
    write(*,*) 'done.'
end if

! WRITING OF OUTPUT FILE

! Writing introductory comment
comment = '# Format: x/A, y/A'
if (output_pdf) then
    comment = trim(comment) // ', PDF'
end if
if (output_pdferr) then
    comment = trim(comment) // ', sigma(PDF)'
end if
if (output_opp) then
    comment = trim(comment) // ', OPP/meV'
end if
if (output_opperr) then
    comment = trim(comment) // ', sigma(OPP)/meV'
end if
write(*, fmt = '(/,A,/)') separator   ! separates calculation from output information
write(*, fmt = '(A)', advance = 'no') ' Writing output file ...'
open(30, file = file_output, status = 'replace', action = 'write')
write(30,*) '# ASCII output generated by CalcOPP'
write(30,*) trim(comment)

! Preparing scratch data
if (output_opp) then
    rewind(40)
end if
if (output_pdferr) then
    rewind(41)
end if

! Writing actual data lines
do i = 1, data_x
    do j = 1, data_y
        write(output_line,fmt = '(2X,ES13.6,2X,ES13.6)') x_min + (i - 1) * x_inc, y_min + (j - 1) * y_inc
        if (output_pdf) then
            write(output_addition,fmt = '(2X,ES13.6)') pdf(i, j)
            output_line = trim(output_line) // output_addition
        end if
        if (output_pdferr) then
            read(41,*) output_addition
            output_line = trim(output_line) // '  ' // output_addition
        end if
        if (output_opp) then
            read(40,*) output_addition
            output_line = trim(output_line) // '  ' // output_addition
        end if
        if (output_opperr) then
            write(output_addition,fmt = '(2X,ES13.6)') z(i,j)
            output_line = trim(output_line) // output_addition
        end if
        write(30,*) trim(output_line)
    end do
end do
endfile(30)
close(30)
write(*,*) 'done.'
write(*,*) 'Output written to: ', trim(file_output)

! Clean exit
deallocate(pdf)
if (allocated(z)) then
    deallocate(z)
end if
if (output_opp) then
    close(40)
end if
if (output_pdferr) then
    close(41)
end if

write(*, fmt = '(/,A,/)') separator ! separates output from goodbye
write(*,*) '"This *does* compute!" - BMO'; write(*,*)

end program pdf2opp_2d


! Greeting text
subroutine print_greeting()
    write(*,*); write(*,*) 'PDF2OPP_2D 2.0.0 - Calculation of 2D OPP from PDF Data (JANA2006 STF Format)'
    write(*,*) 'Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)'; write(*,*)
end subroutine print_greeting


! Help text
subroutine print_help()
    write(*,*); write(*,*) 'Usage: pdf2opp_2d-<x86|x64> [OPTIONS]'; write(*,*)
    write(*,*) 'Options:'; write(*,*)
    write(*,*) '-h                Prints this usage information and exits.'
    write(*,*) '-i <file name>    Specifies the input file (key may be omitted).'
    write(*,*) '-o <file name>    Specifies the output file.'
    write(*,*) '-e <file name>    Specifies the error map file.'
    write(*,*) '-t <T/K>          Specifies the temperature in Kelvin'
    write(*,*) '                  (if not provided, extraction from *.m90 will be tried).'
    write(*,*) '-pdf              Includes PDF data in output.'
    write(*,*) '-pdferr           Includes PDF error map in output.'
    write(*,*) '-opp              Calculates and includes OPP data in output.'
    write(*,*) '-opperr           Calculates and includes OPP error map in output.'
    write(*,*); write(*,*) 'If none of the last four options is included, all data will be calculated'
    write(*,*) 'and put out.'
end subroutine print_help
