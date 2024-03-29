# ======================================================================= #
#  Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

from __future__ import annotations

import subprocess
import sys
import textwrap
from abc import abstractmethod, ABC
from typing import Dict, Any, Literal, Union, Callable

from core.menus import QUIT_FOOTER, BACK_FOOTER, BACK_HELP_FOOTER
from utils.constants import (
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_RED,
    COLOR_CYAN,
    RESET_FORMAT,
)
from utils.logger import Logger


def clear():
    subprocess.call("clear", shell=True)


def print_header():
    line1 = " [ KIAUH ] "
    line2 = "Klipper Installation And Update Helper"
    line3 = ""
    color = COLOR_CYAN
    count = 62 - len(color) - len(RESET_FORMAT)
    header = textwrap.dedent(
        f"""
        /=======================================================\\
        | {color}{line1:~^{count}}{RESET_FORMAT} |
        | {color}{line2:^{count}}{RESET_FORMAT} |
        | {color}{line3:~^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(header, end="")


def print_quit_footer():
    text = "Q) Quit"
    color = COLOR_RED
    count = 62 - len(color) - len(RESET_FORMAT)
    footer = textwrap.dedent(
        f"""
        |-------------------------------------------------------|
        | {color}{text:^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(footer, end="")


def print_back_footer():
    text = "B) « Back"
    color = COLOR_GREEN
    count = 62 - len(color) - len(RESET_FORMAT)
    footer = textwrap.dedent(
        f"""
        |-------------------------------------------------------|
        | {color}{text:^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(footer, end="")


def print_back_help_footer():
    text1 = "B) « Back"
    text2 = "H) Help [?]"
    color1 = COLOR_GREEN
    color2 = COLOR_YELLOW
    count = 34 - len(color1) - len(RESET_FORMAT)
    footer = textwrap.dedent(
        f"""
        |-------------------------------------------------------|
        | {color1}{text1:^{count}}{RESET_FORMAT} | {color2}{text2:^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(footer, end="")


class BaseMenu(ABC):
    NAVI_OPTIONS = {"quit": ["q"], "back": ["b"], "back_help": ["b", "h"]}

    def __init__(
        self,
        options: Dict[str, Union[Callable, Any]],
        options_offset: int = 0,
        default_option: Union[str, None] = None,
        input_label_txt: Union[str, None] = None,
        header: bool = True,
        previous_menu: BaseMenu = None,
        footer_type: Literal[
            "QUIT_FOOTER", "BACK_FOOTER", "BACK_HELP_FOOTER"
        ] = QUIT_FOOTER,
    ):
        self.previous_menu = previous_menu
        self.options = options
        self.default_option = default_option
        self.options_offset = options_offset
        self.input_label_txt = input_label_txt
        self.header = header
        self.footer_type = footer_type

    @abstractmethod
    def print_menu(self) -> None:
        raise NotImplementedError("Subclasses must implement the print_menu method")

    def print_footer(self) -> None:
        footer_type_map = {
            QUIT_FOOTER: print_quit_footer,
            BACK_FOOTER: print_back_footer,
            BACK_HELP_FOOTER: print_back_help_footer,
        }
        footer_function = footer_type_map.get(self.footer_type, print_quit_footer)
        footer_function()

    def display(self) -> None:
        # clear()
        if self.header:
            print_header()
        self.print_menu()
        self.print_footer()

    def handle_user_input(self) -> str:
        while True:
            label_text = (
                "Perform action"
                if self.input_label_txt is None or self.input_label_txt == ""
                else self.input_label_txt
            )
            choice = input(f"{COLOR_CYAN}###### {label_text}: {RESET_FORMAT}").lower()
            option = self.options.get(choice, None)

            has_navi_option = self.footer_type in self.NAVI_OPTIONS
            user_navigated = choice in self.NAVI_OPTIONS[self.footer_type]
            if has_navi_option and user_navigated:
                return choice

            if option is not None:
                return choice
            elif option is None and self.default_option is not None:
                return self.default_option
            else:
                Logger.print_error("Invalid input!", False)

    def start(self) -> None:
        while True:
            self.display()
            choice = self.handle_user_input()

            if choice == "q":
                Logger.print_ok("###### Happy printing!", False)
                sys.exit(0)
            elif choice == "b":
                return
            else:
                self.execute_option(choice)

    def execute_option(self, choice: str) -> None:
        option = self.options.get(choice, None)

        if isinstance(option, type) and issubclass(option, BaseMenu):
            self.navigate_to_menu(option, True)
        elif isinstance(option, BaseMenu):
            self.navigate_to_menu(option, False)
        elif callable(option):
            option(opt_index=choice)
        elif option is None:
            raise NotImplementedError(f"No implementation for option {choice}")
        else:
            raise TypeError(
                f"Type {type(option)} of option {choice} not of type BaseMenu or Method"
            )

    def navigate_to_menu(self, menu, instantiate: bool) -> None:
        """
        Method for handling the actual menu switch. Can either take in a menu type or an already
        instantiated menu class. Use instantiated menu classes only if the menu requires specific input parameters
        :param menu: A menu type or menu instance
        :param instantiate: Specify if the menu requires instantiation
        :return: None
        """
        menu = menu() if instantiate else menu
        menu.previous_menu = self
        menu.start()
