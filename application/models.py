from flask_sqlalchemy import SQLAlchemy
from datetime import date , datetime

db = SQLAlchemy()

#User table
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    qualification = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)

    def __init__(self, email, password, full_name, qualification, date_of_birth):
        self.email = email
        self.password = password
        self.full_name = full_name
        self.qualification = qualification
        self.date_of_birth = date_of_birth

    def to_dict(self):
        return{
            'user_id' : self.user_id,
            'email': self.email, 
            'password' : self.password, 
            'full_name' : self.full_name, 
            'qualification' : self.qualification, 
            'date_of_birth' : self.date_of_birth 
        }

#admin table
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)    

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
    }

#Subjects table
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    #SQLAlchemy relatinship method
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan")

    def __init__(self,id,name,description):
        self.id = id
        self.name = name
        self.description = description

#chapter table
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'),nullable=False)#foreign key
    #SQLAlchemy relatinship method
    quizzes = db.relationship('Quiz', backref='chapter',cascade="all,delete-orphan")

    def __init__(self,id,name,description,subject_id):
        self.id = id
        self.name = name
        self.description = description
        self.subject_id = subject_id    

#quiz table
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"),nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False, default=date)
    duration = db.Column(db.String(10))  # HH:MM:SS format
    remarks = db.Column(db.Text)    
    #SQLAlchemy relatinship method
    questions = db.relationship('Question', backref='quiz',cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='quiz',cascade="all, delete-orphan")

    def __init__(self,id,chapter_id,date_of_quiz,duration,remarks):
        self.id = id
        self.chapter_id = chapter_id
        self.date_of_quiz = date_of_quiz
        self.duration = duration
        self.remarks = remarks        

#question table
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'),nullable=False)
    question_title = db.Column(db.String(30),nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)# Stores 1, 2, 3, or 4    
    image_path = db.Column(db.String(255), nullable=True)  # Path to image file
    audio_path = db.Column(db.String(255), nullable=True)  # Path to audio file

    def __init__(self,id,quiz_id,question_title,question_statement,option1,option2,option3,option4,correct_option,image_path,audio_path):
        self.id=id
        self.quiz_id=quiz_id
        self.question_title=question_title
        self.question_statement=question_statement
        self.option1=option1
        self.option2=option2
        self.option3=option3
        self.option4=option4
        self.correct_option=correct_option 
        self.image_path=image_path
        self.audio_path=audio_path    

#score table
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True ,autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False)
   
    def __init__(self,quiz_id,user_id,timestamp,total_score):
        self.quiz_id = quiz_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.total_score = total_score
