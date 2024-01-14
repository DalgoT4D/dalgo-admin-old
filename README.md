# dalgo-admin
An administrative web console for Dalgo (https://dalgo.in/).

Dalgo is an open-source data platform for the social sector. Since it is open-source, anyone is free to run their own instance of the platform.

The `dalgo-admin` application allows you to monitor your instance of Dalgo to get an overview of

- infrastructure usage
- client accounts

Project Tech4Dev runs an instance of Dalgo as a paid subscription service, and features for `dalgo-admin` are primarily driven by the use-cases we encounter.

## Installation

To install and run this app locally, you need to have Python v3.10, django v4.2, docker, postgres v14 or more and pip installed on your machine.

### Clone the repository

1. First, fork the repository and then clone the repository from GitHub using the following command on your local system:

```bash
git clone <repository_url>
```


### Setup the Project

2. Now change directory to the dalgo-admin project and take a look around

```bash
cd .\dalgo-admin
```
3. Now run the virtual environment by any of the given commands:

```bash
.\dalgoenv\Scripts\activate
```
Or
```bash
source dalgoenv\Scripts\activate
```

3. now run 

```bash
pip install requirements.txt
```
4. now change directory to the dalgo_admin
```bash
cd .\dalgo_admin
```

### Setup Postgres database (by docker)
Note: you can setup postgres for the django in any way you want (it is considered easier using docker)

1. Install docker on your system

For help refer: [docker docs](https://docs.docker.com/desktop/)

2. Now install postgres official image on docker and create an instance of it

For help refer: [this link](https://www.commandprompt.com/education/how-to-install-and-set-up-docker-postgresql-environment/) or docker docs

or any other article on web

3. run the postgres instance from docker desktop or CLI

4. Create a database and user in this instance from the Postgres prompt

for example,
```bash
CREATE DATABASE dalgo_db;
CREATE USER dalgo_user WITH PASSWORD '**********';
GRANT ALL PRIVILEGES ON DATABASE dalgo_db TO dalgo_user;
```

### return to django project
1. create a .env file in root directory
2. Inside the .env file add the environment variables for the database with values you created above (check the .env.template for variables)
3. Now apply the database settings to your django app
```bash
python manage.py makemigrations
python manage.py migrate
```
4. run the server
```bash
py manage.py runserver
```
5. Paste the given url on browser and see the app running

### Cheers!! Now you are done with the Setup!!