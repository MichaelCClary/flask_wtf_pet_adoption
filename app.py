"""Blogly application."""

from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Pet, default_url
from form import PetForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///adoption_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "dogs4life"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


connect_db(app)
db.create_all()


@app.route('/')
def display_home():
    pets = Pet.query.all()
    return render_template('home.html', pets=pets)


@app.route('/add', methods=["GET", "POST"])
def add_pet():
    form = PetForm()
    if form.validate_on_submit():
        name = form.name.data
        species = form.species.data
        age = form.age.data
        photo_url = form.photo_url.data
        notes = form.notes.data
        available = form.available.data
        photo_url = photo_url if len(photo_url) > 0 else None

        new_pet = Pet(name=name, species=species, age=age,
                      photo_url=photo_url, notes=notes)
        db.session.add(new_pet)
        db.session.commit()
        return redirect("/")
    else:
        return render_template('add_pet.html', form=form)


@app.route("/<int:id>", methods=["GET", "POST"])
def edit_pet(id):
    pet = Pet.query.get_or_404(id)
    form = PetForm(obj=pet)
    if form.validate_on_submit():
        form.photo_url.data = form.photo_url.data if len(
            form.photo_url.data) > 0 else default_url
        pet.name = form.name.data
        pet.species = form.species.data
        pet.photo_url = form.photo_url.data
        pet.notes = form.notes.data
        pet.available = form.available.data
        pet.age = form.age.data

        db.session.commit()
        return redirect("/")
    else:
        return render_template('edit_pet.html', form=form, pet=pet)
