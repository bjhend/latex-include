# LaTeX Include

Resolve `\include` and `\input` commands in a LaTeX document as LaTeX does.


### License

See [License](LICENSE.md)


### Changelog

See [Changelog](CHANGELOG.md)


## Purpose

Some LaTeX tools like for example [*latexdiff*](https://www.ctan.org/pkg/latexdiff) cannot resolve `\include` and `\input` commands. This package resolves `\include` and `\input` creating a single LaTeX document that replaces the commands with the included files.

According to the LaTeX specification `\input` is recursively replaced by the included files. Opposed to that `\include` is only resolved one level deep and if the preamble contains an `\includeonly` command then only the include files listed in `\includeonly` are replaced. Other `\include` commands are ignored. This package considers this specification.


## Documentation

Documentation is generated with MkDocs. See [Contributing](#contributing) below for details.



## Installation

### Prerequesites

* Python3 is available with at least the version set in `pyproject.toml`


### Install

The installation itself can be done with `pip` or [`pipx`](https://pipx.pypa.io):

```
pip(x) install latex-include
```



## Usage

The package provides multiple levels of access:

* Function `latexInclude` receives an open input and an open output text stream resolving the inclusion commands in the input to create the output.
* Function `latexIncludeFiles` receives an input file path and optionally an output file path. It opens the files and calls `latexInclude` with them. If the output argument is omitted output will be `stdout`.
* The package can be executed from the command line with the command `latex-include` (see [options](#command-line-options) below).

See generated documentation for details how to call the Python functions.


### Command line options

Calling `latex-include --help` reproduces the following help text:

```
usage: latex-include [-h] -i INPUT [-o OUTPUT] [-w]

Resolve input/include commands in a LaTeX file to a single file

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Main LaTeX file to resolve
  -o OUTPUT, --output OUTPUT
                        Output file, default is stdout
  -w, --overwrite       Silently overwrite existing diff (default: False)
  --version             Show version number and exit
```

Note, that `stdin` cannot be used for input, because we need the directory of the input file to find included files.



## Contributing

Create issues or a pull requests to point out bugs or improvements.

We use [`uv`](https://docs.astral.sh/uv/) as development and packaging tool so you may use `uv sync` to create a virtual environment with all required packages and execute the scripts with `uv run`. Likely [`poetry`](https://python-poetry.org/) will work as well.

When contributing a pull request please check these points in addition to your tests:

* Add a short description in [Changelog](CHANGELOG.md) under *Next*
* Does the documentation still build and documents your changes?

Documentation is built with [MkDocs](https://www.mkdocs.org). Call `uv run mkdocs build --clean` from the base directory and open `site/index.html` in a browser to check the results. You may use the [MKDocs server](https://www.mkdocs.org/user-guide/cli/#mkdocs-serve) to see your doc changes live (note: opposed to the MkDocs documentation you have to give option `--livereload` besides `--watch` to make it work).

