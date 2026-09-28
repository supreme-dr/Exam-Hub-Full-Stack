import os
import io
import csv
import random
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, abort, Response, send_file, jsonify
)
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Exam, Question, Result, Category, Answer

# ============================================================
# APP SETUP
# ============================================================
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to continue.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


# ============================================================
# PUBLIC ROUTES
# ============================================================
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        else:
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if not check_password_hash(current_user.password_hash, current):
            flash('Current password is incorrect.', 'danger')
        elif len(new) < 6:
            flash('New password must be at least 6 characters.', 'danger')
        elif new != confirm:
            flash('New passwords do not match.', 'danger')
        else:
            current_user.password_hash = generate_password_hash(new)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('profile'))

    return render_template('profile.html')


# ============================================================
# STUDENT ROUTES
# ============================================================
@app.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    taken_exam_ids = {r.exam_id for r in Result.query.filter_by(user_id=current_user.id)}
    results = Result.query.filter_by(user_id=current_user.id) \
                          .order_by(Result.completed_at.desc()).limit(5).all()
    return render_template('dashboard.html',
                           categories=categories,
                           taken_exam_ids=taken_exam_ids,
                           results=results)


@app.route('/exam/<int:id>', methods=['GET', 'POST'])
@login_required
def take_exam(id):
    exam = Exam.query.get_or_404(id)

    if not exam.is_open:
        flash('This exam is not currently open.', 'warning')
        return redirect(url_for('dashboard'))

    existing = Result.query.filter_by(user_id=current_user.id, exam_id=id).first()
    if existing:
        flash('You have already taken this exam.', 'warning')
        return redirect(url_for('result', result_id=existing.id))

    if not exam.questions:
        flash('This exam has no questions yet.', 'warning')
        return redirect(url_for('dashboard'))

    pool = list(exam.questions)
    pick_count = min(exam.questions_per_attempt or 50, len(pool))
    selected = random.sample(pool, pick_count)

    if request.method == 'POST':
        tab_switches = request.form.get('tab_switches', 0, type=int)
        score = 0

        result = Result(
            user_id=current_user.id,
            exam_id=exam.id,
            score=0,
            total_questions=pick_count,
            tab_switches=tab_switches
        )
        db.session.add(result)
        db.session.flush()

        for q in selected:
            chosen = request.form.get(f'q_{q.id}')
            is_correct = bool(chosen and chosen.upper() == q.correct_answer)
            if is_correct:
                score += 1
            db.session.add(Answer(
                result_id=result.id,
                question_id=q.id,
                chosen=chosen.upper() if chosen else None,
                is_correct=is_correct
            ))

        result.score = score
        db.session.commit()
        return redirect(url_for('result', result_id=result.id))

    return render_template('take_exam.html', exam=exam, questions=selected)


@app.route('/result/<int:result_id>')
@login_required
def result(result_id):
    result = Result.query.get_or_404(result_id)
    if result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('result.html', result=result)


@app.route('/result/<int:result_id>/review')
@login_required
def review(result_id):
    result = Result.query.get_or_404(result_id)
    if result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('review.html', result=result)


@app.route('/result/<int:result_id>/certificate')
@login_required
def certificate(result_id):
    result = Result.query.get_or_404(result_id)
    if result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    if result.percentage < 80:
        flash('Certificate requires at least 80%.', 'warning')
        return redirect(url_for('result', result_id=result.id))

    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
    except ImportError:
        flash('Certificate feature requires reportlab. Run: pip install reportlab', 'danger')
        return redirect(url_for('result', result_id=result.id))

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4))
    w, h = landscape(A4)

    # Border
    c.setStrokeColor(HexColor('#764ba2'))
    c.setLineWidth(6)
    c.rect(1*cm, 1*cm, w - 2*cm, h - 2*cm)
    c.setStrokeColor(HexColor('#667eea'))
    c.setLineWidth(2)
    c.rect(1.4*cm, 1.4*cm, w - 2.8*cm, h - 2.8*cm)

    # Title
    c.setFillColor(HexColor('#1a1a2e'))
    c.setFont('Helvetica-Bold', 40)
    c.drawCentredString(w/2, h - 4*cm, 'Certificate of Achievement')

    # Subtitle
    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(w/2, h - 5.2*cm, 'This certificate is proudly presented to')

    # Name
    c.setFillColor(HexColor('#667eea'))
    c.setFont('Helvetica-Bold', 32)
    c.drawCentredString(w/2, h - 7.5*cm, result.student.username)

    # Body
    c.setFillColor(HexColor('#1a1a2e'))
    c.setFont('Helvetica', 14)
    c.drawCentredString(w/2, h - 9*cm, 'for successfully completing')

    c.setFont('Helvetica-Bold', 20)
    c.drawCentredString(w/2, h - 10.5*cm, result.exam.title)

    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(w/2, h - 12*cm,
                        f'with a score of {result.score}/{result.total_questions} '
                        f'({result.percentage}%) — Grade {result.grade}')

    # Date
    c.setFont('Helvetica', 11)
    c.drawCentredString(w/2, 3*cm,
                        f'Issued on {result.completed_at.strftime("%B %d, %Y")} · ExamHub')

    c.showPage()
    c.save()
    buf.seek(0)

    filename = f'certificate_{result.student.username}_{result.exam.id}.pdf'
    return send_file(buf, as_attachment=True, download_name=filename,
                     mimetype='application/pdf')


@app.route('/my-results')
@login_required
def my_results():
    results = Result.query.filter_by(user_id=current_user.id) \
                          .order_by(Result.completed_at.desc()).all()
    return render_template('my_results.html', results=results)


