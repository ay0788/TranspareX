from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# Database setup (Postgres/MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tx:tx25@localhost:5432/transparex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Fund Model
class Fund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    date_disbursed = db.Column(db.DateTime, nullable=False)

@app.route('/')
def home():
    return 'Welcome to TranspareX: Revolutionizing Fund Management with AI and Blockchain!'

# Endpoint to fetch funds data
@app.route('/api/funds', methods=['GET'])
def get_funds():
    try:
        funds = Fund.query.all()
        funds_list = [{
            'recipient': fund.recipient,
            'amount': fund.amount,
            'date_disbursed': fund.date_disbursed.isoformat()
        } for fund in funds]

        return jsonify({'funds': funds_list})
    except Exception as e:
        raise BadRequest('Failed to fetch funds data.')

if __name__ == '__main__':
    app.run(debug=True)
