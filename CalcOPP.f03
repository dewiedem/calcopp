program CalcOPP

!   CalcOPP 1.6.1 - Calculation of 2D OPP from PDF Data (JANA2000/2006 STF Format)
!   Copyright (C) 2015  Dr. Dennis Wiedemann (MIT License, see License.txt)

implicit none
character(248)                      :: file_input
character(256)                      :: file_output, file_error, key, arg, T_string, comment
character(256)                      :: output_line, output_addition
character(51), parameter            :: separator = ' ======================================='
integer                             :: i, j, data_x, data_y, ext_dot, io_status
integer                             :: remain_vals, job, err_data_x, err_data_y
integer, dimension(2)               :: xy_0
real                                :: x_min, x_max, y_min, y_max, T, pdf_0, x_inc, y_inc
real                                :: err_x_min, err_x_max, err_y_min, err_y_max, err_pdf_0
real, dimension(:), allocatable     :: z_stack
real, dimension(:,:), allocatable   :: z, pdf
logical                             :: exists_input, exists_error, output_pdf, output_pdferr
logical                             :: output_opp, output_opperr, interactive
real, parameter                     :: k = 8.6173324E-2     ! Boltzmann constant in meV/K

! ACQUIRING NECESSARY INPUT

! Parsing command-line arguments
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
        case ('-i', '--input')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_input)
            else
                write(*,*) 'Used -i, but no input-file name provided. Exiting.'
                stop
            end if
            i = i + 1
        case ('-o', '--output')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_output)
            else
                write(*,*) 'Used -o, but no output-file name provided. Exiting.'
                stop
            end if
            i = i + 1
        case ('-e', '--error_map')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_error)
            else
                write(*,*) 'Used -e, but no error-map name provided. Exiting.'
                stop
            end if
            i = i + 1
        case ('-t', '--temperature')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, T_string)
                read(T_string, '(E12.5)') T
            else
                write(*,*) 'Used -t, but no temperature provided. Exiting.'
                stop
            end if
            i = i + 1
        case ('-pdf', '--pdf')
            output_pdf = .true.
            i = i + 1
        case ('-pdferr', '--pdf_error')
            output_pdferr = .true.
            i = i + 1
        case ('-opp', '--opp')
            output_opp = .true.
            i = i + 1
        case ('-opperr', '--opp_error')
            output_opperr = .true.
            i = i + 1
        case ('-h', '--help')
            call print_help()
            stop
        case default
            if (index(arg, '-') == 1) then
                write(*,*) 'Unrecognised command-line option: ', arg
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

if ((.not. output_pdf) .and. (.not. output_pdferr) .and. (.not. output_opp) .and. (.not. output_opperr)) then
    output_pdf = .true.
    output_pdferr = .true.
    output_opp = .true.
    output_opperr = .true.
end if

call print_greeting()
write(*, fmt = '(/,A,/)') separator   ! separates greeting from input part

! Check if input-file name is valid, else ask for it and check again
exists_input = .false.
interactive = .false.
if (file_input /= '') then
    inquire(file = file_input, exist = exists_input)
end if
do while (.not. exists_input)
    interactive = .true.
    write(*, fmt = '(A)', advance = 'no') ' Name of input file (STF format from JANA2006): '
    read(*, fmt = '(A248)') file_input
    inquire(file = file_input, exist = exists_input)
end do

! Ask for name of output file, if not provided, or generate automatically
if ((interactive) .and. (file_output == '')) then
    write(*, fmt = '(/,A)', advance = 'no') ' Name of output file (default: <input>_opp.asc): '
    read(*, fmt = '(A256)') file_output
end if
if (file_output == '') then
    file_output = file_input
    ext_dot = index(file_output, '.', .true.)    ! check for file extension
    if (ext_dot > 0) then                        ! crop file extension, if existing
        file_output(ext_dot:len_trim(file_output)) = repeat(' ', len_trim(file_output) - ext_dot)
    end if
    file_output = trim(file_output) // '_opp.asc'
end if

! Provide menu for interactive mode
if (interactive) then
    call print_menu()
    do
        write(*, fmt = '(/,A)', advance = 'no') ' Please select the job: '
        read(*, fmt = '(I2)') job
        select case (job)
        case (1)
            output_pdf = .true.
            output_pdferr = .false.
            output_opp = .false.
            output_opperr = .false.
            exit
        case (2)
            output_pdf = .true.
            output_pdferr = .true.
            output_opp = .false.
            output_opperr = .false.
            exit
        case (3)
            output_pdf = .false.
            output_pdferr = .false.
            output_opp = .true.
            output_opperr = .false.
            exit
        case (4)
            output_pdf = .false.
            output_pdferr = .false.
            output_opp = .true.
            output_opperr = .true.
            exit
        case (5)
            output_pdf = .true.
            output_pdferr = .false.
            output_opp = .true.
            output_opperr = .false.
            exit
        case (6)
            output_pdf = .true.
            output_pdferr = .true.
            output_opp = .true.
            output_opperr = .true.
            exit
        case default
            write(*,*) 'Invalid choice.'
            cycle
        end select
    end do
end if

! Automatically generate name of error map, if not provided and necessary, and check existence;
! User input, if not existent
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
        write(*,*); write(*,*) 'Default error map <input>_err.stf not found.'
        if (.not. interactive) then
            output_pdferr = .false.
            output_opperr = .false.
        end if
    end if
    do while ((.not. exists_error) .and. interactive)
        write(*, fmt = '(A)', advance = 'no') ' Name of error map: '
        read(*, fmt = '(A256)') file_error
        inquire(file = file_error, exist = exists_error)
    end do
end if

