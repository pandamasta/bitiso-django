# Bitiso.org

Tracker for project bitiso.org

This is a django project that can be run out of the box to host a tracker.

## How to run

### Create a virtual env
```
python3 -m venv bitiso 
cd bitiso
git clone https://github.com/pandamasta/bitiso-django.git
cd bitiso-django
```

### Set settings .env variables

```
cp .env-template .env
```

Set proper value in this config file

### Bootstrap the project

```
source ../bin/activate
(bitiso) pip install -r requirements.txt
(bitiso) python3 manage.py migrate
(bitiso) source .env; python manage.py createsuperuser --settings=settings.base
(bitiso) source .env; python manage.py runserver x.x.x.x:8080 --settings=settings.base
```
