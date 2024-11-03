==================================================
 RstDocGen - Generate doc snippets from YAML data
==================================================

|pre|

|tag| |license| |python| |contributors|

**Documentation as Code** (and sometimes *it is* code)

What is this thing?
===================

Mainly some helper tools to create/maintain reStructuredText_ document
includes to build larger (and more dynamic) documents such as the one
produced from `this System Test Description`_ template.

Generator tools
---------------

* ``gentestcase`` - generate new source file with test case metadata

  - input: YAML data file
  - output: YAML test case source file stub with example steps

* ``genrstdocs`` - generate test case metadata and procedures doc from source

  - input: YAML source file for test case
  - output: formatted document source in single ``.rst`` file

The first one is typically used once per test case to generate a new YAML
source file, while the second integrates nicely in a makefile for building
a complete Test Description document.

Traceability tool
-----------------

In addition to generating formatted test cases in reStructuredText_, we also
need to generate a cross-reference report showing both forward and inverse
traceability for requirement IDs and test case IDs.

* ``gentrace`` - generate SRVM cross-reference report for STD chapter 5

  - inputs: test case (YAML) sources and project data (typically CSV export
    from spreadsheet)
  - output: forward and inverse traceability reports


Software Stack and Tool Dependencies
====================================

Install the following with your system package manager to run the workflows:

* Python_ - at least version 3.8
* Tox_ - at least version 4.2

.. _Python: https://docs.python.org/3.9/index.html
.. _Tox: https://tox.wiki/en/latest/user_guide.html


Now you can use the workflow commands to install the remaining dependencies
using Python virtual environments inside the project directory and use the
tools for generating document sources, eg, test case snippets.

Optional dependencies
---------------------

Optional dependencies are use-case or task-specific; when used with the
downstream System/software Test Description template the core workflow and
optional dependencies are documented in the README_ and captured in the
``tox.ini`` files.

.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _rst2pdf: https://rst2pdf.org/
.. _this System Test Description:
.. _README: https://github.com/VCTLabs/software_test_description_template


Contributing
============

Please read CONTRIBUTING_ for details on the code of conduct and some general
guidance on submitting pull requests.

.. _CONTRIBUTING: https://github.com/sarnold/rstdocgen/blob/master/CONTRIBUTING.rst

Pre-commit
----------

This repo is pre-commit_ enabled for python/rst source and file-type
linting. The checks run automatically on commit and will fail the commit
(if not clean) and perform simple file corrections.  For example, if the
mypy check fails on commit, you must first fix any fatal errors for the
commit to succeed. That said, pre-commit does nothing if you don't install
it first (both the program itself and the hooks in your local repository
copy).

You will need to install pre-commit before contributing any changes;
installing it using your system's package manager is recommended,
otherwise install with pip into your local user environment using
something like::

  $ sudo emerge pre-commit       # --or--
  $ sudo apt install pre-commit  # --or--
  $ pip install pre-commit

then install the hooks into the repo you just created from the template::

  $ cd your_new_repo/
  $ pre-commit install --install-hooks

It's usually a good idea to update the hooks to the latest version::

  $ pre-commit autoupdate

Most (but not all) of the pre-commit checks will make corrections for you,
however, some will only report errors, so these you will need to correct
manually.

Automatic-fix checks include black, isort, autoflake, and miscellaneous
file fixers. If any of these fail, you can review the changes with
``git diff`` and just add them to your commit and continue.

If any of the mypy or rst source checks fail, you will get a report, but
then you must fix any errors before you can continue adding/committing.

For example, to see a "replay" of any ``rst`` check errors, run::

  $ pre-commit run rst-backticks -a
  $ pre-commit run rst-directive-colons -a
  $ pre-commit run rst-inline-touching-normal -a

To run all ``pre-commit`` checks manually, try::

  $ pre-commit run -a

.. _pre-commit: https://pre-commit.com/index.html


License
=======

This project is licensed under the MIT license - see the `LICENSE file`_ for
details.

.. _LICENSE file: https://github.com/sarnold/rstdocgen/blob/master/LICENSE


.. |license| image:: https://img.shields.io/github/license/sarnold/rstdocgen
    :target: https://github.com/sarnold/rstdocgen/blob/master/LICENSE
    :alt: License

.. |tag| image:: https://img.shields.io/github/v/tag/sarnold/rstdocgen?color=green&include_prereleases&label=latest%20release
    :target: https://github.com/sarnold/rstdocgen/releases
    :alt: GitHub tag

.. |python| image:: https://img.shields.io/badge/python-3.8+-blue.svg
    :target: https://www.python.org/downloads/
    :alt: Python

.. |pre| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. |contributors| image:: https://img.shields.io/github/contributors/sarnold/rstdocgen
   :target: https://github.com/sarnold/rstdocgen/
   :alt: Contributors
