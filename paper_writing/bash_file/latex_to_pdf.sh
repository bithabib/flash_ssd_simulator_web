#!/bin/bash
rm -rf output
sleep 1
mkdir output
pdflatex /home/habib/Desktop/flash_ssd_simulator_web/paper_writing/latex_file/conference_101719.tex

# rm -rf *.hex
rm -rf *.log
# rm -rf *.aux

mv conference_101719.pdf ./output/conference_101719.pdf
# mv chapter_1.pdf ./output/chapter_1.pdf