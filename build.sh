#!/bin/bash
#
# This file is used to build/freeze CalcOPP on Linux systems. It relies on
# GFortran (https://gcc.gnu.org/wiki/GFortran), Pandoc (https://pandoc.org/),
# Python (https://www.python.org/), and UPX (https://upx.github.io/) being
# in the system PATH.


# Compile the Fortran modules "pdf2opp_2d" and "pdf2opp_3d"
if [ ! -d "dist" ]; then
    mkdir dist
fi

gfortran-10 pdf2opp_2d.f90 \
    -o pdf2opp_2d \
    -std=f2018 \
    -fall-intrinsics \
    -ffpe-summary=none \
    -pedantic \
    -Wall \
    -Wextra \
    -O3 \
    -fno-backtrace \
    -static \
    -s \
    -m64

gfortran-10 pdf2opp_3d.f90 \
    -o pdf2opp_3d \
    -std=f2018 \
    -fall-intrinsics \
    -ffpe-summary=none \
    -pedantic \
    -Wall \
    -Wextra \
    -O3 \
    -fno-backtrace \
    -static \
    -s \
    -m64 

chmod +x pdf2opp_2d pdf2opp_3d


# Create the documentation HTML files
cd pandoc

pandoc ../README.md \
    --from gfm \
    --to html5 \
    --output ../docs/README.html \
    --standalone \
    --metadata-file=metadata.yaml \
    --resource-path=.:.. \
    --self-contained

pandoc ../CHANGELOG.md \
    --from gfm \
    --to html5 \
    --output ../docs/CHANGELOG.html \
    --standalone \
    --metadata-file=metadata.yaml \
    --self-contained

cd ..


# Freeze the Python modules "sd2opp" and "calcopp-gui"
# ("--strip" flag incompatible with NumPy 1.19.1)
python3.7 -O -m PyInstaller sd2opp.py \
   --noconfirm \
   --clean \
   --onedir \
   --log-level=WARN \
   --upx-dir="/usr/bin/"

python3.7 -O -m PyInstaller calcopp-gui.py \
   --name=CalcOPP \
   --noconfirm \
   --clean \
   --onedir \
   --log-level=WARN \
   --add-data="data/citation.bib:data" \
   --add-data="data/citation.ris:data" \
   --add-data="data/logo.png:data" \
   --add-data="data/CalcOPP.ico:data" \
   --add-data="docs/README.html:docs" \
   --add-data="docs/CHANGELOG.html:docs" \
   --add-data="LICENSE:docs" \
   --add-data="docs/BSD-2.0.txt:docs" \
   --add-data="docs/LGPL-3.0.txt:docs" \
   --add-data="dist/sd2opp/sd2opp:." \
   --add-data="pdf2opp_2d:." \
   --add-data="pdf2opp_3d:." \
   --upx-dir="/usr/bin/"

chmod +x dist/CalcOPP/CalcOPP dist/CalcOPP/sd2opp


# Pack the data for distribution
cd dist

zip -r9 CalcOPP.zip CalcOPP

cd ..
