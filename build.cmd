@echo off
rem   This file is used to build/freeze CalcOPP on Windows systems. It relies on
rem   GFortran (https://gcc.gnu.org/wiki/GFortran), Pandoc (https://pandoc.org/),
rem   Python (https://www.python.org/), and UPX (https://upx.github.io/) being
rem   in the system PATH and WinRAR residing in its standard path.


rem   Compile the Fortran modules "pdf2opp_2d" and "pdf2opp_3d"
rem   WORKAROUND: Last option to mitigate MSYS linking bug with ASLR enabled
if not exist dist\ mkdir dist

gfortran pdf2opp_2d.f90 ^
    -o pdf2opp_2d.exe ^
    -std=f2018 ^
    -fall-intrinsics ^
    -ffpe-summary=none ^
    -pedantic ^
    -Wall ^
    -Wextra ^
    -O3 ^
    -fno-backtrace ^
    -static ^
    -s ^
    -Wl,--default-image-base-low

gfortran pdf2opp_3d.f90 ^
    -o pdf2opp_3d.exe ^
    -std=f2018 ^
    -fall-intrinsics ^
    -ffpe-summary=none ^
    -pedantic ^
    -Wall ^
    -Wextra ^
    -O3 ^
    -fno-backtrace ^
    -static ^
    -s ^
    -Wl,--default-image-base-low


rem   Create the documentation HTML files
if exist pandoc\ (
    cd pandoc
    pandoc ..\README.md ^
        --from gfm ^
        --to html5 ^
        --output ..\docs\README.html ^
        --standalone ^
        --metadata-file=metadata.yaml ^
        --resource-path=.;.. ^
        --self-contained

    pandoc ..\CHANGELOG.md ^
        --from gfm ^
        --to html5 ^
        --output ..\docs\CHANGELOG.html ^
        --standalone ^
        --metadata-file=metadata.yaml ^
        --self-contained
    cd ..
)


rem   Freeze the Python modules "sd2opp" and "calcopp-gui"
python -m PyInstaller sd2opp.py ^
   --noconfirm ^
   --clean ^
   --onedir ^
   --log-level=WARN ^
   --nowindowed ^
   --icon=data\CalcOPP.ico ^
   --version-file=sd2opp_info.txt ^
   --upx-dir=C:\upx

python -m PyInstaller calcopp-gui.py ^
   --name=CalcOPP ^
   --noconfirm ^
   --clean ^
   --onedir ^
   --log-level=WARN ^
   --add-data="data\citation.bib;data" ^
   --add-data="data\citation.ris;data" ^
   --add-data="data\logo.png;data" ^
   --add-data="data\CalcOPP.ico;data" ^
   --add-data="docs\README.html;docs" ^
   --add-data="docs\CHANGELOG.html;docs" ^
   --add-data="LICENSE;docs" ^
   --add-data="docs\BSD-2.0.txt;docs" ^
   --add-data="docs\LGPL-3.0.txt;docs" ^
   --add-binary="dist\sd2opp\sd2opp.exe;." ^
   --add-data="dist\sd2opp\sd2opp.exe.manifest;." ^
   --add-binary="pdf2opp_2d.exe;." ^
   --add-binary="pdf2opp_3d.exe;." ^
   --noconsole ^
   --icon=data\CalcOPP.ico ^
   --version-file=calcopp_info.txt ^
   --upx-dir=C:\upx


rem   Pack the data for distribution
if exist dist\ (
    cd dist
    "C:\Program Files\WinRAR\WinRAR.exe" a -m5zip CalcOPP.zip CalcOPP
    cd ..
)
