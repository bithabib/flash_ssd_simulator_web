#!/bin/bash
# read the current directory
echo "Current directory: $PWD"
# set it in a variable
current_dir=$PWD
# add /paper_writing/latex_file/conference_101719.tex with the current directory variable
current_dir_with_file=$current_dir/paper_writing/latex_file/conference_101719.tex
pdflatex $current_dir_with_file
rm -rf *.hex
rm -rf *.log
rm -rf *.aux
mv conference_101719.pdf ./static/paper/conference_101719.pdf
