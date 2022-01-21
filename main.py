import multiprocessing
import os
import install
import links_parser
import links_filter
import selenium_test


def print_menu():
    menu = """
    ----------------------
    1. Restart parser
    2. Start Selenium
    3. Change webdriver
    ----------------------
    """
    print(menu)


def is_file_existing(file):
    if os.path.exists(file):
        return True
    else:
        return False


if __name__ == "__main__":
    # Libs Installer
    # choice = input("Press Enter...")

    # Pyinstaller fix
    multiprocessing.freeze_support()

    is_initial_file = is_file_existing(links_parser.optimized_path("prefBrowser.txt"))
    if not is_initial_file:
        install.main()  # Installer

    loop = True
    while loop:
        print_menu()
        choice = input("Enter your choice [1-2]: ")
        choice = int(choice)

        if choice == 1:
            links_parser.parse()  # Parser links start
            links_filter.generate_filtered_file()  # Apply filter
        elif choice == 2:
            selenium_test.start_test()
        elif choice == 3:
            install.main()  # Installer
