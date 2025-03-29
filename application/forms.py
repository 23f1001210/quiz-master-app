from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

# class for user search
class userForm(FlaskForm):    
    name = StringField('user Name')    
    submit = SubmitField('Search')

# class for subject search
class subjectForm(FlaskForm):
    name = StringField('subject name')
    submit = SubmitField('Search')

#class for quiz search
class quizForm(FlaskForm):
    id = StringField('quiz id')
    submit = SubmitField('Search')

#class for quiz search based on date
class dateSearch(FlaskForm):
    date = StringField('date')
    submit = SubmitField('Search')
    
#class for score search based on the quiz id
class scoreSearch(FlaskForm):
    score = StringField('score')
    submit = SubmitField('Search')

#class for searching question by admin
class questionSearch(FlaskForm):
    question = StringField('question')
    submit = SubmitField('Search')