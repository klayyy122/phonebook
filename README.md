# Phonebook
## Installation
```bash

sudo pacman -Syu

sudo pacman -S docker docker-compose git

sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

git clone https://github.com/klayyy122/phonebook.git
cd phonebook
```
## Create a .env file
```
nano .env

PG_DB=phonebook
PG_USER=phonebook_user
PG_PASS=password

GADMIN_EMAIL=admin@gmail.com
PGADMIN_PASS=admin
```
## Start
```bash
#start all containers
docker-compose up -d

#check logs
docker-compose logs -f
```

## Where is check?
- Phonebook http://localhost
- PGAdmin http://localhost/pgadmin login and password from .env
