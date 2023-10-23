from flask import abort, session
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from hashlib import md5
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired,Email




class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)


    
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
  #  posts = db.relationship('Blogpost', backref='user', passive_deletes=True)



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=False)
    text = db.Column(db.String(200), nullable=False)
    email =  db.Column(db.String(150), unique=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String(200), nullable = False, default = "pending")
    approved = db.Column(db.Boolean, default=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'blogpost.id', ondelete="CASCADE"), nullable=False)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send") 