# ============================================================
# ADMIN ROUTES
# ============================================================
@app.route('/admin')
@admin_required
def admin_dashboard():
    exams = Exam.query.order_by(Exam.created_at.desc()).all()
    categories = Category.query.all()
    total_students = User.query.filter_by(is_admin=False).count()
    total_attempts = Result.query.count()
    return render_template('admin_dashboard.html', exams=exams,
                           categories=categories,
                           total_students=total_students,
                           total_attempts=total_attempts)


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    exams = Exam.query.all()
    data = []
    for exam in exams:
        results = Result.query.filter_by(exam_id=exam.id).all()
        if results:
            scores = [r.percentage for r in results]
            data.append({
                'exam': exam,
                'attempts': len(results),
                'avg': round(sum(scores) / len(scores), 1),
                'high': max(scores),
                'low': min(scores),
                'pass_rate': round(sum(1 for s in scores if s >= 50) / len(scores) * 100, 1),
            })

    category_stats = []
    for cat in Category.query.all():
        cat_exams = Exam.query.filter_by(category_id=cat.id).all()
        exam_ids = [e.id for e in cat_exams]
        results = Result.query.filter(Result.exam_id.in_(exam_ids)).all() if exam_ids else []
        category_stats.append({
            'category': cat,
            'attempts': len(results),
            'avg': round(sum(r.percentage for r in results) / len(results), 1) if results else 0,
        })

    return render_template('admin_analytics.html', data=data, category_stats=category_stats)


@app.route('/admin/export-results')
@admin_required
def export_results():
    results = Result.query.order_by(Result.completed_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student', 'Exam', 'Category', 'Score',
                     'Total', 'Percentage', 'Grade', 'Tab Switches', 'Completed'])

    for r in results:
        writer.writerow([
            r.student.username,
            r.exam.title,
            r.exam.category.name,
            r.score,
            r.total_questions,
            f'{r.percentage}%',
            r.grade,
            r.tab_switches,
            r.completed_at.strftime('%Y-%m-%d %H:%M'),
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=exam_results.csv'}
    )


@app.route('/admin/exam/new', methods=['GET', 'POST'])
@admin_required
def admin_create_exam():
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        duration = request.form.get('duration_minutes', type=int)
        category_id = request.form.get('category_id', type=int)
        per_attempt = request.form.get('questions_per_attempt', type=int) or 50

        if not title or not duration or not category_id:
            flash('Title, category, and duration are required.', 'danger')
        else:
            exam = Exam(
                title=title, description=description,
                duration_minutes=duration, category_id=category_id,
                questions_per_attempt=per_attempt
            )
            db.session.add(exam)
            db.session.commit()
            flash('Exam created! Now add questions.', 'success')
            return redirect(url_for('admin_questions', exam_id=exam.id))

    return render_template('admin_exam_form.html', exam=None, categories=categories)


@app.route('/admin/exam/<int:exam_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    categories = Category.query.all()

    if request.method == 'POST':
        exam.title = request.form.get('title', '').strip()
        exam.description = request.form.get('description', '').strip()
        exam.duration_minutes = request.form.get('duration_minutes', type=int)
        exam.category_id = request.form.get('category_id', type=int)
        exam.questions_per_attempt = request.form.get('questions_per_attempt', type=int) or 50
        db.session.commit()
        flash('Exam updated.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_exam_form.html', exam=exam, categories=categories)


@app.route('/admin/exam/<int:exam_id>/delete', methods=['POST'])
@admin_required
def admin_delete_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    flash('Exam deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/exam/<int:exam_id>/questions', methods=['GET', 'POST'])
@admin_required
def admin_questions(exam_id):
    exam = Exam.query.get_or_404(exam_id)

    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        a = request.form.get('option_a', '').strip()
        b = request.form.get('option_b', '').strip()
        c = request.form.get('option_c', '').strip()
        d = request.form.get('option_d', '').strip()
        correct = request.form.get('correct_answer', '').upper()
        difficulty = request.form.get('difficulty', 'Medium')

        if not all([text, a, b, c, d]) or correct not in ['A', 'B', 'C', 'D']:
            flash('All fields required. Correct answer must be A, B, C, or D.', 'danger')
        else:
            db.session.add(Question(
                exam_id=exam.id, text=text, option_a=a, option_b=b,
                option_c=c, option_d=d, correct_answer=correct,
                difficulty=difficulty
            ))
            db.session.commit()
            flash('Question added!', 'success')
        return redirect(url_for('admin_questions', exam_id=exam.id))

    return render_template('admin_questions.html', exam=exam)


@app.route('/admin/question/<int:q_id>/delete', methods=['POST'])
@admin_required
def admin_delete_question(q_id):
    q = Question.query.get_or_404(q_id)
    exam_id = q.exam_id
    db.session.delete(q)
    db.session.commit()
    flash('Question deleted.', 'success')
    return redirect(url_for('admin_questions', exam_id=exam_id))


@app.route('/admin/category/new', methods=['POST'])
@admin_required
def admin_create_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', '📘').strip() or '📘'

    if not name:
        flash('Category name is required.', 'danger')
    elif Category.query.filter_by(name=name).first():
        flash('That category already exists.', 'danger')
    else:
        db.session.add(Category(name=name, description=description, icon=icon))
        db.session.commit()
        flash(f'Category "{name}" created!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/results')
@admin_required
def admin_results():
    results = Result.query.order_by(Result.completed_at.desc()).all()
    return render_template('admin_results.html', results=results)


# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# ============================================================
# CREATE TABLES
# ============================================================
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
    