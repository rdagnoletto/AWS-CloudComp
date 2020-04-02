#!venv/bin/python
from app import webapp, db
#webapp.run(host='0.0.0.0',debug=False)

# This creates all the tables described in the models.py, the db itself must exist already though
# still works fine if the tables already exist
db.create_all()
webapp.run(host='0.0.0.0',debug=True)
