from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\hende\\AppData\\Roaming\\mydatabase.db'
db = SQLAlchemy(app)

@app.route("/")
def hello():
    return render_template('pages/index.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/search")
def search():
    return render_template('search.html')

@app.route('/allusers')
def all_users():
    return str(User.query.all())

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

db.create_all()
