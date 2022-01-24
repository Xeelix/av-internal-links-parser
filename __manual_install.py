import subprocess
import sys

def install(name):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', name])

my_packages = ['requests', 'clint', 'faker', 'selenium', 'beautifulsoup4', "lxml", "colorama", "PyInstaller"]

for package in my_packages:
    install(package)
    print('\n')
