from FlashCards import db, ma, basedir
from flask import make_response, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import os,logging, epitran, string, random, abc
from datetime import datetime

"""Log handler"""
#Specify the error handler
log_handler= datetime.now().strftime(basedir+'logfile_%H_%M_%S_%d_%m_%Y.log')
logging.basicConfig(filename=log_handler,level=logging.DEBUG)

"""Database classes"""
#Card interface
class Card(db.Model):
    #Automatically appended id
    id = db.Column(db.Integer, primary_key=True)
    #Category id
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    #Level id
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    #Default name of the word in Polish
    name = db.Column(db.String(30), unique=True, nullable=False)
    #wordType of the word
    wordType = db.Column(db.String(20), unique=True)
    #Constructor
    def __init__(self, name, wordType, category_id, level_id):
        self.name = name
        self.wordType = wordType
        self.category_id = category_id
        self.level_id = level_id
    #Representation
    def __repr__(self):
        return '{self.__class__.__name__}({self.name},{self.wordType})'.format(self=self)
    #Card recognition
    def __str__(self):
        return '<{self.name}:{self.id}>'.format(self=self)
    #Add translation
    @abc.abstractmethod
    def translate(self, word):
        pass
    #Add example
    @abc.abstractmethod
    def example(self, expression, language):
        pass
#Language fiche
class CardLanguage(Card):
#Phonetic writting
    phonetic = db.Column(db.String(30), unique=True, nullable=True)
#Translation
    translation = db.Column(db.String(30), unique=False)
# Example of the word
    example = db.Column(db.String(200), unique=False)
    def __init__(self, phonetic, translation, example):
        super().__init__(self, name, wordType)
    def translate(self, word):
        self.translation = word
    def example(self, expression):
        self.example = expression

"""Inherited fiches of the cardlanguage which represent the specific language"""
class FicheEng(CardLanguage):
    #Phonetic translation
    eng = epitran.Epitran('eng-Latn')
    #Apply phonetic translation
    def translate(self, word):
        self.phonetic = eng.transliterate(unicode(word, 'utf-8'))

class FicheFr(CardLanguage):
    #Phonetic translation
    fr = epitran.Epitran('fra-Latn')
    #Apply phonetic translation
    def translate(self, word):
        self.phonetic = fr.transliterate(unicode(word, 'utf-8'))

class FicheSp(CardLanguage):
    #Phonetic translation
    sp = epitran.Epitran('spa-Latn')
    #Apply phonetic translation
    def translate(self, word):
        self.phonetic = sp.transliterate(unicode(word, 'utf-8'))

#Category class
class Category(db.Model):
    #Automatically appended id
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False)
    #Relationship colum - artificial
    words = db.relationship('Card', backref='card.id', lazy=True)
    #Constructor
    def __init__(self, name, description):
        self.name = name
        self.description = description
    #Representation
    def __repr__(self):
        return '{self.__class__.__name__}({self.name})'.format(self=self)
    #Category recognition
    def __str__(self):
        return '<{self.name}:{self.id}>'.format(self=self)

#Levels class
class Level(db.Model):
    #Automatically append id
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False, unique=True)
    # Relationship colum - artificial
    #words = db.relationship('Card', backref='card.id', lazy=True)
    #Constructor
    def __init__(self, name, description):
        self.name = name
        self.description = description
    #Representation
    def __repr__(self):
        return '{self.__class__.__name__}({self.name})'.format(self=self)
    #Level recognition
    def __str__(self):
        return '<{self.name}:{self.id}>'.format(self=self)

#User class
class User(db.Model):
    #Automatic append id
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(30), nullable=False, unique=False)
    secondName = db.Column(db.String(30), nullable=False, unique=False)
    login = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    rightsLevel = db.Column(db.Integer, nullable=False, unique=False)
    passwordHash = db.Column(db.String(128), nullable=False)
    #Constructor
    def __init__(self, login, email, passwordHash, rightsLevel):
        self.login = login
        self.email = email
        self.passwordHash = passwordHash
        self.rightsLevel = rightsLevel
    # Representation
    def __repr__(self):
        return '{self.__class__.__name__}({self.login},{self.email},{self.rightsLevel})'.format(self=self)
    # User recognition
    def __str__(self):
        return '<{self.login}>'.format(self=self)
    #Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def generate_password(self):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(12))

