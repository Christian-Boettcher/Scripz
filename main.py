#!/usr/bin/env python3

"""
:'######:::'######::'########::'####:'########::'########:
'##... ##:'##... ##: ##.... ##:. ##:: ##.... ##:..... ##::
 ##:::..:: ##:::..:: ##:::: ##:: ##:: ##:::: ##::::: ##:::
. ######:: ##::::::: ########::: ##:: ########::::: ##::::
:..... ##: ##::::::: ##.. ##:::: ##:: ##.....::::: ##:::::
'##::: ##: ##::: ##: ##::. ##::: ##:: ##::::::::: ##::::::
. ######::. ######:: ##:::. ##:'####: ##:::::::: ########:
:......::::......:::..:::::..::....::..:::::::::........::

__________________________________________________________

Author: CBoettcher
Version: v0.0.3
Description:
Simple python powered GUI for storing scripts or plain text entries in an organized fashion.

"""

__author__ = "CBoettcher"
__version__ = "v0.0.3"

import flet as ft
import google.generativeai as genai
import json
import os
import time
import requests
import logging
import shutil
import sys
import atexit
import subprocess

ENV_FILE = "data\\profile.env"
LOG_FILE = "data\\scripz.log"
SCRIPTS_FILE = "data\\scripts.json"
GITHUB_API = f"https://api.github.com/repos/Christian-Boettcher/Scripz/releases/latest"
SETTINGS = {}
SCRIPT_OBJECTS = {}
DEFAULT_TYPES = [
    "ASP.NET",
    "Bash",
    "C",
    "C#",
    "C++",
    "CSS",
    "Cmd",
    "Dart",
    "Django",
    "Docker File",
    "Go",
    "HTML",
    "HTTP",
    "JSON",
    "JSP",
    "JSX",
    "Java",
    "Javascript",
    "Lua",
    "Other",
    "PHP",
    "Perl",
    "Powershell",
    "Python",
    "Ruby",
    "SQL",
    "Swift",
    "Text",
    "Typescript",
    "VB",
    "VBScript",
    "XML",
    "YAML"]
SCRIPT_TYPE_OPTIONS = []
GEMINI_API_KEY = ""
FIRST_START = True
GEMINI_ENABLED = False


def handle_update():
    """
    Performs the update process for the program.

    This function moves the 'Scripz.exe' file from the '.\\data\\' directory to the current directory,
    logs the update process, stops the program, starts the update process, and then launches the updated program.

    Note:
    - This function assumes that 'log_info' and 'shutil' modules have been imported.
    - This function assumes that 'os' and 'subprocess' modules are available.

    Raises:
    No explicit exceptions are raised within this function. However, it may raise exceptions
    related to file operations, subprocess management, or other system-related errors.

    Returns:
    None
    """
    log_info("Update in process...")  # Log update process initiation
    shutil.move(os.path.join(".\\data\\", 'Scripz.exe'),
                os.path.dirname(__file__) + "\\Scripz.exe")  # Move Scripz.exe to current directory
    log_info("Program stopped.")  # Log program stop
    log_info("Update completed")  # Log update completion
    # Configure subprocess startup info to hide the window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # Launch the updated program
    subprocess.Popen(os.path.dirname(__file__) + "\\Scripz.exe", startupinfo=startupinfo)


def setup_logger():
    """
    Sets up logging configuration for the program.

    This function creates a 'data' directory if it doesn't exist, initializes a 'scripz.log' file if it's not present,
    configures a logger to log both to the file and the console with appropriate formatting, and sets the logging level to INFO.

    Note:
    - This function assumes that 'os' and 'logging' modules have been imported.

    Raises:
    No explicit exceptions are raised within this function. However, it may raise exceptions related to file operations
    or other system-related errors while creating directories or files.

    Returns:
    None
    """
    global LOG_FILE
    if not os.path.isdir("data"):
        os.mkdir("data")  # Create 'data' directory if it doesn't exist
    if not os.path.exists(LOG_FILE):
        # Initialize 'scripz.log' file if it doesn't exist
        with open(LOG_FILE, 'a') as file:
            file.writelines("Initialized\n")

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set logger level to DEBUG

    # Create file handler and set level to INFO
    file_handler = logging.FileHandler(LOG_FILE, mode='a')
    file_handler.setLevel(logging.INFO)

    # Create console handler and set level to INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %H:%M:%S')

    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_error(message):
    logging.error(message)


def log_info(message):
    logging.info(message)


def load_env_file():
    """
        Loads environment variables from a file and populates the SETTINGS dictionary.

        This function attempts to load environment variables from a file specified by ENV_FILE.
        It reads each line in the file, expecting a key-value pair separated by '=',
        and populates a dictionary with these key-value pairs.
        Additionally, it assigns these variables to the SETTINGS dictionary.
        If the file doesn't exist, it creates it with default values and logs the event.
        In case of a FileNotFoundError, it logs the error and creates the file with default values.

        Note:
        - This function assumes that 'ENV_FILE', 'SETTINGS', and 'log_error' modules are defined.
        - Default values for the environment variables are assumed to be present in the except block.

        Raises:
        No explicit exceptions are raised within this function. However, it may raise exceptions
        related to file operations or other system-related errors while reading or creating the file.

        Returns:
        dict: A dictionary containing loaded environment variables.
        """
    try:
        env_vars = {}
        with open(ENV_FILE, 'r') as file:
            for line in file:
                # Split each line into key and value
                key, value = line.strip().split('=', 1)
                env_vars[key] = value
                SETTINGS[key] = value
        return env_vars

    except FileNotFoundError:
        # If the file doesn't exist, return an empty dictionary
        log_error(f".\\{ENV_FILE} not found.")
        # Write the modified contents back to the file
        with open(ENV_FILE, 'w') as file:
            file.writelines("GEMINI_ENABLED=False\nGEMINI_API_KEY=\nTHEME=dark\n")
            log_info(f".\\{ENV_FILE} created.")
        return {}


def update_env_file(key, value):
    """
        Updates or adds a key-value pair in the environment file specified by ENV_FILE.

        This function attempts to read the contents of the environment file specified by ENV_FILE.
        If the file exists, it updates the existing key-value pair if the key is found; otherwise, it adds a new key-value pair.
        If the file doesn't exist, it creates the file with the new key-value pair.
        The function logs relevant information about file creation and key-value addition or modification.

        Args:
        key (str): The key to be updated or added in the environment file.
        value (str): The value corresponding to the key.

        Note:
        - This function assumes that 'ENV_FILE', 'log_error', and 'log_info' modules are defined.

        Raises:
        No explicit exceptions are raised within this function. However, it may raise exceptions
        related to file operations or other system-related errors while reading or writing to the file.

        Returns:
        None
        """
    try:
        # Read the contents of the file
        with open(ENV_FILE, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        # If the file doesn't exist, create it with the new key-value pair
        log_error(f".\\{ENV_FILE} not found. Creating it and adding the new values...")
        lines = []

    # Update or add the key-value pair
    found = False
    for i, line in enumerate(lines):
        if line.startswith(key + '='):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}\n")

    # Write the modified contents back to the file
    with open(ENV_FILE, 'w') as file:
        file.writelines(lines)
    if found:
        log_info(f"Updated key '{key}' in .\\{ENV_FILE} to {value}.")
    else:
        log_info(f"Added key '{key}' to .\\{ENV_FILE} with a value of {value}.")


