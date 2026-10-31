![Banner](banner.png)

# file-comment-stripper
Removes comments from source code files to reduce attack surface and potential information leakage. Supports configurable comment syntax for various languages. - Focused on File operations and analysis

## Install
`git clone https://github.com/ShadowGuardAI/file-comment-stripper`

## Usage
`./file-comment-stripper [params]`

## Parameters
- `-h`: Show help message and exit
- `--comment_style`: No description provided
- `--strip_shebang`: No description provided
- `--backup`: Create a backup of the original file before modification.

## License
Copyright (c) ShadowGuardAI

The default style removes the whole comment, marker and text, for `#` line comments, `//` line comments, and `/* ... */` block comments. Marker sequences inside string literals are left byte identical, so a string holding `//` or `#` and a URL survive unchanged. The shebang line is preserved verbatim as the first line unless `--strip_shebang` is given, in which case the whole shebang line is removed. `--backup` copies the input to `<input>.bak` and leaves the original in place. An output path that resolves to the input file is refused at exit 1. Every run reports the number of comments stripped; a run that strips nothing exits 1 with a plain nothing stripped line and writes no output. A missing input, a non UTF-8 input, and an invalid comment style regex each exit 1 with the reason logged and no output written.
