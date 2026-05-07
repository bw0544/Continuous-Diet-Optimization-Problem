## Structure Of Repository
- `data_json`: contains the .json files with the data used in the project.
- `reference_code`: contains the .py files with the code from lecturers. It is in Spanish and hard to work with, so use the functions from `wrapper_helper_functions.py` file instead.
- `data_models`: contains data models used in the project (e.g. Individual)
- `playground`: all other random scripts/python files that are not necessary for the project, rather tryout scripts etc.

## Important implementation details
- Population consists of `Individual` objects, which are defined in `data_models/individual.py`. Here we are trying to optimize the food_type chosen and the amount.
That's why we have 2 vectors for each individual: food_type and amount.
- We have to define and hard-code the subject (age and calories intake goal for the day). In our case we set it to: **age=30, calories_goal=2567.85** (chosen from the `subjects.json` file). 
Use the constant `TEST_SUBJECT_JOHN` from `data_models/subject.py` to access this subject in your code.
- Our goal is to optimize the calories intake, nothing else!
- When working with the food database, import the constant `FOOD_DATABASE` from `data_models/database.py` to access it in your code.


## [Optional] MySQL database - setup and download data
Add the .env file in the root of this repository (Python/.env), with the following content:

```
mysql_password=your_password
```

To create the .json files with data from the MySQL database, run the file `reference_code/database.py`.
This step is not necessary if you already have the .json files in the `data` folder.
