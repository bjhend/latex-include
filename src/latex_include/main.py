#!/usr/bin/env python3

# Recursively resolve LaTeX input and include commands according to LaTeX specification


import sys
import re
import typing
import argparse
import pathlib as pl
import contextlib
import importlib.metadata
from icecream import ic



class _Config():
    """Configuration values"""

    texExtension = '.tex'

    # Regular expression template to find LaTeX commands which are not commented out
    # the first part only allows '%' with an odd number of leading backslashes
    _commandPattern = r"^(?P<before>(?:[^%\\]|\\.)*)\\{cmd}{{(?P<filename>.*?)}}(?P<after>.*)"
    inputRe = re.compile(_commandPattern.format(cmd='input'))
    includeRe = re.compile(_commandPattern.format(cmd='include'))
    includeOnlyRe = re.compile(_commandPattern.format(cmd='includeonly'))


def _recursion(inFile:typing.TextIO, outFile:typing.TextIO, includeDir:pl.Path,
               includeOnly:list[str]|None=None, isResolveInclude:bool=True) -> None:
    """Copy inFile to outFile recursively inserting inputs and includes

    According to LaTeX `\\input` is always inserted but `\\include` is more special.
    `\\include` cannot be nested and if `\\includeonly` is given in the preamble
    includes are limited to those files. In addition `\\include` is surrounded by
    `\\clearpage`.

    Args:
        inFile:           readable text file object to parse
        outFile:          writable text file object to write result into
        includeDir:       dir to resolve included files
        includeOnly:      list of filenames to include found in `\\includeonly` command
        isResolveInclude: True if `\\include` should be resolved to avoid nested inclusion
    """
    config = _Config()

    def getFilename(match:re.Match) -> str:
        """Get filename argument from command match"""
        return match.group('filename').strip()

    def insertFile(match:re.Match, isInclude:bool) -> None:
        """Open filename in match and insert its content"""

        if isInclude:
            label = 'include'
            surround = "\\clearpage  % inserted due to resolved include\n"
            newIsResolveInclude = False
        else:
            label = 'input'
            surround = ''
            newIsResolveInclude = isResolveInclude

        includeFilename = getFilename(match)
        includePath = pl.Path(includeFilename).with_suffix(config.texExtension)
        if not includePath.is_absolute():
            includePath = includeDir / includePath
        includePathAbs = includePath.absolute()
        before = match.group('before')
        after = match.group('after')

        outFile.write(before)
        outFile.write(f"% ========= begin {label} of '{includeFilename}' ({includePathAbs}) ==========\n")
        outFile.write(surround)
        with includePathAbs.open() as file:
            _recursion(file, outFile, includeDir,
                       includeOnly=includeOnly, isResolveInclude=newIsResolveInclude)
        outFile.write(surround)
        outFile.write(f"% ========= end {label} of '{includeFilename}' ({includePathAbs}) ==========\n")
        outFile.write(after)

    for line in inFile:
        # Handle \includeonly
        matchIncludeOnly = config.includeOnlyRe.search(line)
        if matchIncludeOnly:
            filenames = getFilename(matchIncludeOnly).split(sep=',')
            includeOnly = [ f.strip() for f in filenames ]

        # Handle \input
        matchInput = config.inputRe.search(line)
        if matchInput:
            insertFile(match=matchInput, isInclude=False)
            continue

        # Handle \include
        if isResolveInclude:
            matchInclude = config.includeRe.search(line)
            if matchInclude:
                if (not includeOnly) or (getFilename(matchInclude) in includeOnly):
                    insertFile(match=matchInclude, isInclude=True)
                    continue

        # Copy line
        outFile.write(line)


def latexInclude(inFile:typing.TextIO, outFile:typing.TextIO, includeDir:pl.Path|str|None=None) -> None:
    """Start recursively resolving inputs/includes

    Args:
        inFile:     An open read text file object to read input LaTeX code from
        outFile:    An open write text file object to write resolved LaTeX code to
        includeDir: Optional dir to resolve includes from. If omitted the current
                    dir is used.
    """
    if not includeDir:
        includeDir = pl.Path.cwd()
    _recursion(inFile, outFile, pl.Path(includeDir))


def latexIncludeFiles(inPath:pl.Path|str, outPath:pl.Path|str|None=None, overwrite:bool=False) -> None:
    """Open files and call `latexInclude` with them using `inPath`'s parent as `includeDir`

    Both files can be given as `pathlib.Path` or string.

    We require `inPath` instead of defaulting to `stdin`, because we need
    its directory to resolve relative input/include paths in the LaTeX code

    Args:
        inPath:    path of input file
        outPath:   optional name of output file, if omitted `stdout` is used instead
        overwrite: overwrite existing output file if `True`

    Raises:
        OSError:         If a file cannot be opened.
        FileExistsError: If `outPath` exists and `overwrite` is `False`. Note that
                         `FileExistsError` is a specialization of `OSError`, so
                         catch it first.
    """
    inPath = pl.Path(inPath)
    assert inPath.is_file()

    inPathAbs = inPath.absolute()
    if outPath:
        # Mode 'x' raises FileExistsError if file exists
        mode = 'w' if overwrite else 'x'
        outPathAbs = pl.Path(outPath).absolute()
        output:contextlib.AbstractContextManager[typing.TextIO] = contextlib.closing(outPathAbs.open(mode))
    else:
        output = contextlib.nullcontext(sys.stdout)

    with inPathAbs.open() as inFile:
        with output as outFile:
            latexInclude(inFile, outFile, inPathAbs.parent)


def main() -> None:
    """Called from command line

    Parses command line for input and output and calls `latexIncludeFiles` with them.

    If output exists an additional command line flag is required to overwrite it.
    """
    parser = argparse.ArgumentParser(description="Resolve input/include commands in a LaTeX file to a single file")

    # See latexIncludeFiles documentation, why --input is required
    parser.add_argument('-i', '--input', required=True, type=pl.Path, help="Main LaTeX file to resolve")
    parser.add_argument('-o', '--output', type=pl.Path, help="Output file, default is stdout")
    parser.add_argument('-w', '--overwrite', action='store_true', help="Silently overwrite existing diff (default: %(default)s)")
    parser.add_argument('--version', action='version', version=importlib.metadata.version('latex-include'), help="Show version number and exit")
    args = parser.parse_args()

    try:
        latexIncludeFiles(args.input, args.output, overwrite=args.overwrite)
    except FileExistsError as ex:
        print(f"Output exists. Delete it or set option --overwrite (-w) to overwrite it: {ex}")
        exit(1)
    except OSError as ex:
        ic(ex)
        print(f"Cannot open input or output file: {ex}")
        exit(1)


if __name__ == "__main__":
    main()

