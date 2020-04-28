from flask import Flask, make_response, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_wtf import FlaskForm
import Model as md
import os

#Init Application
app = Flask(__name__)
#Specify the base directory
basedir = os.path.abspath(os.path.dirname(__file__))
#Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
#Init database
db = SQLAlchemy(app)
#Init marshmallow
ma = Marshmallow(app)
#Routing
@app.route("/")
def welcome():
    return render_template('welcome.html', directory=md.basedir)
"""Cards"""
@app.route("/card/<language>/<id>/<side>")
def getSingleCard(language, id, side):
    if side == 'recto':
        return render_template('recto.html', title=language, number=id, side=side, word='reka', translation='hand')
    elif side == 'verso':
        return render_template('verso.html', title=language, number=id, side=side, word='reka', translation='hand')

@app.route("/api/<language>/card/<id>", methods=['GET', 'PUT', 'DELETE'])
def responseSingleCard(language, id):
    if request.method == 'GET':
        return md.getApiCard(language, id)
    elif request.method == 'PUT':
        return md.updateApiCard(language, id)
    elif request.method == 'DELETE':
        return md.removeApiCard(language, id)

@app.route("/api/<language>/card", methods=['GET','POST'])
def responseCards(language):
    if request.method == 'POST':
        return md.addCard(language)
    elif request.method == 'GET':
        return md.getAllCards(language)
    else:
        abort(404)

"""Categories"""
@app.route("/api/category", methods=['GET','POST'])
def responseCategories():
    if request.method == 'POST':
        return md.addCategory()
    elif request.method == 'GET':
        return md.getAllCategories()
    else:
        abort(404)

"""Levels"""
@app.route("/api/level", methods=['GET','POST'])
def responseLevels():
    if request.method == 'POST':
        return md.addLevel()
    elif request.method == 'GET':
        return md.getAllLevels()
    else:
        abort(404)
#Run Server
if __name__ == '__main__':
    app.run(debug=True)