import email
from flask import Flask, request, abort, jsonify
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_json import MutableJson
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
db = SQLAlchemy(app)

## MODEL DEFINITION ##
@dataclass
class MedicalData(db.Model):
    user_id: int
    gender: str
    blood_type: str
    donations: list
    # user: User

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, primary_key=True)
    # user = db.relationship(User, backref="users")
    gender = db.Column(db.String(1), nullable=False) # M: Male, F: Female
    blood_type = db.Column(db.String(4), nullable=False)
    # List of dates (at least 3 months between dates for male and 4 months for female)
    donations = db.Column(MutableJson)

@dataclass
class User(db.Model):
    id: int
    email: str
    password: str
    name: str
    last_name: str
    medical_data: MedicalData

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    medical_data = db.relationship(MedicalData)



## HELPERS ##
def get_json_or_die(request):
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        return json
    else:
        abort(400, 'Body not Json!') 

## SERVER DEFINITION ##
# TODO: to be removed
@app.route("/users", methods = ['GET'])
def get_users():
    return jsonify(User.query.all())

# { 
#   email: '', password: '', 
#   medical_data: { blood_type: '', gender: '' }
# }
@app.route("/user", methods = ['POST'])
def create_user():
    body = get_json_or_die(request)
    user = User(
        email= body['email'], 
        password= body['password'],
        name = body['name'],
        last_name = body['last_name'])
    medical = MedicalData(
        user=user, 
        blood_type= body['medical_data']['blood_type'], 
        gender=body['medical_data']['gender'])
    db.session.add(user)
    db.session.add(medical)
    db.session.commit()
    return "Created!", 201

@app.route("/user/<id>", methods = ['GET'])
def get_user(id):
    return jsonify(User.query.get(id))

# No need for new/old password as auth will be handled by JWT
# { 
#   email: '', password: '',
#   medical_data: { blood_type: '', gender: '' }
# }
@app.route("/user/<id>", methods = ['PUT'])
def update_user(id):
    return json.dumps(User.query.get(id))

@app.route("/user/<id>/donations", methods = ['GET'])
def get_donations(id):
    return jsonify((MedicalData.query.get(id)).donations)

# { date: 'yyy-MM-dd' } [optional, if not present use today]
@app.route("/user/<id>/donations", methods = ['PUT'])
def put_donation(id):
    body = get_json_or_die(request)
    return "Donation added!"

## RUNTIME DEFINITION ##
app.run(host="0.0.0.0")