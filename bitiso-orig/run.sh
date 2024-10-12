#!/bin/sh
./venv/bin/python manage.py runserver $(hostname -I | awk '{print $1}'):$1