#Serialized cards
class CardSchema(ma.Schema):
    class Meta:
        fields=('id','category_id','level_id','name','phonetic','wordType','translation',
                'example')
#Serialized categories
class CategorySchema(ma.Schema):
    class Meta:
        fields=('id', 'name', 'description', 'words')
#Serialized levels
class LevelSchema(ma.Schema):
    class Meta:
        fields=('id', 'name', 'description', 'words')

#Init schema
cardSchema = CardSchema()
cardsSchema = CardSchema(many=True)
categorySchema = CategorySchema()
categoriesSchema = CategorySchema(many=True)
levelSchema = LevelSchema()
levelsSchema = LevelSchema(many=True)

"""Model functions"""
#Single card operations
def getApiCard(language, id):
    if language == 'eng':
        card = FicheEng.query.get(id)
        return cardSchema.jsonify(card)
    elif language == 'fr':
        card = FicheFr.query.get(id)
        return cardSchema.jsonify(card)
    elif language == 'sp':
        card = FicheSp.query.get(id)
        return cardSchema.jsonify(card)
    else:
        abort(404)

def updateApiCard(language, id):
    name = request.json['name']
    wordType = request.json['wordType']
    example = request.json['example']
    translation = request.json['translation']
    phonetic = request.json['phonetic']
    category_id = request.json['category_id']
    level_id = request.json['level_id']
    if language == 'eng':
        card = FicheEng.query.get(id)
    elif language == 'fr':
        card = FicheFr.query.get(id)
    elif language == 'sp':
        card = FicheSp.query.get(id)
    else:
        abort(404)
    card.name = name
    card.wordType = wordType
    card.example = example
    card.translation = translation
    card.phonetic = phonetic
    card.category_id = category_id
    card.level_id = level_id
    db.session.commit()
    return cardSchema.jsonify(card)

def removeApiCard(language, id):
    if language == 'eng':
        card = FicheEng.query.get(id)
    elif language == 'fr':
        card = FicheFr.query.get(id)
    elif language == 'sp':
        card = FicheSp.query.get(id)
    else:
        abort(404)
    db.session.delete(card)
    db.commit()
    return cardSchema.jsonify(card)

#Card group
def addCard(language):
    name = request.json['name']
    wordType = request.json['wordType']
    example = request.json['example']
    translation = request.json['translation']
    phonetic = request.json['phonetic']
    category_id = request.json['category_id']
    level_id = request.json['level_id']
    if language == 'eng':
        newCard = Card(name, wordType)
        newFiche = FicheEng(phonetic, translation, example)
    elif language == 'fr':
        newCard = Card(name, wordType)
        newFiche = FicheFr(phonetic, translation, example)
    elif language == 'sp':
        newCard = Card(name, wordType)
        newFiche = FicheSp(phonetic, translation, example)
    else:
        abort(404)
    db.session.add(newFiche)
    db.session.commit()
    return cardSchema.jsonify(newFiche)

def getAllCards(language):
    if language == 'eng':
        allCards = FicheEng.query.all()
    elif language == 'fr':
        allCards = FicheFr.query.all()
    elif language == 'sp':
        allCards = FicheSp.query.all()
    else:
        abort(404)
    result = cardsSchema.dump(allCards)
    return jsonify(result.data)

#Category group
def addCategory():
    name = request.json['name']
    description = request.json['description']
    newCategory = Category(name, description)
    db.session.add(newCategory)
    db.session.commit()
    return categorieSchema.jsonify(newCategory)

def getAllCategories():
    allCategories = Category.query.all()
    result = categoriesSchema.dump(allCategories)
    return jsonify(result.data)

#Level group
def addLevel():
    name = request.json['name']
    description = request.json['description']
    newLevel = Level(name, description)
    db.session.add(newLevel)
    db.session.commit()
    return levelSchema.jsonify(newLevel)

def getAllLevels():
    allLevels = Level.query.all()
    result = levelsSchema.dump(allLevels)
    return jsonify(result.data)






