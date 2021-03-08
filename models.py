from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


default_url = "https://www.publicdomainpictures.net/pictures/270000/velka/cat-silhouette-sitting-clipart-1535435479JQZ.jpg"


class Pet(db.Model):
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(30), nullable=False)

    species = db.Column(db.String(30), nullable=False)

    photo_url = db.Column(db.String(300), default=default_url)

    age = db.Column(db.Integer)

    notes = db.Column(db.String(500))

    available = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        p = self
        return f"<Pet id={p.id} name={p.name} species={p.species} photo_url={p.photor_url} age={p.age} notes={p.notes} available={p.available}>"
