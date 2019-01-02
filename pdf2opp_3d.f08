program pdf2opp_3d

!   CalcOPP 2.0.0-rc1 - Calculation of Effective One-Particle Potentials
!   PDF2OPP_3D - Subroutines for Calculation from 3D PDF Data (JANA2006 XSF Format)
!   Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)

implicit none
character(len = 256)               :: file_input_xsf, file_output_xsf, &
                                      file_input_m90, file_output_vesta   ! Input and output file names
character(len = 256)               :: line                                ! Input line read from files
character(len = 256)               :: dataset_name                        ! Name of dataset from header
character(len = 256)               :: temp_string                         ! Temperature as string
character(len = 256)               :: cmd_arg                             ! Command-line argument
integer                            :: io_status                           ! Status of the file I/O
integer                            :: i                                   ! Counter
integer                            :: in_unit, out_unit, m90_unit         ! Unit numbers for file access
integer, dimension(3)              :: npoints                             ! Number of points in x, y, z direction
real,    dimension(:), allocatable :: values                              ! PDF/OPP values
real                               :: temp                                ! Temperature in Kelvin
real                               :: pdf_0                               ! Maximum input PDF
real                               :: pdf_min                             ! Minimum input PDF
real                               :: opp_max                             ! Maximum OPP
logical                            :: exists_input_xsf, exists_input_m90  ! Flags for the existence of files
logical                            :: is_dnd                              ! Flag for drag and drop

character(len = *), parameter      :: SEPARATOR = ' ' // repeat('=', 50)  ! Visual separator for standard output
character(len = *), parameter      :: VERSION = '2.0.0-rc1'               ! Program version
real,               parameter      :: K_B = 8.617330E-5                   ! Boltzmann constant in eV/K


! INITIALIZE

file_input_xsf = ''
file_output_xsf = ''
out_unit = -1
temp = -1.0
is_dnd = .false.

! PARSE COMMAND-LINE ARGUMENTS

