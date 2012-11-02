from google.appengine.ext import db

class Users(db.Model):
    facebookID = db.StringProperty()
    accessToken = db.StringProperty()
    email = db.EmailProperty()
    
class AllUsers(db.Model):
    facebookID = db.StringProperty()
    name = db.StringProperty()
    birthday = db.IntegerProperty()
    email = db.EmailProperty()
    accessToken = db.StringProperty()

class Settings(db.Model):
    name = db.StringProperty()
    birthday = db.DateTimeProperty()