from src.app import ui
from src.cli import cli_doc

__author__ = 'ShiningZec'


def main():
    print(ui.__author__, cli_doc.__author__, sep=', ')
    print("Hello from classarrangement!")


if __name__ == "__main__":
    main()
