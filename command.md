# GO TO DJANGO PROJECT
cd "C:\Users\CCTC\Desktop\PANUGALING_PYTHON\PANUGALING_DJANGO\IMS_Project"  # Go to folder containing manage.py


# PYTHON / PIP
py --version                         # Check Python version
py -m pip --version                  # Check pip version
py -m pip list                       # List installed packages
py -m pip freeze                     # Show installed packages and versions
py -m pip install PACKAGE            # Install a package
py -m pip uninstall PACKAGE          # Uninstall a package
py -m pip install --upgrade PACKAGE  # Upgrade a package
py -m pip install --upgrade pip      # Upgrade pip


# DJANGO INSTALLATION
py -m pip install django             # Install Django
py -m pip install Django==6.1        # Install Django 6.1
py -m django --version               # Check Django version


# DJANGO PROJECT
py -m django startproject PROJECT    # Create a new Django project
py -m django startproject PROJECT .  # Create project in current folder


# DJANGO APP
py manage.py startapp APP_NAME       # Create a new Django app


# SERVER
py manage.py runserver               # Start Django development server
py manage.py runserver 8080          # Start server on port 8080
py manage.py runserver 0.0.0.0:8000  # Allow access from network


# DATABASE / MIGRATIONS
py manage.py makemigrations           # Create migration files
py manage.py migrate                  # Apply migrations to database
py manage.py showmigrations           # Show migration status
py manage.py sqlmigrate APP 0001     # Show SQL for a migration
py manage.py flush                    # Delete all database data


# ADMIN
py manage.py makemigrations           # Create migration files
py manage.py migrate                   # Apply migrations to database
py manage.py createsuperuser          # Create admin account
py manage.py changepassword USERNAME  # Change user password


# DJANGO SHELL
py manage.py shell                    # Open Django Python shell


# PROJECT CHECK
py manage.py check                    # Check for configuration errors


# TESTING
py manage.py test                     # Run all tests
py manage.py test APP_NAME            # Run tests for a specific app


# STATIC FILES
py manage.py collectstatic            # Collect static files


# PIPENV
py -m pip install pipenv              # Install Pipenv
py -m pipenv --version                # Check Pipenv version
py -m pipenv install                  # Install dependencies from Pipfile
py -m pipenv install django           # Install Django using Pipenv
py -m pipenv install PACKAGE          # Install package using Pipenv
py -m pipenv uninstall PACKAGE        # Uninstall package from Pipenv
py -m pipenv shell                    # Enter Pipenv virtual environment
py -m pipenv graph                    # Show dependency tree
py -m pipenv --venv                   # Show virtual environment location
py -m pipenv run COMMAND              # Run command inside Pipenv environment


# REQUIREMENTS.TXT
py -m pip freeze > requirements.txt   # Save installed packages
py -m pip install -r requirements.txt # Install requirements


# WINDOWS COMMANDS
dir                                   # Show files and folders
cd FOLDER                             # Enter a folder
cd ..                                 # Go back one folder
mkdir FOLDER                          # Create a folder
cls                                   # Clear terminal
exit                                  # Close terminal


# URLS
# http://127.0.0.1:8000/              # Django website
# http://127.0.0.1:8000/admin/        # Django Admin