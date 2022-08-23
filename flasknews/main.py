import os
from flask import Flask, jsonify
from routes.admin import admins
from routes.post import posts
from routes.user import users
from db import db
from models.user import *
from models.post import *



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@db/{os.getenv('DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.register_blueprint(admins)
app.register_blueprint(posts)
app.register_blueprint(users)


@app.route('/')
def welcome():
    return jsonify({'message': 'Hello world!'})






if __name__ == '__main__':
    # db.drop_all(app=app)
    db.create_all(app=app)
    app.run(host='0.0.0.0')