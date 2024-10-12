# Bitiso.org | Bittorent web indexer for free content.

Official https://www.bitiso.org website

You can use this Django project to run your own Bittorent website.

It tend to be generic but at the moment I focus to build it on top of bitiso.org

All feedbacks are welcome :)

## How to run

### One liner with interactive instalation.

You need python-venv as it will deplyed in virtual environement

```
git clone https://github.com/pandamasta/bitiso-django.git && cd bitiso-django && chmod +x install.sh && ./install.sh
```

By default it will chose sqlite. Edit .env to match your settings.


### Manual installation
#### Create a virtual env
```
python3 -m venv venv
git clone https://github.com/pandamasta/bitiso-django.git
cd bitiso-django
```

#### Set settings .env variables

```
cp .env-template .env
```

Set proper value in .env

#### Bootstrap the project

```
source venv/bin/activate
(venv) pip install -r requirements.txt
(venv) python3 manage.py migrate
(venv) python manage.py createsuperuser
(venv) python manage.py runserver x.x.x.x:8080 or python manage.py runserver $(hostname -I | awk '{print $1}'):\8000
```

### Start webserver

```
./run <port>
```

#### Postgrsql settings


If some error on  DB privilège ensure that the user of the DB has full privilege on following object

```
postgres=# GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <user>;
GRANT
postgres=# \c <db_name>
You are now connected to database "<db_name>" user "postgres".

<db_name>=# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO <user>;
GRANT
<db_name=># GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO <user>;
GRANT
<db_name>=# GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO <user>;
GRANT
<bitiso_dev>=# ALTER TABLE <table> OWNER TO <user>;
```
