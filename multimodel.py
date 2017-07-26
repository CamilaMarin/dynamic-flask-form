# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import FieldList
from wtforms import Form as NoCsrfForm
from wtforms.fields import StringField, FormField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

"""
   Simple example to load and save a User instance with related phone
   entries in a WTForm
"""


# - - - Models - - -
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(40))
    phones = db.relationship('Phone')
    # this 'phones' match names with the form 'phones' or populate_obj fails


class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    phone_number = db.Column(db.String(50))
    phone_name = db.Column(db.String(50))


# - - - Forms - - -
class PhoneForm(NoCsrfForm):
    # this forms is never exposed so we can user the non CSRF version
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    phone_name = StringField('Phone Description')


class CombinedForm(Form):
    username = StringField('User', validators=[DataRequired()])
    # we must provide empth Phone() instances else populate_obj will fail
    phones = FieldList(FormField(PhoneForm, default=lambda: Phone()), min_entries=1)
    submit = SubmitField('Submit')


# - - - Routes - - -
@app.route('/', methods=['GET', 'POST'])
def index():
    # always "blindly" load the user
    user = User.query.first()

    # forms loaded through db relation
    form = CombinedForm(obj=user)

    if request.method == 'POST':
        # remove the hidden first entry (to be able to have no entries)
        hidden_entry = form.phones.entries.pop(0)
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.commit()
            flash("Saved Changes")
        form.phones.entries.insert(0, hidden_entry)
    return render_template('multi.html', form=form)


# - - - Execute - - -
def prep_db():
    db.drop_all()
    db.create_all()
    db.session.add(User(username='Umberto'))
    db.session.commit()

if __name__ == '__main__':
    prep_db()
    app.run(debug=True, port=5002)
