# FMP-PostgreSQL-PyQt
Using Financial Modeling Prep APIs with SQL storage and dashboarding.

The project involves providing a GUI to collect the data supplied by the [Financial Model Prep](https://site.financialmodelingprep.com/) site via its APIs, store it in a suitable database, and put it to use in a chart study or financial analysis. The current example is based on the composition of the STOXX Europe 600 index, but other stock market indices can easily be added or substituted.

## Tags
- Python
- PyQt6
- PostgreSQL
- TimescaleDB
- GUI
- Application Development
- Linux Ubuntu
- FMP

## How to use on Linux
*Tested on Ubuntu 22.04*

### Prerequisites
- Python 3.11
- PostgreSQL 16
- TimescaleDB 2.14.2
- FMP account and its API key

Documentation on all these prerequisites is available directly in the 'docs' folder; retrieve it from the application's 'Preinstallation' menu. 

### Install the Application 
After the `$ git clone` you need to follow these steps:

1. **Modify PYTHONPATH**:
    Run `$ export PYTHONPATH="${PYTHONPATH}:/your/folder/FMP-PostgreSQL-PyQt"` to extend the Python interpreter's module search path to include the specified directory.

2. **Install Python Libraries**:
    - Create a virtual environment at project root : `$ python -m venv .venv`
    - Use it : `$ source .venv/bin/activate`
    - Run `$ pip install -r requirements.txt` to install the necessary librairies.

3. **Create an ENVIRONMENT File (.env)**   
    See documentation available in the 'docs' folder. The file will be used to store PostgreSQL database environment variables and the FMP API key.

4. **Start the Application**   
    To run the application, use the following command : `$ python3.11 src/main.py`

You should see a window similar to this :
![Capture d’écran du 2024-05-07 15-01-17](https://github.com/dasycarpum/FMP-PostgreSQL-PyQt/assets/35745289/486f6a8a-9be3-4a6f-a5b7-dee0308ea56f)


### Set up the Database and its Tables

Go to the 'FMP Database' menu in the main window, and follow the steps in order:
- Create new database, and restart the application
- Create tables
- Fetch initial data for the various tables

Please note that some tables may take a long time to download.

## License

This project is open-source and available under the GNU General Public License v3.0 (GPL-3.0). A copy of the GPL-3.0 license can be found in the LICENSE file in this repository.

### Dependencies and External Services

This software utilizes several open-source libraries and external services, each with their respective licenses:

- PyQt6: As PyQt6 is used in this project, the entire codebase is licensed under the GPL-3.0 to comply with its licensing terms.
- PostgreSQL and TimescaleDB: These databases are utilized under their PostgreSQL License, a liberal open source license, which is included by reference here.
- Financial Modeling Prep API: The usage of Financial Modeling Prep's API is subject to their own terms of service, which should be reviewed [here](https://site.financialmodelingprep.com/terms-of-service) . Users of this software are responsible for ensuring their use of the FMP API complies with these terms.

### Support and Contributions
For support, questions, or contributions, please submit an issue or pull request on GitHub. 

Contributions to this project are welcome, but by contributing, you agree that your contributions will be licensed under the same GPL-3.0 license. Please ensure that you have the right to submit anything you contribute, especially if it involves third-party copyrighted material or code.
