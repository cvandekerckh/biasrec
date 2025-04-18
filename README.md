# Biasrec
The following repo implements a web application designed to study of recommender systems in an online setting

# Installation
## Step 1 : dependencies
- Install python 3.10
- Install make
- Install pipenv

## Step 2 : create virtual environment
- In a terminal, create the virtual environment with `pipenv install`

## Step 3 : define environment variables
- Create a .env file and assign the secret key values : `SECRET_KEY=secret-key`.

# Quick start
- Assign experiment conditions to each user : `make assign-conditions`
- Create all the tables : `make reload-experiment`
- Train a recommender system model : `make create-model`
- Launch an experiment : `python microblog.py --config=rate` (see config.py to find appropriate configs)
- Display tables : `make display-ratings` (see Makefile)

# How to keep track of experiments and never loose data
After each experiment:
- make dump-database (on the virtual machine)
- make download_database (on your local machine)
- check you have the folder in deploy/data/received with the correct datatime
- copy/paste the new folder in a Onedrive to never miss any data 

# How to update a code ?
- make stop-deploy
- git pull
- (make reload-experiment⁠) : destroy all data ! be careful
- make start-deploy
