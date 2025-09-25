<!-- `ssh -i "eastora.pem" ubuntu@3.111.23.194` -->

`ssh -i "clinic_project.pem" ubuntu@3.109.62.26`

# After logging in to server

sudo apt update
sudo apt install -y python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl git

# Configure Database Postgresql

`sudo -u postgres psql`
CREATE DATABASE clinic;
CREATE USER clinic WITH PASSWORD 'clinic';

ALTER ROLE clinic SET client_encoding TO 'utf8';
ALTER ROLE clinic SET default_transaction_isolation TO 'read committed';
ALTER ROLE clinic SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE clinic TO clinic;
\q



# Create directory and go to directory

mkdir ~/clinic
cd ~/clinic



# Create git and pull project from git

`git init
git remote add origin https://github.com/vaisagh-mp/clinic_project.git
git pull origin main`

# Create virtual environment and activate

'python3 -m venv venv
source venv/bin/activate'

# Install dependencies

`pip install django gunicorn psycopg2-binary`

. . .

Make sure you have following configuration in database settings of the project

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'eastora',
            'USER': 'eastora',
            'PASSWORD': 'eastora',
            'HOST': 'localhost',
            'PORT': '',
        }
}
. . .

# Create git and pull project from git

`git init

git pull origin main`

# Install dependencies from requiremnets file

`pip install -r requirements.txt`

`python manage.py makemigrations
python manage.py migrate`

`python manage.py createsuperuser`

`python manage.py collectstatic`

sudo ufw allow 8000
python manage.py runserver 0.0.0.0:8000

# open link http://server_domain_or_IP:8000 and make sure site is working properly

# Configuring gunicorn

`gunicorn --bind 0.0.0.0:8000 clinic_project.wsgi`

# Deactive virtualenv

`deactivate`

`sudo nano /etc/systemd/system/gunicorn.socket`

# Add this code to gunicorn.socket file.

. . .

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target

. . .

`sudo nano /etc/systemd/system/gunicorn.service`

# Add this code to gunicorn.service file.

. . .

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/clinic
ExecStart=/home/ubuntu/clinic/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          clinic_project.wsgi:application

[Install]
WantedBy=multi-user.target


. . .

sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket

. . .

# Output

. . .

`file /run/gunicorn.sock`

. . .

# Output

. . .

sudo journalctl -u gunicorn.socket
sudo systemctl status gunicorn

. . .

# Output

. . .

`curl --unix-socket /run/gunicorn.sock localhost`

. . .

# Output

The index page will be shown as output

. . .

`sudo systemctl status gunicorn`

# Output

. . .

sudo journalctl -u gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

`sudo nano /etc/nginx/sites-available/clinic_project`

# Add this code to project file.

. . .

server {
listen 80;
server_name 3.111.23.194;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

}

Ctrl + O → Save (Write Out)

Enter → Confirm filename

Ctrl + X → Exit

client_max_body_size 50M;
. . .

`sudo ln -s /etc/nginx/sites-available/clinic_project /etc/nginx/sites-enabled/clinic_project`

sudo nginx -t
sudo systemctl restart nginx

`sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full`

# Now the site will be available at ip address

# To check your Nginx error log

sudo tail -f /var/log/nginx/error.log

# To Update changes in project

`sudo systemctl restart gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn.socket gunicorn.service
sudo nginx -t && sudo systemctl restart nginx`