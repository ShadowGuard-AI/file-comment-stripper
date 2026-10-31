#!/usr/bin/env python3

import argparse
import logging
import pathlib
import re
import os
import shutil
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_STYLE = '//|#'

def setup_argparse():
    parser = argparse.ArgumentParser(description='Removes comments from source code files.')
    parser.add_argument('input_file', type=str, help='Path to the input file.')
    parser.add_argument('output_file', type=str, help='Path to the output file.')
    parser.add_argument('--comment_style', type=str, default=DEFAULT_STYLE, help="Comment style regex (default: //|#). The default handles '#' line comments, '//' line comments, and '/* ... */' block comments, respecting string literals. A custom regex is treated as the start-of-comment pattern: text from a match to the end of the line is removed.")
    parser.add_argument('--strip_shebang', action='store_true', help='Strip shebang line (#!...) from the beginning of the file.')
    parser.add_argument('--backup', action='store_true', help='Copy the original file to <input>.bak before modification, leaving the original in place.')
    return parser.parse_args()

def _trim_trailing_spaces(out):
    while out and out[-1] in (' ', '\t'):
        out.pop()

def strip_default(text):
    """State machine for the default styles. Returns (stripped_text, comment_count)."""
    out = []
    i = 0
    n = len(text)
    count = 0
    while i < n:
        # Triple-quoted strings first
        if text.startswith('"""', i) or text.startswith("'''", i):
            quote = text[i:i+3]
            end = text.find(quote, i+3)
            if end == -1:
                out.append(text[i:]); i = n
            else:
                out.append(text[i:end+3]); i = end+3
            continue
        ch = text[i]
        if ch in ('"', "'"):
            j = i + 1
            while j < n:
                if text[j] == '\\' and j + 1 < n:
                    j += 2; continue
                if text[j] == ch:
                    j += 1; break
                if text[j] == '\n':
                    break
                j += 1
            out.append(text[i:j]); i = j; continue
        if text.startswith('/*', i):
            end = text.find('*/', i+2)
            count += 1
            if end == -1:
                i = n
            else:
                i = end + 2
            continue
        if text.startswith('//', i) or ch == '#':
            count += 1
            _trim_trailing_spaces(out)
            end = text.find('\n', i)
            if end == -1:
                i = n
            else:
                i = end  # keep the newline, consumed as a normal char next pass
            continue
        out.append(ch); i += 1
    return ''.join(out), count

def strip_custom(text, pattern):
    out_lines = []
    count = 0
    for line in text.split('\n'):
        m = pattern.search(line)
        if m:
            count += 1
            line = line[:m.start()].rstrip()
        out_lines.append(line)
    return '\n'.join(out_lines), count

def remove_comments(input_file, output_file, comment_style, strip_shebang, backup):
    input_path = pathlib.Path(input_file)
    output_path = pathlib.Path(output_file)
    # Ruling (1): refuse when the resolved output path is the input file, before opening anything for write.
    try:
        same = input_path.resolve() == output_path.resolve()
    except Exception:
        same = os.path.abspath(input_file) == os.path.abspath(output_file)
    if same:
        logging.error("Output path resolves to the input file; refusing.")
        print("Error: output path is the input file; refusing to overwrite it.")
        return 1
    if not input_path.exists():
        logging.error(f"Input file not found: {input_file}")
        print(f"Error: input file not found: {input_file}")
        return 1
    # Validate the regex first, for every style spelling.
    try:
        pattern = re.compile(comment_style)
    except re.error as e:
        logging.error(f"Invalid comment style regex: {e}")
        print(f"Error: invalid comment style regex: {e}")
        return 1
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError as e:
        logging.error(f"Input file is not valid UTF-8: {e}")
        print(f"Error: input file is not valid UTF-8: {e}")
        return 1
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        print(f"Error: reading input file: {e}")
        return 1

    # Shebang handling: preserve verbatim unless --strip_shebang removes the whole line.
    shebang = ''
    body = text
    if text.startswith('#!'):
        nl = text.find('\n')
        if nl == -1:
            first, body = text, ''
        else:
            first, body = text[:nl], text[nl+1:]
        if strip_shebang:
            logging.debug("Stripping shebang line.")
        else:
            shebang = first + ('\n' if nl != -1 else '')

    if comment_style == DEFAULT_STYLE:
        stripped_body, count = strip_default(body)
    else:
        stripped_body, count = strip_custom(body, pattern)

    print(f"Comments stripped: {count}")
    logging.info(f"Comments stripped: {count}")
    if count == 0:
        print("Nothing stripped: no comments were found.")
        logging.error("Nothing stripped: no comments were found.")
        return 1

    if backup:
        backup_file = input_file + ".bak"
        try:
            shutil.copy2(input_file, backup_file)
            logging.info(f"Created backup file: {backup_file}")
        except Exception as e:
            logging.error(f"Failed to create backup file: {e}")
            print(f"Error: failed to create backup file: {e}")
            return 1

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(shebang + stripped_body)
    except Exception as e:
        logging.error(f"Error writing to output file: {e}")
        print(f"Error: writing to output file: {e}")
        return 1
    logging.info(f"Successfully stripped comments from {input_file} and wrote to {output_file}.")
    return 0

def main():
    args = setup_argparse()
    return remove_comments(args.input_file, args.output_file, args.comment_style, args.strip_shebang, args.backup)

if __name__ == "__main__":
    sys.exit(main())
