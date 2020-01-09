# Python CDCS REST API client

This is a base Python package for accessing instances of the NIST Configurable Data Curation System (CDCS) databases, versions 2+.  It defines a Python CDCS class that streamlines REST calls to a database by

- Taking access settings once (username, password, etc) and saving them for subsequent REST calls.
- Defining methods that wrap around REST calls to interact with the database in a more Pythonic way.
- Automatically converting any accessed information to pandas Series and DataFrame objects to allow for the information to be easily manipulated.

## Installation

The package can be installed using pip:

    pip install pycdcs

or conda (comming soon):

    conda install -c conda-forge pycdcs

Alternatively, the source code can be downloaded from github at [https://github.com/lmhale99/pycdcs](https://github.com/lmhale99/pycdcs)

## Documentation

Documentation for the package is given as Jupyter Notebooks that can be found on the github site.  Each Notebook is focused on providing details and examples related to different use cases for the package.

- **CDCS Public Data Exploration** outlines the basic functions allowing an anonymous user (i.e. not logged in) to explore the available public data on a curator.
- **CDCS Data Management** outlines the basic pre-defined functions allowing a logged-in user to manage their own templates, data records and blobs.
- **CDCS Rest Builder** provides a simple explanation of how users can easily build their own functions and make their own REST API calls should they wish to interact with the database in ways outside the pre-defined functions.
