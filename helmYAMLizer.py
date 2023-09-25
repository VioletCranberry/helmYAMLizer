#!/usr/bin/env python3
# coding: utf-8

# pylint: disable=missing-module-docstring
# pylint: disable=invalid-name

import argparse
import logging
import os
import sys
from functools import wraps
from typing import Callable, Any, Dict, Optional

from ruamel.yaml import YAML, YAMLError

# Initialize new global YAML instance.
yaml = YAML()
# Ensure that the original quotes around string scalars are preserved.
yaml.preserve_quotes = True
# Ensure that each YAML document in a multi-document file starts with '---'.
yaml.explicit_start = True


def handle_exceptions(func: Callable) -> Callable:
    """Decorator to catch exceptions occurring within the decorated function."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Attempt to execute the provided function.
        try:
            return func(*args, **kwargs)
        # If any exception occurs, handle it.
        # pylint: disable=broad-except
        except Exception as err:
            # Get the name of the function where the exception occurred.
            func_name = func.__name__
            logging.fatal("An exception occurred " "in function %s: %s", func_name, err)
            # Exit the program with an error status.
            sys.exit(1)

    return wrapper


@handle_exceptions
def get_first_line_comment(document: dict) -> Optional[str]:
    """Return the comment from the first line of the YAML document if it exists."""
    # Check if the document is a dictionary or is not None (empty YAML)
    if document is None or not isinstance(document, dict):
        return None
    try:
        # Accessing comments associated with the document
        if hasattr(document, "ca") and document.ca.comment:
            comment_data = document.ca.comment
            # Retrieve first line comment
            comment_token = comment_data[1][0]
            comment_value = comment_token.value.strip()
            logging.debug("Comment value: %s", comment_value)
            return comment_value
    # Handle cases where expected structures are not found
    except (AttributeError, IndexError):
        return None
    return None


@handle_exceptions
def get_template_source_path(comment: str) -> Optional[str]:
    """Get the document template path from a given comment string."""
    path_pattern = "# Source:"
    # Validate if comment is a string
    if not isinstance(comment, str):
        raise ValueError(f"Expected a string for comment, but got {type(comment)}.")
    # Check if comment starts with the desired pattern
    if comment.startswith(path_pattern):
        try:
            template_path = comment.split(": ", 1)[1].strip()
            # Handle the case when the path is empty after stripping
            if not template_path:
                raise ValueError(
                    f"Comment '{comment}' is missing a template path"
                    f" after '{path_pattern}'."
                )
        # Handle the case when the split operation doesn't produce the expected list size
        except IndexError as err:
            raise ValueError(
                f"Comment '{comment}' is malformed "
                f"and cannot be split appropriately."
            ) from err
        logging.debug("Document source path: %s", template_path)
        return template_path
    raise ValueError(f"Comment {comment} does not begin with {path_pattern}")


@handle_exceptions
def flatten_source_path(template_path: str) -> str:
    """Flatten template path based on certain prefixes or substrings."""
    if not isinstance(template_path, str):
        raise ValueError(
            f"Expected a string for template path, but got {type(template_path)}."
        )
    # Check if template_path starts with "crds/"
    if template_path.startswith("crds/"):
        return template_path
    # Check if "/templates/" is present in template_path
    if "/templates/" in template_path:
        return template_path.split("/templates/")[1]
    # Raise an error if neither of the conditions is met
    raise ValueError(
        f"The path '{template_path}' neither "
        f"starts with 'crds/' nor contains"
        f" '/templates/'."
    )


@handle_exceptions
def save_document_to_file(file_path: str, document: Dict) -> None:
    """Save the given data to the specified file path."""
    # Validate that the provided document is a dictionary
    logging.debug("Document data to be saved: %s", document)
    if not isinstance(document, Dict):
        raise ValueError(
            f"Provided document must be a dictionary, but got {type(document)}."
        )
    # Validate that the provided file path is a string
    if not isinstance(file_path, str):
        raise ValueError(
            f"Provided file path must be a string, but got {type(file_path)}."
        )
    try:
        with open(file=file_path, encoding="utf-8", mode="w") as yaml_file:
            logging.debug("File path: %s", yaml_file.name)
            # Dump the document data to the file in YAML format
            yaml.dump(document, yaml_file)
    # Catch IO errors that might occur during file operations
    except IOError as io_err:
        raise RuntimeError(
            f"Failed to save data to '{file_path}'." f" IOError: {str(io_err)}"
        ) from io_err
    # Catch errors that might occur during YAML operations
    except YAMLError as yaml_err:
        raise RuntimeError(
            f"Failed to save data to '{file_path}' due to YAML error:"
            f" {str(yaml_err)}"
        ) from yaml_err


@handle_exceptions
def ensure_dirs_exists(file_path: str) -> None:
    """Ensure that the directory of the given path exists."""
    # Ensure path is a string
    if not isinstance(file_path, str):
        raise ValueError("Provided path must be a string.")
    folder_path = os.path.dirname(file_path)
    # If folder_path is empty, it means the provided path is a file/directory
    # in the current directory. So, we don't need to do anything.
    if not folder_path:
        return
    try:
        # Check if the directory already exists, if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
    except OSError as err:
        raise RuntimeError(
            f"Failed to create directory '{folder_path}'." f" Error: {str(err)}"
        ) from err


@handle_exceptions
def prepare_file_path(target_dir: str, flattened_path: str) -> str:
    """Prepare and ensure the directory for the file path exists."""
    # Combine target directory and flattened path to form the local file path.
    try:
        local_file_path = os.path.join(target_dir, flattened_path)
    except TypeError as err:
        raise RuntimeError(f"Failed to join file paths." f" Error: {str(err)}") from err
    # Ensure that all directories in the path exist.
    ensure_dirs_exists(local_file_path)
    return local_file_path


def get_arguments() -> argparse.Namespace:
    """Parses and returns command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dir",
        action="store",
        help="The directory where files will be saved.",
        required=True,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Should we run the script in debug mode?",
        required=False,
    )
    return parser.parse_args()


def main() -> None:
    """Main function"""
    args = get_arguments()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)8s - %(message)s",
    )

    target_dir = args.dir
    user_input = sys.stdin.read()
    yaml_input = yaml.load_all(user_input)

    for index, document in enumerate(yaml_input, start=1):
        # Retrieve first document comment
        source_comment = get_first_line_comment(document)
        # If document begins with the comment
        if source_comment:
            logging.info("Processing document [#%s] %s", index, source_comment)
            # Retrieve document source comment of the template.
            doc_source_path = get_template_source_path(source_comment)
            # Flatten document source comment path.
            doc_source_path = flatten_source_path(doc_source_path)
            # Prepare document local path.
            file_path = prepare_file_path(target_dir, doc_source_path)
            # Save the document to file.
            save_document_to_file(file_path, document)
        else:
            logging.warning(
                "Document [#%s] has no recognizable source." " Skipping.", index
            )


if __name__ == "__main__":
    main()
