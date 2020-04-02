#!venv/bin/python
from app import webapp, db

# This creates all the tables described in the models.py, the db itself must exist already
# It still works fine if the tables already exist unless their structure has been changed
db.create_all()
webapp.run(host='0.0.0.0',debug=True)
