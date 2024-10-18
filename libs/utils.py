from functools import wraps
from types import SimpleNamespace
from pathlib import Path
import os
import yaml
import pandas as pd


# _______________ EXCEPTIONS

def handle_exceptions(func):
    """
    Decorator to handle exceptions for functions.

    This decorator wraps a function in a try-except block, catching any
    exceptions that occur during the function's execution. If an exception
    is raised, an error message is printed to the console.

    Parameters:
        func (Callable): The function to be wrapped by the decorator.

    Returns:
        Callable: A wrapper function that includes exception handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print_message(f"\n... Error in {func.__name__}: {e}")
    return wrapper


# _______________ PATH

@handle_exceptions
def get_current_path() -> Path:
    """
    Get the absolute path of the current file.

    Returns:
        Path: The absolute path of the current file as a Path object.
    """

    return Path(__file__).absolute()

@handle_exceptions
def get_project_path() -> Path:
    """
    Get the absolute path of the project's root directory.

    This function assumes that the project root is two directories up
    from the current file's directory.

    Returns:
        Path: The absolute path of the project's root directory as a Path object.
    """

    return get_current_path().parent.parent.absolute()


# _______________ FILES

@handle_exceptions
def check_file_exists(path: str) -> bool:
    """
    Check if a file exists at the given path.

    Parameters:
        path (str): The path to the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """

    if os.path.isfile(path):
        return True
    else:
        return False

@handle_exceptions
def delete_file(path: str) -> None:
    """
    Delete a file at the specified path.

    Parameters:
        path (str): The path to the file to be deleted.

    Returns:
        None: This function does not return a value.
    """

    if os.path.exists(path):
        os.remove(path)

# _______________ FOLDERS

@handle_exceptions
def check_folder_exists(path: str) -> bool:
    """
    Check if a folder exists at the specified path.

    Parameters:
        path (str): The path to the folder to check.

    Returns:
        bool: True if the folder exists, False otherwise.
    """

    if os.path.isdir(path):
        return True
    else:
        return False

@handle_exceptions
def create_folder(path: str) -> None:
    """
    Create a new folder at the specified path if it does not already exist.

    Parameters:
        path (str): The path where the new folder should be created.

    Returns:
        None: This function does not return a value.
    """

    if not os.path.exists(path):
        os.makedirs(path)


# _______________ YAML

@handle_exceptions
def load_yaml(file_name: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary.

    Parameters:
        file_name (str): The path to the YAML file to be loaded.

    Returns:
        dict: The contents of the YAML file as a dictionary.

    Raises:
        yaml.YAMLError: If there is an error loading the YAML file, an error message will be printed.
    """

    with open(file_name, 'r', encoding='UTF-8') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f'ERROR loading yaml file {file_name}: {exc}')

    return yaml_content

# _______________ PANDAS

@handle_exceptions
def load_df_from_csv(path) -> pd.DataFrame:
    """
    Load a DataFrame from a CSV file.

    Parameters:
        path (str): The path to the CSV file to be loaded.

    Returns:
        pd.DataFrame: The DataFrame loaded from the CSV file.
    """

    return pd.read_csv(path)

@handle_exceptions
def save_df_to_csv(df, path) -> None:
    """
    Save a DataFrame to a CSV file.

    Parameters:
        df (pd.DataFrame): The DataFrame to be saved.
        path (str): The path where the CSV file should be saved.

    Returns:
        None: This function does not return a value.
    """

    create_folder(path.parent)
    df.to_csv(path)

# _______________ PRINT

@handle_exceptions
def print_message(message: str, tab: int = 4) -> None:
    """
    Print a message with optional indentation.

    Args:
        message (str): The message to print.
        tab (int): The number of spaces to indent the message. Default is 4.
    """

    if tab == 0:
        _text = f" ... {message}"
    else:
        _text = f"{'':>{tab}} {message}"

    print(_text)


# _______________ OBJECTS

@handle_exceptions
def dict_to_namespace(data: dict) -> SimpleNamespace:
    """
    Convert a dictionary to a SimpleNamespace object, recursively converting
    nested dictionaries and lists. Additionally, it processes 'path' keys
    to create folders and construct paths based on their values.

    Parameters:
        data (dict): The dictionary to be converted.

    Returns:
        SimpleNamespace: A SimpleNamespace object representing the dictionary.

    """

    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = dict_to_namespace(value)

            if key =='path':

                # convert string to Path object
                if value.startswith('./'):
                    _path = get_project_path().joinpath(value)    # relative path
                else:
                    _path = Path(value).joinpath(value)           # absolute path

                create_folder(_path)

                # add filename to the path
                if data.get('file_name') is not None:
                    data['path'] = _path.joinpath(data.get('file_name'))
                else:
                    data['path'] = _path

        return SimpleNamespace(**data)

    elif isinstance(data, list):
        return [dict_to_namespace(item) for item in data]
    else:
        return data
