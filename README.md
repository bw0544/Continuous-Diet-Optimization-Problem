## Structure Of Repository
- `data_json`: contains the .json files with the data used in the project.
- `reference_code`: contains the .py files with the code from lecturers. It is in Spanish and hard to work with, so use the functions from `wrapper_helper_functions.py` file instead.
- `data_models`: contains data models used in the project (e.g. Individual)
- `playground`: all other random scripts/python files that are not necessary for the project, rather tryout scripts etc.


## [Optional] MySQL database - setup and download data
Add the .env file in the root of this repository (Python/.env), with the following content:

```
mysql_password=your_password
```

To create the .json files with data from the MySQL database, run the file `reference_code/database.py`.
This step is not necessary if you already have the .json files in the `data` folder.