class AppHeader(ft.Container):
    def __init__(self, page):
        self.page = page
        self.container = None
        super().__init__()
        self.expand = True
        self.on_hover = lambda e: self.show_search_bar(e)
        self.height = 60
        self.bgcolor = "Transparent"
        self.border_radius = ft.border_radius.only(top_left=15, top_right=15)
        self.padding = ft.padding.only(left=15, right=15)
        self.content = ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.category_drawer_toggle(),
                    self.app_header_search(),
                    self.theme_toggle(),
                ],
            )
        self.build()

    def category_drawer_toggle(self):
        return ft.Container(
            content=ft.IconButton(
                icon="menu",
                on_click=lambda e: self.open_drawer(e),
            ),
        )

    def app_header_search(self):
        return ft.Container(
            width=400,
            bgcolor='white10',
            border_radius=6,
            opacity=0,
            animate_opacity=320,
            padding=8,
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(name=ft.icons.SEARCH_ROUNDED, size=17, opacity=0.85, color="white", ),
                    ft.TextField(
                        border_color='transparent',
                        height=20,
                        text_size=14,
                        content_padding=0,
                        cursor_color="white",
                        cursor_width=1,
                        color="white",
                        hint_text="Search",
                        hint_style=ft.TextStyle(color="white10", weight=ft.FontWeight.NORMAL),
                        on_change=lambda e: self.container.search(e.control),
                    ),
                    ft.IconButton(
                        icon=ft.icons.CLOSE_ROUNDED,
                        icon_size=17,
                        icon_color="white",
                        opacity=0.85,
                        tooltip="Clear",
                        on_click=lambda e: self.clear_search_bar(e)
                    )
                ]
            )
        )

    def open_drawer(self, e):
        self.page.drawer.open = True
        self.page.update()

    def show_search_bar(self, e):
        if e.data == 'true':
            self.content.controls[1].opacity = 1
            self.content.controls[1].content.controls[1].focus()
            self.content.controls[1].update()
        elif isinstance(e, ft.KeyboardEvent):
            self.content.controls[1].opacity = 1
            self.content.controls[1].content.controls[1].focus()
            self.content.controls[1].update()
        else:
            self.content.controls[1].opacity = 0
            self.content.controls[1].update()

    def clear_search_bar(self, e):
        self.content.controls[1].content.controls[1].value = ""
        self.content.controls[1].update()
        self.container.search(self.content.controls[1].content.controls[1])

    def change_theme(self, e):
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
        self.content.controls[2].selected = not self.content.controls[2].selected
        update_env_file("THEME", self.page.theme_mode)
        self.update()
        self.page.update()

    def theme_toggle(self):
        return ft.IconButton(
                on_click=lambda e: self.change_theme(e),
                icon="light_mode",
                selected_icon="dark_mode",
                style=ft.ButtonStyle(
                    color={"": ft.colors.WHITE, "selected": ft.colors.BLACK}
                )
            )


class AppFooter(ft.Container):
    def __init__(self, page):
        self.page = page
        super().__init__()
        self.content = ft.Container(
            expand=True,
            height=22,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.icons.SETTINGS_OUTLINED,
                            on_click=lambda e: self.page.dialog.open_dialog(dialog_title="Settings",
                                                                            dialog_type="settings", )
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            f'{__version__}',
                            text_align=ft.TextAlign.END,
                        ),
                    ),
                ],
            )
        )
        self.build()