! Read in values and perform basic checks
i = 1
do while (i <= command_argument_count())
    call get_command_argument(i, cmd_arg)
    select case (cmd_arg)
        case ('-h')
            call print_help()
            call finish('', out_unit, is_dnd)
        case ('-v')
            write(*, fmt = '(A)') VERSION
            call finish('', out_unit, is_dnd)
        case ('-i')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_input_xsf)
            else
                call print_help()
                call finish('Used -i, but no input file name provided.', out_unit, is_dnd)
            end if
            i = i + 1
        case ('-o')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, file_output_xsf)
            else
                call print_help()
                call finish('Used -o, but no output file name provided.', out_unit, is_dnd)
            end if
            i = i + 1
        case ('-t')
            i = i + 1
            if (i <= command_argument_count()) then
                call get_command_argument(i, temp_string)
                read(temp_string, *, iostat = io_status) temp
                if (io_status /= 0) call finish('Used -t, but no valid temperature as decimal value provided.', out_unit, is_dnd)
            else
                call print_help()
                call finish('Used -t, but no temperature provided.', out_unit, is_dnd)
            end if
            i = i + 1
        case default
            if (index(cmd_arg, '-') == 1) then
                call print_help()
                call finish('Unrecognized command-line option: ' // trim(cmd_arg), out_unit, is_dnd)
            else if (file_input_xsf == '') then
                file_input_xsf = cmd_arg
                is_dnd = .true.
            else
                write(*, *) 'Ignoring unexpected input: ' // trim(cmd_arg)
            end if
            i = i + 1
    end select
end do

! Check validity of input file name
if (file_input_xsf == '') then
    call print_help()
    call finish('No input file name provided.', out_unit, is_dnd)
else
    exists_input_xsf = .false.
    inquire(file = file_input_xsf, exist = exists_input_xsf)
    if (.not. exists_input_xsf) call finish('No valid input file name provided.', out_unit, is_dnd)
end if

call print_greeting(SEPARATOR, VERSION)

! Construct file names
file_input_m90 = new_ext(file_input_xsf, '.m90')
if (file_output_xsf == '') then
    file_output_xsf = new_ext(file_input_xsf, '_opp.xsf')
    file_output_vesta = new_ext(file_input_xsf, '_opp.vesta')
else
    file_output_vesta = new_ext(file_output_xsf, '.vesta')
end if

! Extract temperature from *.m90
if (temp <= 0.0) then
    write(*, fmt = '(A)', advance = 'no') ' Temperature not given. Probing *.m90 ...'

    exists_input_m90 = .false.
    inquire(file = file_input_m90, exist = exists_input_m90)
    if (exists_input_m90) then
        write(*, fmt = '(A)', advance = 'no') ' found.'
        open(newunit = m90_unit, file = file_input_m90, status = 'old', action = 'read')
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
            if (io_status /= 0) call finish('No valid temperature found in *.m90.', out_unit, is_dnd)
            write(*, *)
            write(*, fmt = '(A, F0.4, A)') ' Temperature: T = ', temp, ' K'
            write(*, fmt = '(/, A, /)') SEPARATOR  ! Separates temperature extraction from calculation
        else
            call finish('No valid temperature found in *.m90.', out_unit, is_dnd)
        end if
    else
        write(*, *) 'failed.'
        call finish('Temperature not given and *.m90 not found.', out_unit, is_dnd)
    end if
end if

! PARSE AND COPY INPUT HEADER

write(*, fmt = '(A)', advance = 'no') ' Reading file header ...'
open(newunit = in_unit, file = file_input_xsf, status = 'old', action = 'read')
open(newunit = out_unit, file = file_output_xsf, status = 'replace', action = 'write')
line = ''
io_status = 0

! Copy between beginning and dataset title verbatim
do while ((.not. is_iostat_end(io_status)) .and. (index(line, 'BEGIN_BLOCK_DATAGRID_3D') /= 1))
    read(in_unit, fmt = '(A)', iostat = io_status) line
    write(out_unit, fmt = '(A)') trim(line)
end do

if (is_iostat_end(io_status)) then
    write(*, *) 'failed.'
    call finish('No 3D data-grid block found.', out_unit, is_dnd)
end if

! Read dataset title and write modified title
read(in_unit, fmt = '(A)', iostat = io_status) dataset_name
if (io_status /= 0) then
    write(*, *) 'failed.'
    call finish('Error reading dataset title.', out_unit, is_dnd)
end if
write(out_unit, fmt = '(A)') '  OPP from ' // trim(adjustl(dataset_name))

! Copy between dataset title and first 3D grid verbatim
do while ((.not. is_iostat_end(io_status)) .and. (index(line, 'BEGIN_DATAGRID_3D') == 0))
    read(in_unit, fmt = '(A)', iostat = io_status) line
    write(out_unit, fmt = '(A)') trim(line)
end do

if (is_iostat_end(io_status)) then
    write(*, *) 'failed.'
    call finish('No 3D data grid found.', out_unit, is_dnd)
end if

! Read number of data points
read(in_unit, *, iostat = io_status) npoints
if (io_status /= 0) then
    write(*, *) 'failed.'
    call finish('Error reading number of data points.', out_unit, is_dnd)
end if
write(out_unit, fmt = '(3(2X, I0))') npoints

! Copy origin and three spanning vectors verbatim
do i = 1, 4
    read(in_unit, fmt = '(A)', iostat = io_status) line
    if (io_status /= 0) then
        write(*, *) 'failed.'
        call finish('Error reading cell vectors.', out_unit, is_dnd)
    end if
    write(out_unit, fmt = '(A)') trim(line)
end do

write(*, *) 'done.'
write(*, *) 'Dataset title: ' // trim(adjustl(dataset_name))
write(*, fmt = '(A, 3(I0, 2X), /)') ' Number of data (x, y, z):  ', npoints

! READ, PROCESS, AND WRITE VALUES

! Read PDF from file
allocate(values(product(npoints)))
write(*, fmt = '(A)', advance = 'no') ' Reading data ...'
read(in_unit, *, iostat = io_status) values
if (io_status /= 0) then
    write(*, *) 'failed.'
    call finish('Error reading data values.', out_unit, is_dnd)
    end if
write(*, *) 'done.'

pdf_min = minval(values)
pdf_0 = maxval(values)
write(*, fmt = '(A, ES13.6, A)') ' p(max) = ', pdf_0, ' A^-3'
write(*, fmt = '(A, ES13.6, A)') ' p(min) = ', pdf_min, ' A^-3'


! Check for regular termination of data block
read(in_unit, fmt = '(A)', iostat = io_status) line
if (io_status /= 0 .or. trim(adjustl(line)) /= 'END_DATAGRID_3D') then
    write(*, *)
    write(*, *) 'WARNING: Irregular end of data grid.'
    write(*, *) '         Output will possibly be malformed.'
end if

write(*, fmt = '(/, A, /)') SEPARATOR  ! Separates PDF from OPP part

! Calculate OPP
write(*, fmt = '(A)', advance = 'no') ' Calculating OPP ...'

values = -1 * K_B * temp * log(values/pdf_0)
opp_max = maxval(values, (.not. isnan(values)))
where (isnan(values)) values = opp_max
write(*, *) 'done.'
write(*, fmt = '(A, ES13.6, A, /)') ' V(max) = ', opp_max, ' eV'

! Write OPP to file
write(*, fmt = '(A)', advance = 'no') ' Writing OPP ...'
write(out_unit, fmt = '(5E15.6)') values
write(out_unit, fmt = '(A)') '  END_DATAGRID_3D'
write(*, *) 'done.'

! COPY INPUT FOOTER

do while (.not. is_iostat_end(io_status))
    read(in_unit, fmt = '(A)', iostat = io_status) line
    if (is_iostat_end(io_status)) cycle
    write(out_unit, fmt = '(A)') trim(line)
end do

! CREATE VESTA FILE

call create_vesta('OPP from ' // trim(adjustl(dataset_name)), file_output_xsf, file_output_vesta, opp_max / 2)

! TERMINATE

close(in_unit)
close(out_unit)
call print_goodbye(SEPARATOR)
call finish('', out_unit, is_dnd)


contains


! Add a different extension to a file name
function new_ext(file_name, extension)

    implicit none
    character(len = *), intent(in)  :: file_name  ! File to add new extension to
    character(len = *), intent(in)  :: extension  ! New extension to add
    character(len = 256)            :: new_ext    ! File name with new extension
    integer, dimension(2)           :: ext_pos    ! Positions of extension separators

    ext_pos = (/ scan(trim(file_name), '_tmp', back = .true.) - 4,  scan(trim(file_name), '.', back = .true.) - 1 /)
    if (any(ext_pos > 0)) then
        new_ext = file_name(1:minval(ext_pos, (ext_pos > 0))) // extension
    else
        new_ext = trim(file_name) // extension
    end if

end function new_ext


end program pdf2opp_3d


! Print greeting text
subroutine print_greeting(sep, ver)

    implicit none
    character(len = *), intent(in) :: sep  ! Visual separator
    character(len = *), intent(in) :: ver  ! Program version

    write(*, *) 'PDF2OPP_3D ' // ver // ' - Calculation of 3D OPP from PDF Data (JANA2006 XSF Format)'
    write(*, *) 'Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)'
    write(*, fmt = '(/, A, /)') sep

end subroutine print_greeting


! Print help text
subroutine print_help()

    write(*, *) 'Usage: pdf2opp_3d [OPTIONS]'
    write(*, *)
    write(*, *) 'Options:'
    write(*, *)
    write(*, *) '-h                Prints this usage information and exits.'
    write(*, *) '-v                Prints the version number and exits.'
    write(*, *) '-i <file name>    Specifies the input file.'
    write(*, *) '-o <file name>    Specifies the output file.'
    write(*, *) '-t <T/K>          Specifies the temperature in Kelvin'
    write(*, *) '                  (if not provided, extraction from *.m90 will be tried).'

end subroutine print_help


! Print goodbye text
subroutine print_goodbye(sep)

    implicit none
    character(len = *), intent(in) :: sep  ! Visual separator

    write(*, fmt = '(/, A, /)') sep
    write(*, *) '"Trust me, I''m the doctor!" - The Doctor'

end subroutine print_goodbye


! Create VESTA file
subroutine create_vesta(title, xsf_file, vesta_file, isovalue)

    implicit none
    character (len = *), intent(in) :: title                 ! Title of data set
    character (len = *), intent(in) :: xsf_file, vesta_file  ! Name of XSF and VESTA output files
    real,                intent(in) :: isovalue              ! Isosurface level for initial display
    integer                         :: vesta_unit            ! Unit number for VESTA output file

    write(*, fmt = '(A)', advance = 'no') ' Creating VESTA file ...'
    open(newunit = vesta_unit, file = vesta_file, status = 'replace', action = 'write')

    write(vesta_unit, fmt = '(A)') '#VESTA_FORMAT_VERSION 3.3.0'
    write(vesta_unit, *)
    write(vesta_unit, *)
    write(vesta_unit, fmt = '(A)') 'CRYSTAL'
    write(vesta_unit, *)
    write(vesta_unit, fmt = '(A)') 'TITLE'
    write(vesta_unit, fmt = '(A)') trim(title)
    write(vesta_unit, *)
    write(vesta_unit, fmt = '(A)') 'IMPORT_STRUCTURE'
    write(vesta_unit, fmt = '(A)') trim(xsf_file)
    write(vesta_unit, *)
    write(vesta_unit, fmt = '(A)') 'IMPORT_DENSITY 1'
    write(vesta_unit, fmt = '(A)') '+1.000000 ' // trim(xsf_file)
    write(vesta_unit, *)
    write(vesta_unit, fmt = '(A)') 'STYLE'
    write(vesta_unit, fmt = '(A)') 'SECTS  96  0'
    write(vesta_unit, fmt = '(A)') 'ISURF'
    write(vesta_unit, fmt = '(A, F0.2, A)') '  1   1          ', isovalue ,' 255 255   0 127 255'
    write(vesta_unit, fmt = '(A)') '  0   0   0   0'

    close(vesta_unit)
    write(*, *) 'done.'

end subroutine create_vesta


! Exit program
subroutine finish(error_message, out_unit, is_drag_and_drop)

    implicit none
    character(len = *), intent(in) :: error_message     ! Error message (empty for no error)
    integer,            intent(in) :: out_unit          ! Unit number of output file
    logical,            intent(in) :: is_drag_and_drop  ! True if program invoked via drag and drop
    logical                        :: output_open       ! Flag for status of output
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
        output_open = .false.
        if (out_unit /= -1) inquire(out_unit, opened = output_open)
        if (output_open) close(out_unit, status = 'delete')
        error stop error_message
    else
        stop
    end if

end subroutine finish
