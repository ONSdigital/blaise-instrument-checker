# Blaise Instrument Checker
 
### Setup Development Environment 

Clone the project locally:

```
git clone https://github.com/ONSdigital/blaise-instrument-checker.git
```


Create a virtual environment:

On MacOS
```
python3 -m venv venv  
source venv/bin/activate (this will run a .bat file)
```
On Windows
```
python -m venv venv  
venv\Scripts\activate (this will run a .bat file)
```

Install the requirements:

```
pip install -r requirements.txt
```

Create a .env file in the project root folder and add the following settings:

```
PROTOCOL = 'https'
BLAISE_USERNAME = 'blaise'
BLAISE_PASSWORD = 'password'
LOG_LEVEL=DEBUG
```

##### Running locally

from inside the venv, run:
```
python -m flask run
```

#### PyCharm Setup:

To get BIC up and runnable from PyCharm, make sure you follow the commands above to setup the venv and the `.env` file . 
1. Press **Shift** twice and enter `/project interpreter` and press enter.
1. Select the Cog and select Add
1. With the venv already, it should select Existing environment wit it pointing to the env/ folder
1. Press OK, you should now see a long list of installed modules then select OK again
1. Select 'Add Configuration' from the top right corner of the IDE
1. Add a new Python Configuration
    1. Under the Configuration tab change  Script Path to Module Name, and set the Module to be `flask`
    1. Set parameters to `run`
    1. Set Python interpreter as the one you just created.
    1. Set the working directory to the subdirectory to `blaise_instrument_checker` so it should be some like `path/to/project/blaise-instrument-checker/blaise_instrument_checker`
    1. Select Ok
1. Select Run or Debug to get the application started
