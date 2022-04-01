import subprocess
import sys

from sys import platform
from helper import optimized_path
from __dwnldDrivers.versions import *


class Installer:
    my_packages = ['requests', 'clint', 'faker', 'selenium', 'beautifulsoup4', "lxml", "colorama", "PyInstaller"]
    installed_pr = []

    @staticmethod
    def __install_package(name):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', name])

    @staticmethod
    def _manual_packages_install():
        for package in Installer.my_packages:
            Installer.__install_package(package)
            print('\n')

    @staticmethod
    def _install_drivers():
        # MacOS
        if platform == "darwin":
            print('Safari\n')
            Installer.installed_pr.append('Darwin')

        print('Firefox')
        firefox_ver = get_firefox_version()
        if firefox_ver is not None:
            is_firefox_there = 1
            Installer.installed_pr.append('Firefox')
            setup_Firefox(firefox_ver)
        else:
            is_firefox_there = 0
            print('Firefox isn\'t installed')

        print('\nChrome')
        chrome_ver = get_chrome_version()

        if chrome_ver is not None:
            is_chrome_there = 1
            Installer.installed_pr.append('Chrome')
            setup_Chrome(chrome_ver)
        else:
            is_chrome_there = 0
            print('Chrome isn\'t installed')

        if is_firefox_there == 0 and is_chrome_there == 0:
            print('Error - Setup installation failed \nReason - Please install either Chrome or Firefox browser to '
                  'complete setup process')
            exit()

        print('\nWich browser do you prefer to run script on')

        print(Installer.installed_pr)
        for index, pr in enumerate(Installer.installed_pr, start=1):
            print('\n[*] ' + str(index) + ' ' + pr)

        inpErr = True

        while inpErr:
            print(f'\nEnter id ex - 1 or {len(Installer.installed_pr)}: ', end='')
            userInput = int(input())

            if len(Installer.installed_pr) >= userInput > 0:
                selected = Installer.installed_pr[userInput - 1]
                fp = open(optimized_path('prefBrowser.txt'), 'w')
                fp.write(selected.lower())
                inpErr = False
            else:
                print(f'Wrong id, Either input 1 or {len(Installer.installed_pr)}')

        print('Setup Completed')

    @staticmethod
    def install_all():
        Installer._manual_packages_install()
        Installer._install_drivers()


if __name__ == '__main__':
    Installer.install_all()
