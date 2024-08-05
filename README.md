# Bitiso.org

Official bitiso.org website

You can use this Django project to run your own Bittorent website.

It tend to be generic but at the moment I focus to build it on top of bitiso.org

All feedbacks are welcome :)

## How to run

### Create a virtual env
```
python3 -m venv bitiso 
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

### Postgrsql settings


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
