from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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

    def __repr__(self):
        return f'<User {self.user_id}>'

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'password': self.password,
            'full_name': self.full_name,
            'qualification': self.qualification,
            'date_of_birth': self.date_of_birth
        }


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

    def __repr__(self):
        return f'<Chapter {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject_id': self.subject_id
        }


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duration = db.Column(db.String(10))  
    remarks = db.Column(db.Text)

    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

    def __repr__(self):
        return f'<Quiz {self.id} - {self.chapter.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'date_of_quiz': self.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': self.duration,
            'remarks': self.remarks
        }


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  

    def __repr__(self):
        return f'<Question {self.id} - {self.quiz.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_statement': self.question_statement,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_option': self.correct_option
        }


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Score User: {self.user.email} - Quiz: {self.quiz.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'total_score': self.total_score
        }
