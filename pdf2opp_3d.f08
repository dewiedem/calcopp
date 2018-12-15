program pdf2opp_3d

!   CalcOPP 2.0.0 - Calculation of Effective One-Particle Potentials
!   PDF2OPP_3D - Subroutines for Calculation from 3D PDF Data (JANA2006 XSF Format)
!   Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)

implicit none
character(len = 256)                    :: file_input_xsf, file_output_xsf, &
                                           file_input_m90, file_output_vesta   ! Input and output file names
character(len = 256)                    :: line                                ! Input line read from files
character(len = 256)                    :: keyword                             ! Keyword read from XSF file
character(len = 256)                    :: opp_high_str, columns_str           ! String variables for maximum OPP and column number
character(len = 256)                    :: fmt_str                             ! Format string for data lines in XSF files
integer                                 :: ext_position                        ! Position of extension dot in file name
integer                                 :: io_status                           ! Status of the file I/O
integer                                 :: header_end                          ! Line number of header end in XSF files
integer                                 :: i                                   ! Counter
integer, parameter                      :: columns = 5                         ! Number of columns in input grid data
real,                dimension(columns) :: pdf, opp                            ! PDF and OPP data
character(len = 64), dimension(columns) :: pdf_str, opp_str                    ! PDF and OPP data as strings
real                                    :: T                                   ! Temperature in Kelvin
real                                    :: pdf_0                               ! Maximum input PDF
real                                    :: pdf_min                             ! Minimum input PDF
real                                    :: opp_high                            ! Maximum OPP
logical                                 :: exists_input_xsf, exists_input_m90  ! Flags for the existence of files
logical                                 :: temp_found                          ! Flag for existence of temperature in *.m90

character(len = *), parameter           :: separator = ' ' // repeat('=', 40)  ! Visual separator for standard output
character(len = *), parameter           :: version = '2.0.0'                   ! Program version
real,               parameter           :: K_B = 8.617330E-5                   ! Boltzmann constant in eV/K

! INITIALIZING

call print_greeting(separator)

! Preparing input/output formats
write(columns_str, *) columns
fmt_str = '(' // trim(columns_str) // 'A15)'

! ACQUIRING INPUT FILE

! Getting file name from command line
if (command_argument_count() == 0) then
    write(*, *) 'No file name provided. Exiting.'
    call print_help(separator)
    call print_goodbye(separator)
    stop
else
    call get_command_argument(1, file_input_xsf)
end if

! Testing if input file exists
exists_input_xsf = .false.
inquire(file = file_input_xsf, exist = exists_input_xsf)
if (.not. exists_input_xsf) then
    write(*, *) 'Input file not found. Exiting.'
    call print_help(separator)
    call print_goodbye(separator)
    stop
end if

! Preparing file names
file_output_xsf = file_input_xsf
ext_position = index(file_output_xsf, '.', .true.)    ! check for file extension
if (ext_position > 0) then                            ! crop file extension, if existing
    file_output_xsf(ext_position:len_trim(file_output_xsf)) = repeat(' ', len_trim(file_output_xsf) - ext_position)
end if

ext_position = index(file_output_xsf, '_tmp', .true.) ! check for "_tmp" ending
if (ext_position > 0) then                            ! crop "_tmp" ending, if existing
    file_output_xsf(ext_position:len_trim(file_output_xsf)) = repeat(' ', len_trim(file_output_xsf) - ext_position)
end if

file_input_m90 = trim(file_output_xsf) // '.m90'
file_output_vesta = trim(file_output_xsf) // '_opp.vesta'
file_output_xsf = trim(file_output_xsf) // '_opp.xsf'

! ACQUIRING TEMPERATURE

! Try automatic extraction from *.m90
inquire(file = file_input_m90, exist = exists_input_m90)

if (exists_input_m90) then
    write(*, fmt = '(A)', advance = 'no') ' *.m90 found.'
    open(90, file = file_input_m90, status = 'old', action = 'read')
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
        read(line(12:), *) T
        write(*, *) 'Temperature found: T = ', T, ' K'
        temp_found = .true.
    else
        write(*, *) 'Temperature not found in *.m90.'
        temp_found = .false.
    end if

