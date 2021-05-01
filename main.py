from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
import os

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email, DataRequired

app = Flask(__name__)
if os.name == 'nt':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\hende\\AppData\\Roaming\\mydatabase.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/db.db'
db = SQLAlchemy(app)

@app.route("/")
def hello():
    return render_template('pages/index.html')

class RegisterForm(FlaskForm):
	name        = StringField  (u'Name'      )
	username    = StringField  (u'Username'  , validators=[DataRequired()])
	password    = PasswordField(u'Password'  , validators=[DataRequired()])
	email       = StringField  (u'Email'     , validators=[DataRequired(), Email()])

@app.route("/register")
def register():
    form = RegisterForm(csrf_enabled=False)
    return render_template('pages/register.html', form=form)

@app.route("/compare")
def search():
    return render_template('pages/compare.html')

@app.route('/allusers')
def all_users():
    return str(User.query.all())

@app.route('/redirect')
def new_user():
    user = User(data=UserData())
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('user', id=user.id))

@app.route('/user/<id>')
def user(id):
    return str(User.query.get(id).data)

members = db.Table('members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.PickleType(), nullable=False)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    members = db.relationship(User, secondary=members, lazy='subquery', backref=db.backref('groups', lazy=True))

class Doorsness(Enum):
    OUTDOORS=0
    WHO_CARE=1

class Maskedness(Enum):
    MASKED=0
    WHO_CARE=1

class Distanced(Enum):
    DISTANCED=0
    WHO_CARE=1

class Vaccinated(Enum):
    ALL=0
    ALL_BUT_ONE=1
    WHO_CARE=2

class Food(Enum):
    NO=0
    BRING_OWN=1
    WHO_CARE=2

class UserData(object):
    def __init__(self):
        self._data = [False] * (len(Doorsness) * len(Maskedness) * len(Distanced) * len(Vaccinated) * len(Food))
        self.vaccinated_date = datetime.max

    def ok_with(self, doorsness, maskedness, distanced, vaccine, food):
        return self._data[
            doorsness * (len(Maskedness) * len(Distanced) * len(Vaccinated) * len(Food)) + maskedness * (len(Distanced) * len(Vaccinated) * len(Food)) + distanced * (len(Vaccinated) * len(Food)) + vaccine * len(Food) + food]

    def set_ok(self, doorsness, maskedness, distanced, vaccine, food, ok):
        self._data[doorsness * (len(Maskedness) * len(Distanced) * len(Vaccinated) * len(Food)) + maskedness * (len(Distanced) * len(Vaccinated) * len(Food)) + distanced * (len(Vaccinated) * len(Food)) + vaccine * len(Food) + food] = ok

    def __str__(self):
        return str(self._data) + str(self.vaccinated_date)

db.create_all()
