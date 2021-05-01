from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
import os
import itertools

app = Flask(__name__)
if os.name == 'nt':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\hende\\AppData\\Roaming\\mydatabase.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/db.db'
db = SQLAlchemy(app)

@app.route("/")
def hello():
    return render_template('pages/index.html')

@app.route("/register")
def register():
    return render_template('pages/register.html')

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

@app.route('/user/<id>/set_ok')
def set_okness(id):
    doorsness=Doorsness[request.args.get('doorsness')]
    maskedness=Maskedness[request.args.get('maskedness')]
    distanced=Distanced[request.args.get('distanced')]
    vaccinated=Vaccinated[request.args.get('vaccinated')]
    food=Food[request.args.get('food')]
    user = User.query.get(id)
    user.data = user.data.with_ok(doorsness, maskedness, distanced, vaccinated, food, True)
    db.session.add(user)
    print(user.data.ok_with(doorsness, maskedness, distanced, vaccinated, food))
    db.session.commit()
    print(user.data.ok_with(doorsness, maskedness, distanced, vaccinated, food))
    return redirect(url_for('user', id=user.id))


@app.route('/user/<id>/set_not_ok')
def set_not_okness(id):
    doorsness=Doorsness[request.args.get('doorsness')]
    maskedness=Maskedness[request.args.get('maskedness')]
    distanced=Distanced[request.args.get('distanced')]
    vaccinated=Vaccinated[request.args.get('vaccinated')]
    food=Food[request.args.get('food')]
    user = User.query.get(id)
    user.data = user.data.with_ok(doorsness, maskedness, distanced, vaccinated, food, False)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('user', id=user.id))


@app.route('/group/<id>')
def get_group(id):
    group = Group.query.get(id)
    okness = [all(user.data.ok_with(door, mask, dist, vacc, food))
    for door, mask, dist, vacc, food in itertools.product(Doorsness, Maskedness, Distanced, Vaccinated, Food)]
    return str(okness)

@app.route('group/<gid>/user/<uid>')
def update_group(gid, uid):
    # this is a dumb way to do this so don't.
    pass


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

class UserData(Mutable):
    def __init__(self):
        self._data = [False] * (len(Doorsness) * len(Maskedness) * len(Distanced) * len(Vaccinated) * len(Food))
        self.vaccinated_date = datetime.max

    def ok_with(self, doorsness, maskedness, distanced, vaccine, food):
        return self._data[
            doorsness.value * (len(Maskedness) * len(Distanced) * len(Vaccinated) * len(Food)) + maskedness.value * (len(Distanced) * len(Vaccinated) * len(Food)) + distanced.value * (len(Vaccinated) * len(Food)) + vaccine.value * len(Food) + food.value]

    def with_ok(self, doorsness, maskedness, distanced, vaccine, food, ok):
        ud = UserData()
        ud.vaccinated_date = self.vaccinated_date
        ud._data = self._data
        ud._data[doorsness.value * (len(Maskedness) * len(Distanced) * len(Vaccinated) * len(Food)) + maskedness.value * (len(Distanced) * len(Vaccinated) * len(Food)) + distanced.value * (len(Vaccinated) * len(Food)) + vaccine.value * len(Food) + food.value] = ok
        return ud

    def with_vaccinated_date(self, date)
        ud = UserData()
        ud._data = self._data
        ud.vaccinated_date = date
        return ud

    def __str__(self):
        return str(self._data) + str(self.vaccinated_date)

db.create_all()
