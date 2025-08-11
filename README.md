# vynca_takehome

## Setup Instructions
### Setting Up the Backend 
This FastAPI backend uses Pipenv virtual environment for dependency management and requires and python3 pipenv to install

1. Install dependencies with Pipenv and activate environment in the project root

    `pipenv install --dev`

    `pipenv shell`

2. Navigate to the backend folder and start the server
    `uvicorn main:app --reload`

### Setting Up the Frontend 

1. Navigate to frontend folder and install dependencies

    `npm install`

2. Navigate to the backend folder and start the server
    `npm start`

### Seeding Demo Data


# Activate virtual environment
pipenv shell
The --dev flag installs both runtime and development dependencies (e.g., testing tools, linters).

Schema


Resources
FastAPI YouTube tutorial: https://www.youtube.com/watch?v=iWS9ogMPOI0
DBDiagram: https://dbdiagram.io/d
FastAPI official docs: https://fastapi.tiangolo.com
FastAPI TestClient: https://dev.to/kfir-g/why-you-should-use-a-single-fastapi-app-and-testclient-instance-4m2b
Pydantic: https://docs.pydantic.dev/latest/api/base_model/#pydantic.create_model
SQLModel: https://sqlmodel.tiangolo.com/
Using Pandas for converting txt to csv: https://codingbanana.medium.com/convert-your-text-file-into-csv-using-python-d346c8ae7952
Clean Up with Pandas: https://stackoverflow.com/questions/69238115/how-to-remove-extra-column-with-no-header-in-csv-in-python
https://www.w3schools.com/python/pandas/pandas_cleaning_wrong_format.asp
Data cleanup: https://medium.com/@rgr5882/100-days-of-data-science-day-37-using-regular-expressions-for-data-cleaning-809ab09a4958
https://stackoverflow.com/questions/78485326/pandas-extract-phone-number-if-it-is-in-correct-format/78485400
https://github.com/tiangolo/sqlmodel/issues/215
https://strawberry.rocks/docs/concepts/typings
https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html
https://www.apollographql.com/docs/react/get-started
https://mui.com/material-ui/getting-started/