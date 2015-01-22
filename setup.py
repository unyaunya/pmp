from distutils.core import setup
import py2exe
setup(windows=[{"script":"pmp\main.py"}], options={"py2exe":{"includes":["sip"]}})
