# rd-flask

This is Rog's test Flask project.

Its initial base was the tutorial here: 

https://www.digitalocean.com/community/tutorials/how-to-use-an-sqlite-database-in-a-flask-application


```
python init_db.py

export FLASK_APP=app
export FLASK_ENV=development
export PLEX_TOKEN=???????

# For Windows:
$env:PLEX_TOKEN='????????????'
$env:SECRET_KEY="????????????"
```

$env:PLEX_TOKEN='dbufy5hZk2k91QpxYUuW'

```
# Expects a .plex file in the same folder as plex_tools module with the following format:

PLEX_IP = '192.168.0.238'
PLEX_PORT = '32400'
PLEX_TOKEN = '?????????????'
```