! Ask for temperature, if not provided, and check it
do while ((T <= 0.) .and. (output_opp .or. output_opperr))
    write(*, fmt = '(/,A)', advance = 'no') ' Temperature/K: '
    read(*,*) T
end do

write(*, fmt = '(/,A,/)') separator    ! separates input part from calculation information

! PARSING INPUT FILE(S)

! Search for DIMENSIONS
open(20,file = file_input,status = 'old',action = 'read')
io_status = 0
key = ''
do while ((io_status == 0) .and. (key /= 'DIMENSIONS'))
    read(20,*,iostat=io_status) key
end do
if (io_status /= 0) then
    write(*,*) 'Unable to find grid dimensions as defined by DIMENSIONS. Exiting.'
    close(20)
    stop
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
    write(*,*) 'Unable to find limits as defined by BOUNDS. Exiting.'
    close(20)
    stop
end if
backspace(20)
read(20,*,iostat=io_status) key, x_min, x_max, y_min, y_max
write(*,*) 'Limits of x (min, max): ', x_min, x_max
write(*,*) 'Limits of y (min, max): ', y_min, y_max; write(*,*)

! Test conformance of error-map DIMENSIONS
if (output_pdferr .or. output_opperr) then
    write(*, fmt = '(A)', advance = 'no') ' Validating error-map dimensions ...'
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

! Test conformance of error-map BOUNDS
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
    write(*,*) 'Unable to find DATA statement. Exiting.'
    close(20)
    stop
end if
do i = 1, int((data_x * data_y)/8.)    ! Reading lines with eight data points
    read(20,*,iostat=io_status) z_stack(8 * i - 7:8 * i)
end do
if (remain_vals > 0) then              ! Reading remaining incomplete line if present
    read(20,*,iostat=io_status) z_stack(8 * i - 7:8 * i - 8 + remain_vals)
end if
write(*,*) 'done.'
write(*,*) 'Total of PDF data-points found: ', 8 * i - 8 + remain_vals
close(20)

! Transfer of PDF data from stack to ordered matrix
allocate(pdf(1:data_x,1:data_y))
pdf = reshape(z_stack, (/ data_x, data_y /))
deallocate(z_stack)

! CALCULATION OF OPP

write(*, fmt = '(/,A,/)') separator  ! seperate PDF from OPP part

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
    write(*,*) 'Total of error data-points found: ', 8 * i - 8 + remain_vals; write(*,*)
    close(25)
end if

! Transfer of PDF error-data from stack to ordered matrix
if (output_pdferr .or. output_opperr) then
    allocate(z(1:data_x,1:data_y))
    z = reshape(z_stack, (/ data_x, data_y /))  ! z filled with PDF error data
    deallocate(z_stack)
end if

! Store PDF error in temporary file to reduce memory usage
if (output_pdferr) then
    open(41,status = 'scratch',access = 'sequential',action = 'readwrite')
    write(*, fmt = '(A)', advance = 'no') ' Temporarily storing PDF error-data ...'
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
    write(*, fmt = '(A)', advance = 'no') ' Calculating OPP error-data ...'
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

write(*, fmt = '(/,A,/)') separator ! Separates output from goodbye
write(*,*) '"This *does* compute!" - BMO'; write(*,*)

end program CalcOPP


! Greeting text
subroutine print_greeting()
    write(*,*); write(*,*) 'CalcOPP 1.6.1 - Calculation of 2D OPP from PDF Data (JANA2000/2006 STF Format)'
    write(*,*) 'Copyright ¸ 2015  Dr. Dennis Wiedemann (MIT License, see License.txt)'; write(*,*)
    write(*,*) 'If you prepare data for publication with CalcOPP, please use the'
    write(*,*) 'following citation:'
    write(*,*) 'D. Wiedemann, CalcOPP, Calculation of 2D OPP from PDF Data,'
    write(*,*) 'Technische Universit„t Berlin, Berlin (Germany), 2015,'
    write(*,*) 'doi:10.6084/m9.figshare.1461721.'
end subroutine print_greeting


! Menu text
subroutine print_menu()
    write(*,fmt = '(/,/,A)') ' List of Jobs'
    write(*,*) '------------'; write(*,*)
    write(*,*) '1 - Write PDF data'
    write(*,*) '2 - Write PDF data with error map'
    write(*,*) '3 - Calculate and write OPP data'
    write(*,*) '4 - Calculate and write OPP data with error map'
    write(*,*) '5 - Calculate and write PDF and OPP data'
    write(*,*) '6 - Calculate and write PDF and OPP data with error maps'
end subroutine print_menu


! Help text
subroutine print_help()
    write(*,*); write(*,*) 'Usage: CalcOPP32|CalcOPP64 [OPTIONS]'; write(*,*)
    write(*,*) 'Without further options, CalcOPP will enter interactive mode and ask the'
    write(*,*) 'user to provide necessary data.'; write(*,*)
    write(*,*) 'Options:'; write(*,*)
    write(*,*) '-h, --help                 Prints this usage information and exits.'
    write(*,*) '-i, --input <file name>    Specifies the input file (key may be omitted).'
    write(*,*) '-o, --output <file name>   Specifies the output file.'
    write(*,*) '-e, --error <file name>    Specifies the error-map file.'
    write(*,*) '-t, --temperature <T/K>    Specifies the temperature in Kelvin.'
    write(*,*) '-pdf, --pdf                Includes PDF data in output.'
    write(*,*) '-pdferr, --pdf_error       Includes PDF error-map in output.'
    write(*,*) '-opp, --opp                Calculates and includes OPP data in output.'
    write(*,*) '-opperr, --opp_error       Calculates and includes OPP error-map in output.'
    write(*,*); write(*,*) 'If none of the last four options is included, all data will be calculated'
    write(*,*) 'and put out.'
end subroutine print_help