else

    write(*, *) '*.m90 not found.'
    temp_found = .false.

end if

! Ask for user input if temperature was not found
if (.not. temp_found) then
    T = -1.
    do while (T <= 0.)
        write(*, fmt = '(A)', advance = 'no') ' Temperature/K: '
        read(*, *) T
    end do
end if

write(*, fmt = '(/, A, /)') separator ! Separates input from calculation

! PARSING INPUT FILE

open(20, file = file_input_xsf, status = 'old', action = 'read')

! Looking for the beginning of the first 3D data grid and saving line number
keyword = ''
header_end = 0
io_status = 0
do while ((.not. is_iostat_end(io_status)) .and. (index(keyword, 'BEGIN_DATAGRID_3D') == 0))
    read(20, *, iostat = io_status) keyword
    header_end = header_end + 1
end do

if (is_iostat_end(io_status)) then
    write(*, *) 'No 3D data grid found in ' // trim(file_input_xsf) // ' . Exiting.'
    call print_goodbye(separator)
    stop
end if

! Skipping origin, three spanning vectors, and number of points
do i = 1, 5
    read(20, *)
end do
header_end = header_end + 5

! GETTING MAXIMUM AND MINIMUM VALUE

write(*, fmt = '(A)', advance = 'no') ' Extracting PDF extrema ...'

pdf_min = huge(0.0)
pdf_0 = tiny(0.0)
io_status = 0
do i = 1, columns
    pdf_str(i) = ''
end do
keyword = ''

do while ((.not. is_iostat_end(io_status)) .and. (keyword /= 'END_DATAGRID_3D'))

    ! Check if block end is reached
    read(20, *, iostat = io_status) keyword
    if (keyword == 'END_DATAGRID_3D') cycle
    backspace(20)

    ! Read and process actual values
    read(20, fmt = fmt_str, iostat = io_status) pdf_str
    do i = 1, columns
        if (pdf_str(i) /= '') then
            read(pdf_str(i), *) pdf(i)
            ! Search for minimum
            if ((pdf(i) < pdf_min) .and. (pdf(i) > 0)) pdf_min = pdf(i)
            ! Search for maximum
            if (pdf(i) > pdf_0) pdf_0 = pdf(i)
        else
            ! Set empty values arbitrarily (will not be used anyway)
            pdf(i) = -1.
        end if
    end do

end do

! Visual output to user
write(*, *) 'Done.'
write(*, *) 'p(max) =', pdf_0, 'A^-3', '     p(min) =', pdf_min, 'A^-3'

if (keyword /= 'END_DATAGRID_3D') then
    write(*, *) ' WARNING: Unexpected end of data grid. Output will probably be malformed.'
end if

close(20)

! COMPUTING AND WRITING DATA OUTPUT

open(20, file = file_input_xsf, status = 'old', action = 'read')
open(30, file = file_output_xsf, status = 'replace', action = 'write')

! Copy header
do i = 1, header_end
    read(20, fmt = '(A256)') line
    write(30, fmt = '(A)') trim(line)
end do

! Calculate OPP for each point
write(*, fmt = '(A)', advance = 'no') ' Calculating OPP and writing data to ' // trim(file_output_xsf) // ' ...'

io_status = 0
do i = 1, columns
    pdf_str(i) = ''
end do
keyword = ''

! Highest OPP in data set
opp_high = -1 * k * T * log(pdf_min/pdf_0)
write(opp_high_str, fmt = '(E15.6)') opp_high

