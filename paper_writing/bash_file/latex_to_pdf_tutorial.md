# QuantumComputingBook
Learning quantum computing with ease
# Required tools for Mac
* Install mactex from here: https://www.tug.org/mactex/

# Required tools for ubuntu
PdfLatex is a tool that converts Latex sources into PDF. This is specifically very important for researchers, as they use it to publish their findings. It could be installed very easily using Linux terminal, though this seems an annoying task on Windows. Installation commands are given below.

### Install the TexLive base
```
sudo apt-get install texlive-latex-base
```
Also install the recommended and extra fonts to avoid running into the error [1], when trying to use pdflatex on latex files with more fonts.
```
sudo apt-get install texlive-fonts-recommended
sudo apt-get install texlive-fonts-extra
```
### Install the extra packages,
```
sudo apt-get install texlive-latex-extra
```
Once installed as above, you may be able to create PDF files from latex sources using PdfLatex as below.
```
pdflatex latex_source_name.tex
```

### Running
`sh textopdf.sh`
