call python setup.py py2exe
rmdir /S /Q .\dist\tcl
#del .\dist\tcl85.dll
#del .\dist\tk85.dll
copy config.cfg .\dist