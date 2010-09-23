import sys
# http://www.py2exe.org/index.cgi/win32com.shell
# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

###################################
# Next ordinary setup.py

from distutils.core import setup
import py2exe
from distutils.core import setup
import py2exe

#mfcdir = "C:\\Python26\\Lib\\site-packages\\pythonwin\\"
#mfcfiles = [mfcdir+"mfc90.dll", mfcdir+"mfc90u.dll",
#		mfcdir+"mfcm90.dll",mfcdir+"mfcm90u.dll",mfcdir+"Microsoft.VC90.MFC.manifest"]

#data_files = [("Microsoft.VC90.MFC", mfcfiles),
#              ]data_files = data_files,
setup(windows=[{"script":"st7b.py"}])
