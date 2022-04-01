import subprocess
import sys
from sys import platform
from __dwnldDrivers.versions import *

######## This script is only for educational purpose ########
######## use it on your own RISK ########
######## I'm not responsible for any loss or damage ########
######## caused to you using this script ########
######## Github Repo - https://git.io/JJisT/ ########
from links_parser import optimized_path


def main():
    installed_pr = []

    if platform == "darwin":
        print('Safari\n')
        installed_pr.append('Darwin')

    print('Firefox')
    firefox_ver = get_firefox_version()
    if firefox_ver is not None:
        is_firefox_there = 1
        installed_pr.append('Firefox')
        setup_Firefox(firefox_ver)
    else:
        is_firefox_there = 0
        print('Firefox isn\'t installed')

    print('\nChrome')
    chrome_ver = get_chrome_version()

    if chrome_ver != None:
        is_chrome_there = 1
        installed_pr.append('Chrome')
        setup_Chrome(chrome_ver)
    else:
        is_chrome_there = 0
        print('Chrome isn\'t installed')

    if is_firefox_there == 0 and is_chrome_there == 0:
        print('Error - Setup installation failed \nReason - Please install either Chrome or Firefox browser to '
              'complete setup process')
        exit()

    print('\nWich browser do you prefer to run script on')

    print(installed_pr)
    for index, pr in enumerate(installed_pr, start=1):
        print('\n[*] ' + str(index) + ' ' + pr)

    inpErr = True

    while inpErr != False:
        print(f'\nEnter id ex - 1 or {len(installed_pr)}: ', end='')
        userInput = int(input())

        if userInput <= len(installed_pr) and userInput > 0:
            selected = installed_pr[userInput - 1]
            fp = open(optimized_path('prefBrowser.txt'), 'w')
            fp.write(selected.lower())
            inpErr = False
        else:
            print(f'Wrong id, Either input 1 or {len(installed_pr)}')

    print('Setup Completed')


if __name__ == '__main__':
    main()
