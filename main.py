from checker import timecit
from src.app import ui
from src.cli import cli_util

__author__ = 'ShiningZec'


def main():
    try:
        print(
            "-START PAGE-\n[1] from ui\n[2] from cli\n[3] run timeit\n[0] exit"
        )
        buff: str = input("Select System >> ")
        if not buff:
            print("Boot up Cancelled")
            return
        choice = buff.strip()[0]
        if choice == '1':
            ui.main()
        elif choice == '2':
            cli_util.main()
        elif choice == '3':
            timecit.main()
        elif choice == '0':
            print("Exit.\n")
            return
        else:
            print(f"No such choice:\n{choice}\nExit.\n")
    except KeyboardInterrupt:
        print("\nExit.\n")
        return


if __name__ == "__main__":
    main()