do while ((.not. is_iostat_end(io_status)) .and. (keyword /= 'END_DATAGRID_3D'))

    ! Check if block end is reached
    read(20, *, iostat = io_status) keyword
    if (keyword == 'END_DATAGRID_3D') then
        write(30, fmt = '(A)') '  END_DATAGRID_3D'
        cycle
    end if
    backspace(20)

    ! Read actual values
    read(20, fmt = fmt_str, iostat = io_status) pdf_str
    do i = 1,columns
        if (pdf_str(i) /= '') then
            read(pdf_str(i), *) pdf(i)
        else
            ! Set empty values arbitrarily (will not be used anyway)
            pdf(i) = -1.
        end if
    end do

    ! Process and write values
    opp = -1 * k * T * log(pdf/pdf_0)
    do i = 1,columns
        write(opp_str(i), fmt = '(E15.6)') opp(i)
        ! Highest OPP for zero or negative PDF
        if (pdf(i) <= 0.) opp_str(i) = trim(opp_high_str)
        ! Empty OPP if PDF was empty
        if (pdf_str(i) == '') opp_str(i) = ''
    end do

    write(30,fmt = fmt_str) opp_str

end do
write(*,*) 'Done.'
write(*,*) 'V(max) =', opp_high, 'eV'

! Copy footer
do while (.not. is_iostat_end(io_status))
    read(20, fmt = '(A256)', iostat = io_status) line
    if (is_iostat_end(io_status)) cycle
    write(30, fmt = '(A)') trim(line)
end do

close(20)
close(30)

! OUTPUT VESTA FILE
write(*, fmt = '(A)', advance = 'no') ' Creating ' // trim(file_output_vesta) // ' ...'
open(40, file = file_output_vesta, status = 'replace', action = 'write')
write(40, fmt = '(A)') '#VESTA_FORMAT_VERSION 2'
write(40, *)
write(40, fmt = '(A)') 'IMPORT_STRUCTURE'
write(40, fmt = '(A)') trim(file_output_xsf)
write(40, *)
write(40, fmt = '(A)') 'IMPORT_DENSITY 1'
write(40, fmt = '(A)') '+1.00000 ' // trim(file_output_xsf)
close(40)
write(*, *) 'Done.'

call print_goodbye(separator)

end program pdf2opp_3d

! TEXT OUTPUTS

! Greeting text
subroutine print_greeting(separator)

    implicit none
    character(*), intent(in) :: separator  ! Visual separator

    write(*, fmt = '(/, A, /)') separator
    write(*, *) 'PDF2OPP_3D 2.0.0 - Calculation of 3D OPP from PDF Data (JANA2006 XSF Format)'
    write(*, *) 'Copyright (c) 2019  Dr. Dennis Wiedemann (MIT License, see LICENSE file)'
    write(*, *)
    write(*, fmt = '(/, A, /)') separator

end subroutine print_greeting

! Help text
subroutine print_help(separator)

    implicit none
    character(*), intent(in) :: separator  ! Visual separator

    write(*, fmt = '(/, A, /)') separator
    write(*, *) 'Usage: pdf2opp_3d [OPTIONS]'
    write(*, *)
    write(*, *) 'Options:'
    write(*, *)
    write(*, *) '-h                Prints this usage information and exits.'
    write(*, *) '-i <file name>    Specifies the input file.'
    write(*, *) '-o <file name>    Specifies the output file.'
    write(*, *) '-t <T/K>          Specifies the temperature in Kelvin'
    write(*, *) '                  (if not provided, extraction from *.m90 will be tried).'

end subroutine print_help

! Goodbye text
subroutine print_goodbye(separator)

    implicit none
    character(*), intent(in) :: separator  ! Visual separator

    write(*, fmt = '(/, A, /)') separator
    write(*, *) '"Trust me, I''m the doctor!" - The Doctor'
    write(*, *)

end subroutine print_goodbye

! TODO (Dennis#1#): Wait in before closing window if invoked via drag and drop
! TODO (Dennis#1#): Accept input/output file names and custom temperatures
! TODO (Dennis#1#): Test output size in GUI
! TODO (Dennis#1#): Check output spacing and separators
! TODO (Dennis#1#): Write better VESTA file (see SD2OPP)
! TODO (Dennis#1#): Strip user input via keyboard
! TODO (Dennis#1#): Use for files NEWUNIT intrinsic
! TODO (Dennis#1#): Version output
! TODO (Dennis#1#): Optimize array handling, avoid text arrays if possible
! TODO (Dennis#1#): Conversion function instead of extra variable for str-to-num
