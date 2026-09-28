from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('Result', backref='student', lazy=True,
                              cascade='all, delete-orphan')

    def __repr__(self):
        role = 'Admin' if self.is_admin else 'Student'
        return f'<User {self.username} ({role})>'


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(10), default='📘')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exams = db.relationship('Exam', backref='category', lazy=True,
                            cascade='all, delete-orphan')


class Exam(db.Model):
    __tablename__ = 'exam'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    questions_per_attempt = db.Column(db.Integer, default=50)
    opens_at = db.Column(db.DateTime, nullable=True)
    closes_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='exam', lazy=True,
                                cascade='all, delete-orphan')
    results = db.relationship('Result', backref='exam', lazy=True,
                              cascade='all, delete-orphan')

    @property
    def is_open(self):
        now = datetime.utcnow()
        if self.opens_at and now < self.opens_at:
            return False
        if self.closes_at and now > self.closes_at:
            return False
        return True


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    difficulty = db.Column(db.String(10), default='Medium')  # Easy, Medium, Hard


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    tab_switches = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('Answer', backref='result', lazy=True,
                              cascade='all, delete-orphan')

    @property
    def percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)

    @property
    def passed(self):
        return self.percentage >= 40

    @property
    def grade(self):
        p = self.percentage
        if p >= 70: return 'A'
        if p >= 60: return 'B'
        if p >= 50: return 'C'
        if p >= 40: return 'D'
        return 'F'


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    chosen = db.Column(db.String(1), nullable=True)  # A/B/C/D or None if skipped
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship('Question')