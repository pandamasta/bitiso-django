sudo apt-get install python3-venv
python3.7 -m venv bitiso 
cd bitiso
source ../bin/activate
pip install -r requirements.txt
python3.7 manage.py migrate
gunicorn --bind xx.xx.xx.xx:8080 bitiso.wsgi 