class CustomDialog(ft.AlertDialog):
    def __init__(self, page, container):
        super().__init__()
        global GEMINI_ENABLED
        self.page = page
        self.container = container
        self.title = ft.Text()
        self.get_started_text = ft.Text(
            "Get Started!",
            offset=ft.transform.Offset(0, 0),
            animate_offset=ft.animation.Animation(
                duration=600,
                curve=ft.AnimationCurve("decelerate"),
            ),
            animate_opacity=200,
            weight=ft.FontWeight.BOLD,
        )
        self.get_started_button = ft.IconButton(
            icon=ft.icons.ARROW_RIGHT_OUTLINED,
            icon_color=ft.colors.WHITE,
            offset=ft.transform.Offset(0, 0),
            animate_offset=ft.animation.Animation(
                duration=600,
                curve=ft.AnimationCurve("decelerate"),
            ),
            scale=ft.Scale(scale=1),
            animate_scale=ft.animation.Animation(
                duration=600,
                curve=ft.AnimationCurve("decelerate"),
            ),
            disabled=True,
        )
        self.api_switch = ft.Switch(
            value=GEMINI_ENABLED,
            label="Enable Gemini",
            on_change=lambda e: self.toggle_api_input(e),
        )
        self.api_input = ft.TextField(
            label="API Key",
            hint_text="API Key Here",
            visible=GEMINI_ENABLED,
            value="",
            adaptive=True,
        )
        self.api_link = ft.TextButton(
            text="Need API Key?",
            on_click=lambda e: self.page.launch_url("https://aistudio.google.com/app/apikey"),
            visible=GEMINI_ENABLED,
        )
        self.update_button = ft.TextButton(
            text="Check for Updates",
            icon=ft.icons.UPDATE,
            on_click=lambda e: self.check_latest_version(e),
        )
        self.confirm_button = ft.TextButton(disabled=True)
        self.close_button = ft.TextButton()

    def build(self):
        pass

    def open_welcome_dialog(self, e):
        self.dismiss_dialog()
        self.page.drawer.open = True
        self.page.update()

    def get_started_hovered(self, e):
        if e.data == "true":
            self.get_started_button.offset = ft.transform.Offset(1.25, 0)
            self.get_started_text.offset = ft.transform.Offset(1, 0)
            self.get_started_text.opacity = 0
            self.get_started_button.scale = ft.transform.Scale(1.25)
            self.page.update()
        else:
            self.get_started_button.offset = ft.transform.Offset(0, 0)
            self.get_started_text.offset = ft.transform.Offset(0, 0)
            self.get_started_text.opacity = 100
            self.get_started_button.scale = ft.transform.Scale(1)
            self.page.update()

    def toggle_api_input(self, e):
        self.api_input.visible = not self.api_input.visible
        self.api_link.visible = not self.api_link.visible
        self.update()
        self.page.update()

    def save_settings(self):
        global GEMINI_API_KEY
        global GEMINI_ENABLED
        GEMINI_API_KEY = self.api_input.value
        GEMINI_ENABLED = self.api_switch.value
        self.api_input.error_text = ""
        if GEMINI_API_KEY == "" and GEMINI_ENABLED is True:
            self.api_input.error_text = "Must not be empty!"
            self.update()
        elif GEMINI_API_KEY != "" and GEMINI_ENABLED is True:
            self.container.generate_description_button.visible = not self.container.generate_description_button.visible
            update_env_file("GEMINI_API_KEY", self.api_input.value)
            update_env_file("GEMINI_ENABLED", self.api_switch.value)
            self.update()
            self.dismiss_dialog()
        elif GEMINI_API_KEY != "" and GEMINI_ENABLED is False:
            self.container.generate_description_button.visible = not self.container.generate_description_button.visible
            update_env_file("GEMINI_API_KEY", self.api_input.value)
            update_env_file("GEMINI_ENABLED", self.api_switch.value)
            self.update()
            self.dismiss_dialog()
        else:
            self.update()
            self.dismiss_dialog()

    def open_dialog(self, dialog_title=None, dialog_type=None, dialog_message=None, function_ref=None):
        global GEMINI_API_KEY
        self.title.value = dialog_title
        temp_list = []
        temp_list.clear()

        if dialog_type == "start_up":
            self.content = ft.Column(
                [
                    ft.Text(value="Get started by creating a category", size=15, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.Container(
                                width=200,
                                height=45,
                                bgcolor=ft.colors.GREEN_ACCENT_700,
                                border_radius=10,
                                on_hover=lambda e: self.get_started_hovered(e),
                                on_click=lambda e: self.open_welcome_dialog(e),
                                content=ft.Row(
                                    [
                                        self.get_started_button,
                                        self.get_started_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                tight=True,
                spacing=25,
                alignment=ft.MainAxisAlignment.END
            )
            self.open = True
            self.page.update()

        elif dialog_type == "download_notify":
            if function_ref:
                self.close_button.text = "Cancel"
                self.close_button.on_click = lambda e: self.dismiss_dialog()
                self.confirm_button.disabled = False
                self.confirm_button.text = "Download"
                self.confirm_button.icon = ft.icons.DOWNLOAD_OUTLINED
                self.confirm_button.on_click = lambda e: function_ref()
                temp_list.append(ft.Text(value=dialog_message))
                temp_list.append(
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    )
                )
                self.content = ft.Column(temp_list, tight=True)
                self.open = True
                self.page.update()
            else:
                self.content = ft.Text(dialog_message)
                self.open = True
                self.page.update()

        elif dialog_type == "user_input":
            self.confirm_button.disabled = True
            self.close_button.text = "Cancel"
            self.close_button.on_click = lambda e: self.dismiss_dialog()
            self.confirm_button.disabled = False
            self.confirm_button.text = "Submit"
            self.confirm_button.icon = ft.icons.SEND_OUTLINED
            self.confirm_button.on_click = lambda e: self.submit_user_variables(dialog_message, input_fields)
            input_fields = []
            # Check if the message contains curly braces
            if "{{" in dialog_message and "}}" in dialog_message:
                # Extract the values between curly braces
                start_index = dialog_message.find("{{") + 2
                while start_index > 1:
                    end_index = dialog_message.find("}}", start_index)
                    if end_index == -1:
                        break
                    extracted_value = dialog_message[start_index:end_index]

                    # Create an input field with the extracted value as the label
                    input_field = ft.TextField(label=extracted_value)
                    input_fields.append(input_field)

                    start_index = dialog_message.find("{{", end_index) + 2  # Move to the next value

            # Set up the dialog with input fields (if any)
            if input_fields:
                for input_field in input_fields:
                    input_field.on_submit = lambda e: self.submit_user_variables(dialog_message, input_fields)
                input_fields.append(
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button
                        ],
                        alignment=ft.MainAxisAlignment.END
                    ),
                )
                self.title.value = "Input Fields"
                self.content = ft.Column(input_fields, tight=True)
                self.actions_alignment = ft.MainAxisAlignment.END
                self.open = True
                self.page.update()

            # Timed Notification
            else:
                self.title.value = "Copied to clipboard"
                self.page.set_clipboard(dialog_message)
                self.content = ft.Text(value=dialog_message, text_align=ft.TextAlign.CENTER, )
                self.page.dialog.open = True
                self.page.update()
                time.sleep(2)
                self.dismiss_dialog()

        elif dialog_type == "new_script":
            if isinstance(dialog_message, list):
                self.confirm_button.disabled = True
                self.close_button.text = "Cancel"
                self.close_button.on_click = lambda e: self.dismiss_dialog(temp_list)
                self.confirm_button.text = "Save"
                self.confirm_button.icon = ft.icons.SAVE_OUTLINED
                self.confirm_button.on_click = lambda e: function_ref()
                for x in dialog_message:
                    temp_list.append(x)
                temp_list.append(
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    )
                )
                self.content = ft.Column(temp_list, width=self.page.window_width, )
            self.open = True
            self.page.update()

        elif dialog_type == "edit_script":
            if isinstance(dialog_message, list):
                self.confirm_button.disabled = False
                self.close_button.text = "Cancel"
                self.close_button.on_click = lambda e: function_ref[1](e)
                self.confirm_button.text = "Save"
                self.confirm_button.icon = ft.icons.SAVE_OUTLINED
                self.confirm_button.on_click = lambda e: function_ref[0](e)
                for x in dialog_message:
                    temp_list.append(x)
                temp_list.append(
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    )
                )
                self.content = ft.Column(temp_list, width=self.page.window_width)
            self.open = True
            self.page.update()

        elif dialog_type == "delete_script":
            self.close_button.text = "Cancel"
            self.close_button.on_click = lambda e: self.dismiss_dialog()
            self.confirm_button.disabled = False
            self.confirm_button.text = "Delete"
            self.confirm_button.icon = ft.icons.DELETE_OUTLINE
            self.confirm_button.on_click = lambda e: function_ref()
            self.content = ft.Column(
                [
                    ft.Text(
                        value=dialog_message,
                        color=ft.colors.RED,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    )
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            self.content.tight = True
            self.open = True
            self.page.update()

        elif dialog_type == "delete_category":
            self.close_button.text = "Cancel"
            self.close_button.on_click = lambda e: self.dismiss_dialog()
            self.confirm_button.disabled = False
            self.confirm_button.text = "Delete"
            self.confirm_button.icon = self.confirm_button.icon = ft.icons.DELETE_OUTLINE
            self.confirm_button.on_click = lambda e: function_ref()
            self.content = ft.Column(
                [
                    ft.Divider(),
                    ft.Text(
                        value=f'Do you really want to delete the {dialog_message.label} category?',
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        value="This will also remove all scripts stored under this category!",
                        color=ft.colors.RED,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            self.open = True
            self.page.update()

        elif dialog_type == "rename_category":
            new_label_input = ft.TextField(value=dialog_message.label,
                                           on_submit=lambda e: function_ref(dialog_message, new_label_input.value))
            self.close_button.text = "Cancel"
            self.close_button.on_click = lambda e: self.dismiss_dialog()
            self.confirm_button.disabled = False
            self.confirm_button.text = "Save"
            self.confirm_button.icon = ft.icons.SAVE_OUTLINED
            self.confirm_button.on_click = lambda e: function_ref(dialog_message, new_label_input.value)
            self.content = ft.Column(
                [
                    new_label_input,
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            self.open = True
            self.page.update()

        elif dialog_type == "settings":
            self.close_button.text = "Close"
            self.close_button.on_click = lambda e: self.dismiss_dialog()
            self.confirm_button.disabled = False
            self.confirm_button.text = "Save"
            self.confirm_button.icon = ft.icons.SAVE_OUTLINED
            self.confirm_button.on_click = lambda e: self.save_settings()
            self.content = ft.Column(
                [
                    ft.ResponsiveRow(
                        [
                            self.api_input,
                            self.api_switch,
                        ],
                    ),
                    self.api_link,
                    self.update_button,
                    ft.Row(
                        [
                            self.close_button,
                            self.confirm_button
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    )
                ],
                tight=True,
                spacing=25,
                alignment=ft.MainAxisAlignment.END,
                width=self.page.window_width / 2,
            )
            if GEMINI_API_KEY:
                self.api_input.value = GEMINI_API_KEY
            self.open = True
            self.page.update()

    def dismiss_dialog(self, controls=None):
        if GEMINI_API_KEY == "" and GEMINI_ENABLED is True:
            self.api_switch.value = False
            self.toggle_api_input(None)
        if controls:
            for x in controls:
                if isinstance(x, ft.TextField):
                    x.value = ""
                    x.error_text = ""
                elif isinstance(x, ft.Dropdown):
                    x.value = ""
                    x.error_text = ""
                elif isinstance(x, ft.Row):
                    for i in x.controls:
                        if isinstance(i, ft.TextField):
                            i.value = ""
                            i.error_text = ""
                        elif isinstance(i, ft.Column):
                            i.controls[0].value = f"""

```

```
"""
        self.open = False
        self.update()
        self.page.update()

    def submit_user_variables(self, message, input_fields):
        """
        Submits user variables and performs necessary actions.

        Parameters:
        - self: The instance of the class.
        - message (str): The message to be processed.
        - input_fields (list): A list of input fields.

        Description:
        - This function takes a message and a list of input fields as parameters.
        - It extracts user values from the input fields and replaces placeholders in the message with those values.
        - The modified message is then set to the clipboard, and a dialog is dismissed.
        - Finally, a new dialog of type "user_input" is opened with the modified message.

        Example Usage:
        submit_user_variables(self, "Get-ADUser {{Username}}", [Username])
        """
        user_values = {}
        final_message = message
        for field in input_fields:
            if isinstance(field, ft.TextField):
                user_values[field.label] = field.value
            for key, value in user_values.items():
                final_message = final_message.replace("{{" + key + "}}", value)
        self.page.set_clipboard(final_message)
        self.dismiss_dialog()
        self.open_dialog(dialog_type="user_input", dialog_message=final_message)

    def check_latest_version(self, e):
        global GITHUB_API
        log_info("Checking for latest version...")
        try:
            response = requests.get(GITHUB_API)
            if response.status_code == 404:
                log_error(f"Repository 'Christian-Boettcher/Scripz' not found or no releases available.")
                return
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release["tag_name"]

            if latest_version == __version__:
                self.dismiss_dialog()
                self.open_dialog(
                    "Up to date!",
                    "download_notify",
                    "You are using the latest version.",
                    None
                )
                log_info("Already using latest version.")
            else:
                assets = latest_release["assets"]
                if len(assets) > 0:
                    asset_url = assets[0]["browser_download_url"]
                    self.dismiss_dialog()
                    self.open_dialog(
                        "Update!",
                        "download_notify",
                        f"There is a newer version ({latest_version}) available.",
                        lambda: self.download_update(latest_version, asset_url)
                    )
                    log_info(f"There is a newer version ({latest_version}) available.")
                else:
                    log_error("No assets found for the latest release.")
        except requests.exceptions.RequestException as e:
            log_error(e)

    def download_update(self, version, file_url):
        self.dismiss_dialog()
        log_info(f"Downloading the latest version ({version})...")
        filename = os.path.join(".\\data\\", os.path.basename(file_url))
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            with open(filename, 'wb') as file:
                file.write(response.content)
            self.open_dialog(
                "Update Downloaded!",
                "download_notify",
                f"Downloaded Scripz {version} successfully.\nPlease close Scripz to complete the update.",
                None
            )
            log_info(f"Downloaded '{filename}' successfully.")

            atexit.register(handle_update)
            sys.exit()
        except requests.exceptions.RequestException as e:
            log_error(e)


class CategoryDrawer(ft.NavigationDrawer):
    def __init__(self, page, script_container):
        super().__init__()
        self.page = page
        self.script_container = script_container
        self.add_button = ft.IconButton(
            icon=ft.icons.ADD,
            selected_icon=ft.icons.CANCEL,
            on_click=self.add_nav_option_clicked,
            style=ft.ButtonStyle(
                color={"": ft.colors.GREEN, "selected": ft.colors.RED},
            ),
            tooltip="Add New Category",
        )
        self.new_category_input = ft.TextField(
            label="New Category",
            visible=False,
            hint_text="Category name",
            on_submit=self.add_nav_option,
            autofocus=True,
            scale=0.80,
        )

    def build(self):
        self.controls = [
            self.add_button,
            self.new_category_input,
            ft.Divider(),
        ]
        self.on_change = self.change_page

    def change_page(self, e):
        """
        Changes the page and performs necessary actions.

        Parameters:
        - self: The instance of the class.
        - e: The event triggering the page change.

        Description:
        - This function changes the page and performs several actions.
        - It cleans the scripts in the script container, updates the page and script container, and iterates through the controls.
        - If a control is a ft.NavigationDrawerDestination and its index matches the selected index, it retrieves the corresponding category from SCRIPT_OBJECTS.
        - For each script object in the category, it adds a ft.DragTarget with a ft.Draggable containing the script object to the script container.
        - It updates the script container's container_title with the category name and updates the page and script container.
        - If the 'e' parameter is not None, it sets the 'open' attribute to False.
        - Finally, it updates the instance.

        """
        global SCRIPT_OBJECTS
        self.script_container.scripts.clean()
        self.page.update()
        for control in self.controls:
            if isinstance(control, ft.NavigationDrawerDestination):
                if self.controls.index(control) - 3 == self.selected_index:
                    for category in SCRIPT_OBJECTS:
                        if category == self.controls[self.controls.index(control)].__getattribute__(
                                "label"):
                            for script_object in SCRIPT_OBJECTS.get(category):
                                self.script_container.scripts.controls.append(
                                    ft.DragTarget(
                                        content=ft.Draggable(
                                            content=ScriptObject(
                                                self.script_container,
                                                script_object.get("script_type"),
                                                script_object.get("script_name"),
                                                script_object.get("script_value"),
                                                script_object.get("script_description"),
                                            )
                                        ),
                                        on_accept=self.script_container.accept_drop
                                    )
                                )
                            self.script_container.container_title.value = category
                            self.script_container.container_title.update()
                    self.page.update()
                    self.script_container.update()
                    self.open = False
                    self.update()
        if e is not None:
            self.open = False

    def update_nav_options(self):
        """
        Updates the navigation options based on the controls in the page.

        Description:
        - This function iterates through the controls and updates the navigation options based on their position in the list of controls.
        - It enables or disables the UP and DOWN options for each control based on its position.

        """
        for control in self.controls:
            if isinstance(control, ft.NavigationDrawerDestination):
                up = self.controls[self.controls.index(control)].__getattribute__("icon_content").controls[0].items[2]
                down = self.controls[self.controls.index(control)].__getattribute__("icon_content").controls[0].items[3]
                # If only 1 category
                if len(self.controls) == 4:
                    up.disabled = True
                    down.disabled = True

                # If the category is at the bottom
                elif self.controls.index(control) == len(self.controls) - 1:
                    up.disabled = False
                    down.disabled = True

                # If the category is at the top
                elif self.controls.index(control) == 3:
                    up.disabled = True
                    down.disabled = False

                # If the category is anywhere in between
                else:
                    up.disabled = False
                    down.disabled = False
        self.page.update()

    def add_nav_option(self, e):
        """
        Adds a navigation option to the navigation drawer.

        Description:
            - This function is called when a button is clicked to add a navigation option to the navigation drawer.
            - It creates a new instance of `ft.NavigationDrawerDestination` with the provided label and icon content.

            The function performs several actions:
            - Sets the `selected` attribute of the `add_button` to False.
            - Creates a new `ft.NavigationDrawerDestination` instance with the provided label and icon content.
            - Appends the new instance to the `controls` list.
            - Updates the navigation options using the `update_nav_options` method.
            - Writes the JSON file with the updated category information.
            - Updates the selected index and triggers an update.
            - Sets the visibility of the `add_script_button` to True.
            - Changes the page to the newly added category.
            - Sets the visibility of the `new_category_input` to False.
            -  Resets the value of the `new_category_input` to an empty string.
            -  Updates the script container and the page.

        Parameters:
            - e: The event object containing information about the button click.

        """
        global SCRIPT_OBJECTS
        if e.control.value != "":
            self.add_button.selected = False
            self.controls.append(CategoryNav(self.page, self, self.new_category_input.value))
            self.update_nav_options()
            self.script_container.write_json_file(category=self.new_category_input.value)
            self.selected_index = list(SCRIPT_OBJECTS).index(self.new_category_input.value)
            self.script_container.add_script_button.visible = True
            self.change_page(None)
            self.new_category_input.visible = False
            self.new_category_input.value = ""
            self.script_container.update()
            self.page.update()
        else:
            self.add_button.selected = False
            self.new_category_input.visible = False
            self.page.update()

    def add_nav_option_clicked(self, e):
        self.new_category_input.visible = not self.new_category_input.visible
        e.control.selected = not e.control.selected
        if e.control.selected:
            e.control.tooltip = "Cancel"
        else:
            self.new_category_input.value = ""
            e.control.tooltip = "Add New Category"
        self.page.update()

    def rename_nav_option(self, event, category_object):
        """
        Renames a navigation option in the ft.NavigationDrawer.

        Parameters:
            - event: The event that triggered the function.
            - category_object: The category object to be renamed.

        """
        self.page.dialog.open_dialog(
            dialog_title="Rename Category",
            dialog_type="rename_category",
            dialog_message=category_object,
            function_ref=lambda ref=category_object, new_label=None: self.confirm_rename_category(ref, new_label)
        )

    def confirm_rename_category(self, ref, new_label):
        """
        Renames a category and updates the necessary attributes.

        Parameters:
            - ref (object): The reference object.
            - new_label (str): The new label for the category.

        """
        global SCRIPT_OBJECTS
        item_to_rename = None
        for category in SCRIPT_OBJECTS:
            if category == ref.label:
                item_to_rename = category
        SCRIPT_OBJECTS = {new_label if k == item_to_rename else k: v for k, v in SCRIPT_OBJECTS.items()}
        index = self.controls.index(ref)
        self.controls.remove(ref)
        self.controls.insert(index, CategoryNav(page=self.page, drawer=self, category_name=new_label))
        self.update_nav_options()
        self.script_container.write_json_file(update=True)

        if index - 3 == self.selected_index:
            self.script_container.container_title.value = new_label
            self.script_container.container_title.update()
        self.page.dialog.dismiss_dialog()

    def remove_nav_option(self, event, category_object):
        """
        Removes a navigation option and opens a confirmation dialog.

        Parameters:
            - event (object): The event object.
            - category_object (str): The label of the category to be removed.

        """
        self.page.dialog.open_dialog(
            dialog_title="Please confirm",
            dialog_type="delete_category",
            dialog_message=category_object,
            function_ref=lambda ref=category_object: self.confirm_remove_category(ref)
        )

    def confirm_remove_category(self, ref):
        """
        Removes a category from the navigation options and updates the necessary attributes.

        Description:
            - This method is called when confirming the removal of a category from the navigation options.
            - It removes the specified category from the list of controls in the navigation drawer,
            updates the global SCRIPT_OBJECTS dictionary by removing the corresponding category,
            and performs additional updates and checks.

        Parameters:
            - ref (object): The reference object representing the category to be removed.

        """
        global SCRIPT_OBJECTS
        self.controls.pop(self.controls.index(ref))
        item_to_remove = None
        for category in SCRIPT_OBJECTS:
            if category == ref.label:
                item_to_remove = category
        SCRIPT_OBJECTS.pop(item_to_remove)
        self.script_container.write_json_file(update=True)
        self.script_container.scripts.clean()
        if len(self.controls) >= 4:
            self.selected_index = 0
            self.change_page(None)
        else:
            self.script_container.container_title.value = "Scripz"
            self.script_container.add_script_button.visible = False

        self.update_nav_options()
        self.script_container.update()
        self.page.dialog.dismiss_dialog()

    def move_nav_option(self, event, category_object, direction):  # TODO Update json to reflect changes.
        """
        Moves a navigation option (category) up or down within the navigation drawer.

        Parameters:
            - event: The event triggered by the user action.
            - category_object: The category object to be moved.
            - direction: The direction to move the category. It can be either "up" or "down".

        Description:
            - This function is called when the user wants to move a category up or down within the navigation drawer.
            - It takes the event, category_object, and direction as parameters.
            - It searches for the category_object within the self.controls list and performs the requested movement.
            - If the direction is "up", the category is moved one position up in the list.
            - If the direction is "down", the category is moved one position down in the list.
            - After the movement, the function updates the navigation drawer and the page.

        """
        is_selected = False
        if self.controls.index(category_object) - 3 == self.selected_index:
            is_selected = True
        if direction == "up":
            self.move_category_to_index(self.controls, category_object, self.controls.index(category_object) - 1)
            if is_selected:
                self.selected_index = self.controls.index(category_object) - 3
                self.change_page(None)

        elif direction == "down":
            self.move_category_to_index(self.controls, category_object, self.controls.index(category_object) + 1)
            if is_selected:
                self.selected_index = self.controls.index(category_object) - 3
                self.change_page(None)

        self.page.update()

    def move_category_to_index(self, controls_list, element, target_index):
        if element in controls_list:
            controls_list.remove(element)
            controls_list.insert(target_index, element)
            self.update_nav_options()
            self.change_page(None)

    def update_drawer(self):
        """
        Updates the navigation drawer with the categories from SCRIPT_OBJECTS.

        Description:
            -This function is called to update the navigation drawer with the categories from SCRIPT_OBJECTS.

            -It iterates over each object_category in SCRIPT_OBJECTS and
            appends a CategoryNav control to self.controls with the corresponding category_name.

            -If the number of controls in self.controls is greater than or equal to 4, it sets the visibility of the
            add_script_button to True and updates the navigation options.

            -Finally, it updates the page.

        """
        if SCRIPT_OBJECTS:
            for object_category in SCRIPT_OBJECTS:
                self.controls.append(CategoryNav(page=self.page, drawer=self, category_name=object_category))

        if len(self.controls) >= 4:
            self.script_container.add_script_button.visible = True
            self.update_nav_options()
            self.change_page(None)
        self.page.update()


class CategoryNav(ft.NavigationDrawerDestination):
    def __init__(self, page, drawer, category_name):
        super().__init__()
        self.page = page
        self.category_name = category_name
        self.drawer = drawer
        self.label = self.category_name
        self.icon_content = ft.Row(
            [
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            icon=ft.icons.EDIT,
                            text="Rename",
                            on_click=lambda event, category_object=self: self.drawer.rename_nav_option(event,
                                                                                                       category_object)
                        ),

                        ft.PopupMenuItem(
                            icon=ft.icons.DELETE_OUTLINE,
                            text="Delete",
                            on_click=lambda event, category_object=self: self.drawer.remove_nav_option(event,
                                                                                                       category_object)
                        ),

                        ft.PopupMenuItem(
                            icon=ft.icons.MOVE_UP,
                            text="Move Up",
                            on_click=lambda event, category_object=self, direction="up": self.drawer.move_nav_option(
                                event, category_object, direction),
                            disabled=True,
                        ),

                        ft.PopupMenuItem(
                            icon=ft.icons.MOVE_DOWN,
                            text="Move Down",
                            on_click=lambda event, category_object=self, direction="down": self.drawer.move_nav_option(
                                event, category_object, direction),
                            disabled=True,
                        ),
                    ],
                ),
                ft.Icon(ft.icons.TEXT_SNIPPET_OUTLINED, ),
            ]
        )

    def build(self):
        return self


class ScriptObject(ft.UserControl):  # TODO Refactor to meet version 22 changes, UserControl is deprecated
    def __init__(self, parent, script_type, script_name, script_value, description):
        super().__init__()
        self.parent = parent
        self.script_type = script_type
        self.script_name = script_name
        self.script_value = script_value
        self.description = description
        self.delete_script = self.parent.delete_script
        self.open_dialog = self.parent.page.dialog.open_dialog
        self.markdown_render = ft.Markdown(
            value=None,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono"),
        )
        self.display_script_name = ft.Tooltip(
            message=f'Type: {self.script_type}\nDescription: {self.description}\nScript Value: \n{self.script_value}',
            content=ft.TextButton(
                text=self.script_name,
                on_click=self.copy_to_clipboard,
            ),
            padding=10,
            border_radius=10,
            text_style=ft.TextStyle(size=15, color=ft.colors.WHITE),
            vertical_offset=60,
        )
        self.edit_type = ft.Dropdown(
            label="Type",
            options=SCRIPT_TYPE_OPTIONS,
            value=self.script_type,
        )
        self.edit_name = ft.TextField(
            label="Name",
            value=self.display_script_name.content.text,
            capitalization=ft.TextCapitalization.SENTENCES,
        )
        self.edit_script = ft.TextField(
            label="Script",
            value=self.script_value,
            multiline=True,
            max_lines=5,
            on_focus=lambda e: self.resize_input_fields(e, self.edit_script),
            on_blur=lambda e: self.resize_input_fields(e, self.edit_script),
            on_change=lambda e: self.update_markdown(e),
            expand=True,
        )
        self.edit_description = ft.TextField(
            label="Description",
            value=self.description,
            multiline=True,
            expand=True,
            on_focus=lambda e: self.resize_input_fields(e, self.edit_description),
            on_blur=lambda e: self.resize_input_fields(e, self.edit_description),
        )
        self.display_view = None

    def build(self):
        self.display_view = ft.Card(
            ft.Row(
                width=self.parent.page.window_width,
                controls=[
                    ft.Row(
                        [
                            ft.IconButton(icon="menu", disabled=True),
                            self.display_script_name,
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.icons.CREATE_OUTLINED,
                                        tooltip="Edit",
                                        on_click=self.edit_clicked,
                                    ),
                                    ft.IconButton(
                                        ft.icons.DELETE_OUTLINE,
                                        tooltip="Delete",
                                        on_click=self.delete_clicked,
                                    ),
                                ],
                                expand=True,
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        expand=True,
                    ),
                ]
            ),
            margin=ft.Margin(0, 0, 10, 0)
        )
        return ft.Column(controls=[self.display_view])

    @staticmethod
    def resize_input_fields(e, control_ref):
        if control_ref.max_lines == 10:
            control_ref.max_lines = 5
        else:
            control_ref.max_lines = 10
        control_ref.update()

    def edit_clicked(self, e):
        self.edit_type.value = self.script_type
        self.edit_name.value = self.display_script_name.content.text
        self.edit_script.value = self.script_value
        #  Markdown being stupid and requires it formatted this way
        self.markdown_render.value = f"""

```{self.edit_type.value.lower()}
{self.edit_script.value}
```
"""
        self.edit_description.value = self.description
        self.page.dialog.open_dialog(
            dialog_title=f'Edit {self.display_script_name.content.text}',
            dialog_type="edit_script",
            dialog_message=[
                self.edit_type,
                self.edit_name,
                ft.Row(
                    [
                        self.edit_script,
                        ft.Column(
                            [
                                self.markdown_render
                            ],
                            auto_scroll=True,
                            scroll=ft.ScrollMode.ALWAYS,
                            expand=True
                        ),
                    ],
                    expand=True
                ),
                self.edit_description,
            ],
            function_ref=[lambda event: self.save_clicked(event), lambda event: self.cancel_clicked(event)]
        )

    def save_clicked(self, e):
        global SCRIPT_OBJECTS
        for script_dict in SCRIPT_OBJECTS[self.parent.container_title.value]:
            if script_dict["script_name"] == self.display_script_name.content.text:
                script_dict["script_type"] = self.edit_type.value
                script_dict["script_name"] = self.edit_name.value
                script_dict["script_value"] = self.edit_script.value
                script_dict["script_description"] = self.edit_description.value
                break
        self.script_type = self.edit_type.value
        self.display_script_name.content.text = self.edit_name.value
        self.script_name = self.edit_name.value
        self.script_value = self.edit_script.value
        self.description = self.edit_description.value
        self.parent.write_json_file(
            self.parent.container_title,
            self.edit_type.value,
            self.edit_name.value,
            self.edit_script.value,
            self.edit_description.value,
            update=True
        )
        self.update()
        self.page.dialog.dismiss_dialog()

    def cancel_clicked(self, e):
        self.edit_name.value = ""
        self.edit_script.value = ""
        self.edit_type.value = ""
        self.update_markdown(None)
        self.edit_description.value = ""
        self.page.dialog.dismiss_dialog()

    def delete_clicked(self, e):
        self.delete_script(self)

    def copy_to_clipboard(self, e):
        if self.parent.container_title.value == "Search":
            self.parent.container_title.value = self.page.drawer.controls[self.page.drawer.selected_index + 3].label
            self.parent.container_title.update()
            for index in self.parent.scripts.controls:
                index.visible = True
            self.parent.update()
        self.open_dialog(dialog_type="user_input", dialog_message=self.script_value)

    def update_markdown(self, e):
        #  Markdown being stupid and requires it formatted this way
        self.markdown_render.value = f"""

```{self.script_type.lower()}
{self.edit_script.value}
```
"""
        self.page.update()


class ScriptContainer(ft.UserControl):# TODO Refactor to meet version 22 changes, UserControl is deprecated
    def __init__(self, page):
        super().__init__()
        global GEMINI_ENABLED
        self.page = page
        self.container_title = ft.Text("Scripz", size=30, expand=True)
        self.markdown_render = ft.Markdown(
            value=None,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono"),
        )
        self.new_script_type = ft.Dropdown(
            label="Type",
            width=300,
            options=SCRIPT_TYPE_OPTIONS,
            error_text="",
            autofocus=True,
            on_change=lambda e: self.check_dropdown_value(e),
        )
        self.new_script_name = ft.TextField(
            label="Name",
            hint_text="Enter a name",
            error_text="",
            capitalization=ft.TextCapitalization.SENTENCES,
            on_blur=lambda e: self.check_input_fields(e),
            on_change=lambda e: self.check_input_fields(e),
        )
        self.new_script_value = ft.TextField(
            label="Script",
            hint_text="Wrap variables in {{}} e.g.: Get-ADUser {{Username}}",
            multiline=True,
            max_lines=10,
            error_text="",
            on_blur=lambda e: self.check_input_fields(e),
            on_change=lambda e: self.check_input_fields(e),
            expand=True,
        )
        self.new_description = ft.TextField(
            label="Description",
            hint_text="",
            multiline=True,
            expand=True,
        )
        self.generate_description_button = ft.TextButton(
            text="Generate",
            on_click=lambda e: self.explain_code(self.new_script_value.value),
            visible=GEMINI_ENABLED,
            disabled=True,
            tooltip="Generate Description Using Gemini",
            icon=ft.icons.ASSISTANT_OUTLINED,
        )
        self.scripts = ft.Column(
            height=self.page.window_height - 275,
            scroll=ft.ScrollMode.ALWAYS,
            width=self.page.window_width,
            adaptive=True,
        )
        self.add_script_button = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            on_click=lambda e: self.page.dialog.open_dialog(
                dialog_title="New Script",
                dialog_type="new_script",
                dialog_message=[
                    self.new_script_type,
                    self.new_script_name,
                    ft.Row(
                        [
                            self.new_script_value,
                            ft.Column(
                                [
                                    self.markdown_render
                                ],
                                auto_scroll=True,
                                scroll=ft.ScrollMode.ALWAYS,
                                expand=True
                            ),
                        ],
                        expand=True
                    ),
                    self.new_description,
                    self.generate_description_button,
                ],
                function_ref=self.create_new_script
            ),
            mini=True,
            tooltip="Add New",
            visible=False,
        )

    def build(self):
        return ft.Column(
            width=self.page.window_width,
            expand=True,
            adaptive=True,
            controls=[
                ft.Row(
                    controls=[
                        self.container_title,
                        self.add_script_button,
                    ],
                    alignment=ft.MainAxisAlignment.END
                ),
                ft.Divider(),
                self.scripts,
                ft.Divider(),
            ],
        )

    def update_markdown(self, e):
        if self.new_script_type.value is not None:
            self.markdown_render.value = f"""

```{self.new_script_type.value.lower()}
{self.new_script_value.value}
```
"""

        self.page.update()

    def check_dropdown_value(self, e):
        self.update_markdown(e)
        if e.control.value is not None:
            e.control.error_text = ""
            self.page.update()

    def check_input_fields(self, e):
        self.update_markdown(e)
        # Check the current text field if it is empty or not.
        if e.control.value == '':
            e.control.error_text = "Must not be empty"
            self.page.dialog.confirm_button.disabled = True
            self.generate_description_button.disabled = True

        else:
            e.control.error_text = ''
            self.page.dialog.confirm_button.disabled = False
            self.generate_description_button.disabled = False

        # Double check that neither text fields are empty.
        if self.new_script_name.value == '' or self.new_script_value.value == '':
            self.page.dialog.confirm_button.disabled = True
            self.generate_description_button.disabled = True

        else:
            self.page.dialog.confirm_button.disabled = False
            self.generate_description_button.disabled = False
        self.page.update()

    def explain_code(self, code_block):
        """Explains a given code block using Google Generative AI.

        Args:
            code_block (str): The code to be explained.

        Returns:
            str: A clear and concise explanation of the code.
        """
        if len([c for c in code_block if c != ' ']) < 5:
            self.new_script_value.error_text = "Must contain more than 5 characters to generate description with Gemini"
            self.page.update()

        elif code_block == '':
            self.new_script_value.error_text = "Must not be empty"
            self.page.update()

        elif self.new_script_name.value == '':
            self.new_script_name.error_text = "Must not be empty"
            self.page.update()

        elif self.new_script_type.value is None:
            self.new_script_type.error_text = "Must choose a type"
            self.page.update()

        else:
            if self.new_description.value != "":
                self.new_description.value = ''
                # TODO: Find a way to ensure that only actual code is sent and not other prompts.
                prompt = f"Explain the following {self.new_script_type.value} code using only 1 to 2 sentences:\n{code_block}"
                response = model.generate_content(prompt)
                self.new_description.value = response.text
                self.page.update()
            else:
                prompt = f"Explain the following {self.new_script_type.value} code using only 1 to 2 sentences:\n{code_block}"
                try:
                    response = model.generate_content(prompt)
                    self.new_description.value = response.text
                    self.page.update()
                except Exception as e:
                    # Handle potential exceptions related to invalid API key or other errors
                    self.new_description.value = f"400 API key not valid. Please pass a valid API key."
                    self.page.update()
                    log_error(f"{e}")

    def load_script_objects_from_json(self):
        """
        Loads script objects from the specified JSON file and appends them to SCRIPT_OBJECTS.
        """
        global SCRIPT_OBJECTS
        filename = SCRIPTS_FILE
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                for category, items in data.items():
                    if category not in SCRIPT_OBJECTS:
                        SCRIPT_OBJECTS[category] = []
                        SCRIPT_OBJECTS[category] = items
                        for item in SCRIPT_OBJECTS[category]:
                            script_type = item.get("script_type")
                            script_name = item.get("script_name")
                            script_value = item.get("script_value")
                            script_description = item.get("script_description")

                            self.scripts.controls.append(
                                ft.DragTarget(
                                    content=ft.Draggable(
                                        content=ScriptObject(
                                            parent=self,
                                            script_type=script_type,
                                            script_name=script_name,
                                            script_value=script_value,
                                            description=script_description,
                                        )
                                    ),
                                    on_accept=self.accept_drop
                                )
                            )
                    else:
                        for item in items:
                            script_type = item.get("script_type")
                            script_name = item.get("script_name")
                            script_value = item.get("script_value")
                            script_description = item.get("script_description")

                            self.scripts.controls.append(
                                ft.DragTarget(
                                    content=ft.Draggable(
                                        content=ScriptObject(
                                            parent=self,
                                            script_type=script_type,
                                            script_name=script_name,
                                            script_value=script_value,
                                            description=script_description,
                                        )
                                    ),
                                    on_accept=self.accept_drop
                                )
                            )
                            SCRIPT_OBJECTS[category].append(item)
        except FileNotFoundError:
            log_error(f".\\{filename} not found. No script objects loaded.")

        self.update()

    @staticmethod
    def write_json_file(category="", script_type="", script_name="", script_value="", description="", update=False):
        """
        Writes data to a JSON file.

        Description:
            - This static method is used to write data to a JSON file.
            - It takes in various parameters such as category, script_type, script_name, script_value, description, and update.
            - If update is True, it updates the JSON file with the SCRIPT_OBJECTS data.
            - Otherwise, it reads the existing data from the file (if any), appends the new data to it, and writes the updated data back to the JSON file.

        Parameters:
            - category (str): The category of the script.
            - script_type (str): The type of the script.
            - script_name (str): The name of the script.
            - script_value (str): The value of the script.
            - description (str): The description of the script.
            - update (bool): Flag indicating whether to update the JSON file.

        """
        global SCRIPT_OBJECTS
        filename = SCRIPTS_FILE
        data = {
            "script_type": script_type,
            "script_name": script_name,
            "script_value": script_value,
            "script_description": description
        }
        if update:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(SCRIPT_OBJECTS, f, ensure_ascii=False, indent=4)
            except FileNotFoundError:
                log_error(f".\\{filename} not found. No script objects updated.")

        else:
            # Read existing data from the file (if any)
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = {}

            # Append the new data to the existing data
            if category not in existing_data:
                existing_data[category] = []
                SCRIPT_OBJECTS[category] = []
            if script_name != "":
                existing_data[category].append(data)
                SCRIPT_OBJECTS[category].append(data)

            # Write the updated data back to the JSON file
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)

    def accept_drop(self, e: ft.DragTargetAcceptEvent):
        """
        Handles the event when a drag-and-drop operation is accepted on a specific control.

        Parameters:
            - e (ft.DragTargetAcceptEvent): The event object containing information about the drag-and-drop operation.
        """
        if self.container_title.value != "Search":
            src = self.page.get_control(e.src_id)
            src_index = None
            object_to_move = None
            object_destination = None
            destination_index = self.scripts.controls.index(e.control)
            for i, x in enumerate(self.scripts.controls):
                if x.content.content.script_name == src.content.script_name and x.content.content.script_value == src.content.script_value:
                    src_index = i
                    break

            with open(SCRIPTS_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

            for i, item in enumerate(existing_data.get(self.container_title.value, [])):
                if item.get("script_name") == src.content.script_name and item.get(
                        "script_value") == src.content.script_value:
                    object_to_move = i
                    break

            for i, item in enumerate(existing_data.get(self.container_title.value, [])):
                if (item.get("script_name") == self.scripts.controls[
                    destination_index].content.content.script_name and item.get("script_value") ==
                        self.scripts.controls[destination_index].content.content.script_value):
                    object_destination = i
                    break

            self.scripts.controls[src_index], self.scripts.controls[destination_index] = (
                self.scripts.controls[destination_index], self.scripts.controls[src_index]
            )

            SCRIPT_OBJECTS[self.container_title.value][object_to_move], SCRIPT_OBJECTS[self.container_title.value][
                object_destination] = (
                SCRIPT_OBJECTS[self.container_title.value][object_destination],
                SCRIPT_OBJECTS[self.container_title.value][object_to_move]
            )
            self.write_json_file(update=True)
            self.update()

    def create_new_script(self):
        """
        Creates a new script and performs necessary actions.

        Description:
        - This function creates a new script by utilizing the provided values for script type, name, value, and description.
        - It then adds the script to the controls list and writes the script details to a JSON file.
        - Finally, it resets the input fields, dismisses the dialog, and updates the page.

        Parameters:
        - self: The current instance of the class.

        """
        script = (
            ft.DragTarget(
                content=ft.Draggable(
                    content=ScriptObject(
                        self,
                        self.new_script_type.value,
                        self.new_script_name.value,
                        self.new_script_value.value,
                        self.new_description.value,
                    )
                ),
                on_accept=self.accept_drop
            )
        )
        self.scripts.controls.append(script)
        self.write_json_file(self.container_title.value,
                             self.new_script_type.value,
                             self.new_script_name.value,
                             self.new_script_value.value,
                             self.new_description.value
                             )
        self.new_script_type.value = ""
        self.new_script_name.value = ""
        self.new_script_value.value = ""
        self.new_description.value = ""
        self.update_markdown(None)
        self.generate_description_button.disabled = True
        self.page.dialog.dismiss_dialog()
        self.update()

    def delete_script(self, script):
        self.page.dialog.open_dialog(
            dialog_title="Please confirm",
            dialog_type="delete_script",
            dialog_message="Do you really want to delete this script?",
            function_ref=lambda: self.confirm_delete(script)
        )

    def confirm_delete(self, script):
        """
        Confirms the deletion of a script and performs necessary actions.

        Description:
            - This function confirms the deletion of a script by searching for a matching script name in the controls list.
            - If a match is found, the script is removed from the controls list, the page is updated, and the dialog is dismissed.

            - Additionally, the function attempts to remove the script details from a JSON file by loading the existing data,
            finding the index of the script with the matching script name, removing it from the list, and writing the updated
            data back to the JSON file.
            - If the JSON file is not found, an error message is logged.

        Parameters:
            - self: The current instance of the class.
            - script: The script object to be deleted.

        """
        global SCRIPT_OBJECTS
        # Find the index of the script with the matching script_name and script_value in scripts container and remove it.
        for index, x in enumerate(self.scripts.controls):
            if x.content.content.script_name == script.script_name and x.content.content.script_value == script.script_value:
                self.scripts.controls.remove(self.scripts.controls[index])
                self.scripts.update()
            self.page.dialog.dismiss_dialog()
            try:
                with open(SCRIPTS_FILE, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

                # Find the index of the script with the matching script_name and script_value in json file.
                index_to_remove = None
                for i, item in enumerate(existing_data.get(self.container_title.value, [])):
                    if item.get("script_name") == script.script_name and item.get(
                            "script_value") == script.script_value:
                        index_to_remove = i
                        break

                # Remove the script from the list in the json.
                if index_to_remove is not None:
                    existing_data[self.container_title.value].pop(index_to_remove)
                    SCRIPT_OBJECTS[self.container_title.value].pop(index_to_remove)

                # Write the updated data back to the JSON file
                with open(SCRIPTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=4)
            except FileNotFoundError:
                log_error(f".\\{SCRIPTS_FILE} not found. Unable to remove script from JSON.")

    def search(self, searchbar):
        if searchbar.value != "":
            self.container_title.value = "Search"
            self.container_title.update()
            for i, x in enumerate(self.scripts.controls):
                if (
                        searchbar.value.capitalize() in x.content.content.script_name
                        or searchbar.value in x.content.content.script_type
                        or searchbar.value in x.content.content.script_value
                ):
                    self.scripts.controls[i].visible = True
                else:
                    self.scripts.controls[i].visible = False
        else:
            self.container_title.value = self.page.drawer.controls[self.page.drawer.selected_index + 3].label
            self.container_title.update()
            for index in self.scripts.controls:
                index.visible = True
        self.update()


def main(page: ft.Page):
    global SCRIPT_OBJECTS
    global DEFAULT_TYPES
    global SCRIPT_TYPE_OPTIONS
    global GEMINI_API_KEY
    global FIRST_START
    global SETTINGS
    global GEMINI_ENABLED
    setup_logger()
    load_env_file()
    GEMINI_ENABLED = SETTINGS.get('GEMINI_ENABLED')
    GEMINI_API_KEY = SETTINGS.get('GEMINI_API_KEY')
    genai.configure(api_key=GEMINI_API_KEY)

    page.title = 'Scripz'
    header = AppHeader(page)
    script_container = ScriptContainer(page)
    header.container = script_container
    category_drawer = CategoryDrawer(page, script_container)
    dialog = CustomDialog(page, script_container)
    page.dialog = dialog
    page.drawer = category_drawer
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(
        header,
        script_container,
        AppFooter(page),
    )

    def resize_container(e):
        script_container.scripts.height = page.window_height - 275
        script_container.scripts.width = page.window_width - 500
        script_container.update()
        page.update()

    if load_env_file():
        page.theme_mode = SETTINGS.get("THEME")
        if page.theme_mode == "light":
            header.content.controls[2].selected = True
        else:
            header.content.controls[2].selected = False
    else:
        page.theme_mode = "dark"
        update_env_file("THEME", "dark")

    def on_keyboard(e: ft.KeyboardEvent, header_ref):
        if e.key == "F" and e.ctrl:
            header_ref.show_search_bar(e)
        elif e.key == "Escape":
            header_ref.clear_search_bar()
        page.update()

    page.on_keyboard_event = lambda e: on_keyboard(e, header)

    page.update()
    script_container.load_script_objects_from_json()
    SCRIPT_TYPE_OPTIONS.extend([ft.dropdown.Option(type_value) for type_value in DEFAULT_TYPES])
    category_drawer.update_drawer()
    page.window_min_width = 500
    page.window_min_height = 500
    page.update()
    page.on_resize = resize_container

    if SCRIPT_OBJECTS:
        FIRST_START = False
    else:
        dialog.open_dialog(dialog_title="Welcome!", dialog_type="start_up")


model = genai.GenerativeModel('gemini-pro')
atexit.register(lambda: log_info("Program stopped."))
ft.app(target=main, assets_dir="assets")
