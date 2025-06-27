#!/usr/bin/env python3

import argparse
import logging
import pathlib
import re
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Removes comments from source code files.')
    parser.add_argument('input_file', type=str, help='Path to the input file.')
    parser.add_argument('output_file', type=str, help='Path to the output file.')
    parser.add_argument('--comment_style', type=str, default='//|#', help='Comment style regex (default: //|#).  Example: \'#\' for Python, \'//|/\\*.*?\\*/\' for C-style comments.')
    parser.add_argument('--strip_shebang', action='store_true', help='Strip shebang line (#!...) from the beginning of the file.')  # Added option to strip shebang
    parser.add_argument('--backup', action='store_true', help='Create a backup of the original file before modification.')

    return parser.parse_args()


def remove_comments(input_file, output_file, comment_style, strip_shebang, backup):
    """
    Removes comments from the input file and writes the result to the output file.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output file.
        comment_style (str): Regular expression defining the comment style.
        strip_shebang (bool): Whether to remove the shebang line.
        backup (bool): Whether to create a backup of the original file.
    """
    try:
        input_path = pathlib.Path(input_file)
        output_path = pathlib.Path(output_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if not os.access(input_file, os.R_OK):
            raise PermissionError(f"No read access to input file: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            raise IOError(f"Error reading input file: {e}")
        
        if backup:
            backup_file = input_file + ".bak"
            try:
                 os.rename(input_file, backup_file)
                 logging.info(f"Created backup file: {backup_file}")
            except Exception as e:
                logging.warning(f"Failed to create backup file: {e}.  Continuing without backup.")

        stripped_lines = []
        for i, line in enumerate(lines):
            if i == 0 and strip_shebang and line.startswith("#!"):  # Strip shebang line
                logging.debug("Stripping shebang line.")
                continue # Skip the first line if it's a shebang
            
            stripped_line = re.sub(comment_style, '', line).rstrip()  # Remove comments and trailing whitespace
            stripped_lines.append(stripped_line + '\n')

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(stripped_lines)
        except Exception as e:
            raise IOError(f"Error writing to output file: {e}")


        logging.info(f"Successfully stripped comments from {input_file} and wrote to {output_file}.")

    except FileNotFoundError as e:
        logging.error(e)
    except PermissionError as e:
        logging.error(e)
    except IOError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def main():
    """
    Main function to execute the file comment stripper.
    """
    args = setup_argparse()
    remove_comments(args.input_file, args.output_file, args.comment_style, args.strip_shebang, args.backup)


if __name__ == "__main__":
    main()