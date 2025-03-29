from application import app
from application.models import *
from flask import render_template, request, redirect, url_for, flash, session
from application.forms import *
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename

#index 
@app.route('/')
def index():    
    session.pop('user',None)
    session.pop('admin',None)
    return render_template('index.html')

#admin login route
@app.route('/adminLogin', methods=['GET', 'POST']) 
def adminLogin():    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for the admin
        admin_user = Admin.query.filter_by(username=email).first()

        if admin_user and admin_user.password == password:
            session['admin'] = admin_user.to_dict()  # Store admin details in session            
            return redirect(url_for('admin'))  # Redirect to admin panel
        if not admin_user or admin_user.password != password:
            flash("Invalid email or password.")
            return redirect(url_for('adminLogin'))

    return render_template('adminLogin.html')

#logout and session clear route
@app.route('/logOut',methods=['GET','POST'])
def logOut():
    session.clear()
    return render_template("index.html")

#admin dashboard route
@app.route('/admin',methods=['GET','POST'])
def admin():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    
    subjects = Subject.query.all()
    for subject in subjects:
        for chapter in subject.chapters:
            # Get all quizzes for this chapter
            quiz_ids = [quiz.id for quiz in Quiz.query.filter_by(chapter_id=chapter.id).all()]            
            # Count all questions for these quizzes
            chapter.question_count = Question.query.filter(Question.quiz_id.in_(quiz_ids)).count()

    search_query = request.form.get('search', '').strip()
    
    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
        quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{search_query}%")).all()
        users = User.query.filter(User.full_name.ilike(f"%{search_query}%")).all()
    else:
        subjects = Subject.query.all()
        quizzes = Quiz.query.all()
        users = User.query.all()
    return render_template('admin.html',subjects=subjects , quizzes=quizzes, users=users, search_query=search_query )

#admin quiz tab route
@app.route("/adminQuiz",methods=['GET','POST'])
def adminQuiz():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 

    quizs = Quiz.query.all()
    return render_template('adminQuiz.html',quizs=quizs)

#register page route
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']        
        email = request.form['email']
        password = request.form['password']     
        qualification=request.form['qualification']   
        date_of_birth=request.form['date_of_birth']
        user = User(email,password,full_name,qualification,date_of_birth)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists! Please use another email.")
            return redirect(url_for('register'))
        try:
            db.session.add(user)
            db.session.commit()
            flash("user created! You can login now")
            return redirect(url_for('userLogin'))
        except :
            db.session.rollback()
            flash("Error registering! recheck entered data")
    return render_template('register.html')

#user login route
@app.route('/userLogin',methods=['GET','POST'])
def userLogin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user'] = user.to_dict()   #Store user details in session                        
            return redirect(url_for('user_dashboard'))  
        if not user or user.password != password:
            flash("Invalid email or password.")
            return redirect(url_for('userLogin'))
    return render_template('userLogin.html')

#user dashboard route
@app.route('/user_dashboard',methods=['GET','POST'])
def user_dashboard():  
    if 'user' not in session:
        flash("Unauthorized access! Please log in as an user.")
        return redirect(url_for('index')) 
    subjects = Subject.query.all()
    data = []

    for subject in subjects:
        quizs = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject.id).all()
        for quiz in quizs:
            quiz.question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        data.append((subject, quizs))

    return render_template('user_dashboard.html', user=session.get('user') , data=data)

#route to add subject
@app.route("/add_subject",methods=['GET','POST'])
def add_subject():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    if request.method == 'POST':
        id= request.form['id']        
        name = request.form['name']
        description= request.form['description']       
        subject = Subject(id,name,description)

        existing_subject = Subject.query.filter(or_(Subject.name == name, Subject.id == id)).first()

        if existing_subject:
            flash("Subject already exists!")
            return redirect(url_for('addSubject'))
        try:
            db.session.add(subject)
            db.session.commit()
            flash("Subject added successfully")
            return redirect(url_for('admin'))
        except:            
            db.session.rollback()
            flash("Error adding subject! recheck entered data")
    return render_template('addSubject.html')   

@app.route("/addSubject",methods=['GET','POST'])
def addSubject():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    return render_template('addSubject.html')  

@app.route("/addQuiz",methods=['GET','POST'])
def addQuiz():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    return render_template('addQuiz.html') 

#route to add quiz
@app.route('/add_quiz',methods=['GET','POST'])
def add_quiz():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    if request.method == 'POST':
        id = request.form['id']        
        chapter_id = request.form['chapterid']
        date_of_quiz = datetime.strptime(request.form['date_of_quiz'], "%Y-%m-%d").date()
        duration=request.form['duration']    
        remarks=request.form['remarks']
        quiz = Quiz(id,chapter_id,date_of_quiz,duration,remarks)

        existing_quiz = Quiz.query.filter_by(id=id).first()
        if existing_quiz:
            flash("quiz already exists!")
            return redirect(url_for('addQuiz'))
        try:
            db.session.add(quiz)
            db.session.commit()
            flash("Quiz added successfully")
            return redirect(url_for('adminQuiz'))
        except Exception as e:            
            print(e)
            db.session.rollback()
            flash("Error adding quiz! recheck entered data")
    return render_template('addQuiz.html')

#route for adding chapter under subject
@app.route("/addChapter",methods=['GET','POST'])
def addChapter():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    return render_template('addChapter.html') 

@app.route("/add_chapter",methods=['GET','POST'])
def add_chapter():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    subject_id = request.args.get('subject_id')
    if subject_id:        
        session['subject_id'] = subject_id
    else:
        subject_id= session.get('subject_id')    

    if request.method == 'POST':
        id= request.form['id']        
        name = request.form['name']
        description= request.form['description']               
        chapter = Chapter(id,name,description,subject_id)
        existing_chapter = Chapter.query.filter(or_(Chapter.name==name , Chapter.id==id)).first()
        if existing_chapter:
            flash("Chapter already exists!")
            return redirect(url_for('addChapter'))
        try:
            db.session.add(chapter)
            db.session.commit()
            flash("Chapter added successfully")
            return redirect(url_for('admin'))
        except:            
            db.session.rollback()
            flash("Error adding chapter! recheck entered data")
    return render_template('addChapter.html') 

#route for adding questions under quiz
@app.route("/addQuestion",methods=['GET','POST'])
def addQuestion():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    return render_template('addQuestion.html') 

@app.route('/add_question',methods=['GET','POST'])
def add_question():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    
    quiz_id = request.args.get('quiz_id')
    if quiz_id:        
        session['quiz_id'] = quiz_id
    else:
        quiz_id = session.get('quiz_id')        
    
    if request.method == 'POST':        
        id = request.form['questionId']        
        question_title = request.form['questionTitle']
        question_statement = request.form['questionStatement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correctOption']
        image = request.files.get('image')
        image_filename = None
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            # Save only filename
        
        # Handle audio upload
        audio = request.files.get('audio')
        audio_filename = None
        if audio and audio.filename != '':
            audio_filename = secure_filename(audio.filename)
            audio.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))
            
        
        question = Question(id,quiz_id,question_title,question_statement,option1,option2,option3,option4,correct_option,image_path=image_filename,audio_path=audio_filename )

        existing_question = Question.query.filter_by(id=id).first()
        if existing_question:
            flash("question already exists!")
            return redirect(url_for('addQuestion'))
        try:
            db.session.add(question)
            db.session.commit()
            flash("Question added successfully")
            return redirect(url_for('adminQuiz'))
        except:            
            db.session.rollback()
            flash("Error adding question! recheck entered data")
    return render_template('addQuestion.html')

#route for deleting a subject
@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    
    subject = Subject.query.get_or_404(subject_id)    
    try:        
        if subject :                   
            db.session.delete(subject)
            db.session.commit()
            flash("Subject deleted successfully!")    
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Error deleting subject")

    return redirect(url_for('admin'))

#route for deleting a quiz
@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    quiz = Quiz.query.get_or_404(quiz_id)    
    try:        
        if quiz:        
            db.session.delete(quiz)
            db.session.commit()
            flash("quiz deleted successfully!")    
    except :
        db.session.rollback()
        flash("Error deleting quiz")

    return redirect(url_for('adminQuiz'))

#route for deleting a chapter
@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    chapter = Chapter.query.get_or_404(chapter_id)    
    try:        
        if chapter:        
            db.session.delete(chapter)
            db.session.commit()
            flash("chapter deleted successfully!")
    
    except :
        db.session.rollback()
        flash("Error deleting chapter")

    return redirect(url_for('admin'))

#route for deleting a question
@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    question = Question.query.get_or_404(question_id)    
   
    image_path = question.image_path
    audio_path = question.audio_path
    upload_folder = app.config['UPLOAD_FOLDER']  # Ensure this is properly set
    
    try:
        # Delete the files if they exist
        if image_path:
            full_image_path = os.path.join(upload_folder, image_path)
            if os.path.exists(full_image_path):
                os.remove(full_image_path)
                print(f"Deleted image file: {full_image_path}")
                
        if audio_path:
            full_audio_path = os.path.join(upload_folder, audio_path)
            if os.path.exists(full_audio_path):
                os.remove(full_audio_path)

        if question:        
            db.session.delete(question)
            db.session.commit()
            flash("question deleted successfully!")
    
    except :
        db.session.rollback()
        flash("Error deleting question")

    
        
    return redirect(url_for('adminQuiz'))

#route for editing a subject
@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        
        subject.name = request.form.get('name')
        subject.description = request.form.get('description')

        try:
            db.session.commit()  
            flash('Subject updated successfully!')
        except :
            db.session.rollback()
            flash('Error')

        return redirect(url_for('admin'))

    return render_template('edit_subject.html', subject=subject)

#route for editing a chapter
@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):    
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')

        try:
            db.session.commit()  
            flash('chapter updated successfully!')
        except :
            db.session.rollback()
            flash('Error')

        return redirect(url_for('admin'))

    return render_template('edit_chapter.html', chapter=chapter)

#route for editing a quiz
@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):    
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        
        quiz.date_of_quiz = datetime.strptime(request.form['date_of_quiz'], "%Y-%m-%d")
        quiz.chapter_id = request.form.get('chapter_id')
        quiz.duration = request.form.get('duration')
        quiz.remarks = request.form.get('remarks')

        try:
            db.session.commit()  
            flash('quiz updated successfully!')
        except :
            db.session.rollback()
            flash('Error')

        return redirect(url_for('adminQuiz'))

    return render_template('edit_quiz.html', quiz=quiz)

#route for editing a question
@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):    
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':        
        
        question.question_title = request.form.get('questionTitle')
        question.question_statement = request.form.get('questionStatement')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = request.form.get('correctOption')
        old_image_path = question.image_path
        old_audio_path = question.audio_path
        
        # Handle image upload
        image = request.files.get('image')
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
            question.image_path = image_filename  # Update with new file
            # Optionally, remove old image
            if old_image_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], old_image_path)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_image_path))
        else:
            # Keep old image if no new image is uploaded
            question.image_path = old_image_path

        # Handle audio upload
        audio = request.files.get('audio')
        if audio and audio.filename != '':
            audio_filename = secure_filename(audio.filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            audio.save(audio_path)
            question.audio_path = audio_filename  # Update with new file
            # Optionally, remove old audio
            if old_audio_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], old_audio_path)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_audio_path))
        else:
            # Keep old audio if no new audio is uploaded
            question.audio_path = old_audio_path

        try:
            db.session.commit()  
            flash('question updated successfully!')
        except :
            db.session.rollback()
            flash('Error')

        return redirect(url_for('adminQuiz'))

    return render_template('edit_question.html', question=question)

#route for navigating to userList tab in admin
@app.route('/userList',methods=['GET','POST'])
def userList():   
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    
    users = User.query.all()
    return render_template('userList.html',users=users)

#route for deleting a user by the admin
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    user = User.query.get_or_404(user_id)    
    try:
        if user:                
            db.session.delete(user)
            db.session.commit()
            flash("user deleted successfully!")
    
    except :
        db.session.rollback()
        flash("Error deleting user")
        
    return redirect(url_for('userList'))

#route for quiz view under admin
@app.route('/view_quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    if 'user' not in session:
        flash("Unauthorized access! Please log in as an user.")
        return redirect(url_for('index')) 
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    quizs = Quiz.query.all() 
    for quiz in quizs:
        quiz.question_count = Question.query.filter_by(quiz_id=quiz.id).count()

    return render_template('view_quiz.html', quiz=quiz, chapter=chapter, subject=subject, quizs=quizs )

#route for user search by admin
@app.route('/user_search',methods=["GET","POST"])
def user_search():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    form = userForm()
    if form.validate_on_submit():
        name = form.name.data
        users = User.query.filter(User.full_name.like(f"%{name}%")).all()
        return render_template('user_search.html', users=users, form=form)
    return render_template('user_search.html', form=form)

#route for question search by admin
@app.route('/question_search',methods=["GET","POST"])
def question_search():
    if 'admin' not in session:
        flash("Unauthorized access! Please log in as an admin.")
        return redirect(url_for('index')) 
    form = questionSearch()
    if form.validate_on_submit():
        question = form.question.data
        questions = Question.query.filter(Question.question_statement.like(f"%{question}%")).all()
        return render_template('question_search.html', questions=questions, form=form)
    return render_template('question_search.html', form=form)

#route for subject search by admin
@app.route('/subject_search',methods=["GET","POST"])
def subject_search():   
    form = subjectForm()
    if form.validate_on_submit():
        name = form.name.data
        subjects = Subject.query.filter(Subject.name.like(f"%{name}%")).all()
        return render_template('subject_search.html', subjects=subjects, form=form)    
    return render_template('subject_search.html',form=form)

#route for quiz search by admin
@app.route('/quiz_search',methods=["GET","POST"])
def quiz_search():
    form = quizForm()
    if form.validate_on_submit():
        id = form.id.data
        quizs = Quiz.query.filter(Quiz.id.like(f"%{id}%")).all()
        return render_template('quiz_search.html', quizs=quizs, form=form)    
    
    return render_template('quiz_search.html',form=form)

#route for quiz start by an user
@app.route('/start_quiz/<int:quiz_id>')
def start_quiz(quiz_id):
    if 'user' not in session:
        flash("Unauthorized access! Please log in as an user.")
        return redirect(url_for('index')) 
    session['quiz_id'] = quiz_id
    session['current_question'] = 0
    session['score'] = 0

    # Fetch the quiz duration from the database
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        duration_parts = list(map(int, quiz.duration.split(":")))  # To convert the HH:MM:SS to list of integers
        quiz_duration = timedelta(hours=duration_parts[0], minutes=duration_parts[1], seconds=duration_parts[2]) # Hours , minutes and seconds individual data is accessed from the list
        
        session['quiz_start_time'] = datetime.utcnow().isoformat()  # Store start time in UTC format in session
        session['quiz_end_time'] = (datetime.utcnow() + quiz_duration).isoformat()  # Store end time in session

    return redirect(url_for('show_question'))

#route for showing questions
@app.route('/show_question', methods=['GET', 'POST'])
def show_question():
    if 'user' not in session:
        flash("Unauthorized access! Please log in as an user.")
        return redirect(url_for('index')) 
    quiz_id = session.get('quiz_id')
    current_question = session.get('current_question', 0)    
    
    # Fetch quiz questions
    questions = Question.query.filter_by(quiz_id=quiz_id).all()    
    if current_question >= len(questions):
        return redirect(url_for('quiz_result'))

    question = questions[current_question]

    if request.method == 'POST':
        action = request.form.get('action')
        selected_option = request.form.get('option')

        if action == 'previous' and current_question > 0:
            session['current_question'] = current_question - 1
            return redirect(url_for('show_question'))
        
        if action == 'next':
            if selected_option and int(selected_option) == question.correct_option:
                session['score'] += 1  # Increment score if correct
            session['current_question'] += 1
            return redirect(url_for('show_question'))
        
        if action == 'submit':
            if selected_option and int(selected_option) == question.correct_option:
                session['score'] += 1
            return redirect(url_for('quiz_result'))    
        
        if action == 'exit':
            return redirect(url_for('user_dashboard'))

    # Calculate remaining time
    quiz_end_time = session.get('quiz_end_time')
    remaining_seconds = 0
    if quiz_end_time:
        quiz_end_time = datetime.fromisoformat(quiz_end_time)  # Converting the stored time from the session
        remaining_seconds = max(0, int((quiz_end_time - datetime.utcnow()).total_seconds()))  # Ensuring no non-negative values

    image_url = None
    audio_url = None

   
    if question.image_path:
        image_url = url_for('static', filename='uploads/' + question.image_path)
        print(f"Image URL: {image_url}")  # Debugging 

    if question.audio_path:
        audio_url = url_for('static', filename='uploads/' + question.audio_path)
        print(f"Audio URL: {audio_url}")

    return render_template(
        'start_quiz.html', 
        question=question, 
        current=current_question+1, 
        total=len(questions),
        remaining_seconds=remaining_seconds, 
        image_url=image_url,
        audio_url=audio_url
    )

#route for displaying quiz_result
@app.route('/quiz_result')
def quiz_result():
    # Retrieve session data
    if 'user' not in session:
        flash("Unauthorized access! Please log in as an user.")
        return redirect(url_for('index')) 
    quiz_id = session.get('quiz_id')
    user_id = session.get('user', {}).get('user_id')
    score = session.get('score', 0)
    total_questions = Question.query.filter_by(quiz_id=quiz_id).count()    

    # Handle zero questions
    if total_questions == 0:
        flash("Quiz already completed ")
        return redirect(url_for('user_dashboard'))

    # Fallback if user_id is None
    if not user_id:
        flash("Session expired. Please log in again.")
        return redirect(url_for('user_dashboard'))

    try:
        # Check if score already exists
        existing_score = Score.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()

        if existing_score:
            # Update the existing score
            existing_score.total_score = score
            existing_score.timestamp = datetime.utcnow()
            
        else:
            # Create a new score entry
            result = Score(
                quiz_id=quiz_id,
                user_id=user_id,
                total_score=score,
                timestamp=datetime.utcnow()
            )
            db.session.add(result)                    
        db.session.commit()        

    except Exception as e:        
        db.session.rollback()        
        flash("An error occurred while saving your score. Please try again.")
        return redirect(url_for('user_dashboard'))
    
    session.pop('quiz_id', None)
    session.pop('current_question', None)
    session.pop('score', None)
    return render_template('quiz_result.html', score=score, total=total_questions)

#route for user scores
@app.route('/user_scores', methods=["GET", "POST"])
def user_scores():
    if 'user' not in session:
        flash("Unauthorized access! Please log in as an user.")
        return redirect(url_for('index')) 
    user_id = session.get('user', {}).get('user_id')    
    scores = Score.query.filter_by(user_id=user_id).all()    
    return render_template('user_scores.html', user_id=user_id, user=session.get('user'), scores=scores)

@app.route('/view_solution/<int:quiz_id>', methods=["GET"])
def view_solution(quiz_id):

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    try:
        return render_template('view_solutions.html', quiz=quiz, questions=questions)
    except Exception as e:
        print (e)
        flash ("Error loading solution. Try again later")
        return redirect(url_for("user_scores"))


#route for searching quiz date
@app.route('/date_search',methods=["GET","POST"])
def date_search():   
    form = dateSearch()
    if form.validate_on_submit():
        date = form.date.data
        quizs = Quiz.query.filter(Quiz.date_of_quiz.like(f"%{date}%")).all()
        return render_template('date_search.html', quizs=quizs, form=form)    
    return render_template('date_search.html',form=form)

#route for searching scores
@app.route('/score_search',methods=["GET","POST"])
def score_search(): 
    if 'user' not in session:
        flash("Unauthorized access! Please log in as an user.")
        return redirect(url_for('index'))   
    form = scoreSearch()
    user_id = session.get('user',{}).get('user_id')    
    
    if form.validate_on_submit():
        score = form.score.data
        scores = Score.query.filter(Score.quiz_id.like(f"%{score}%"),Score.user_id==user_id).all()
        return render_template('score_search.html', scores=scores, form=form)    
    return render_template('score_search.html',form=form)

#route for admin summmary charts
@app.route('/admin_summary',methods=["GET","POST"])
def admin_summary():

    top_scores = db.session.execute(text("""
        SELECT s.name as subject, MAX(sc.total_score) as top_score
        FROM Score sc
        JOIN Quiz q ON sc.quiz_id = q.id
        JOIN Chapter c ON q.chapter_id = c.id
        JOIN Subject s ON c.subject_id = s.id
        GROUP BY s.name
        ORDER BY top_score DESC;
    """)).fetchall()    

    subject_wise_attempts = db.session.execute(text("""
    SELECT s.name as subject, COUNT(sc.user_id) as total_attempts
    FROM Score sc
    JOIN Quiz q ON sc.quiz_id = q.id
    JOIN Chapter c ON q.chapter_id = c.id
    JOIN Subject s ON c.subject_id = s.id
    GROUP BY s.name
    ORDER BY total_attempts DESC;
    """)).fetchall()

    # Convert query result to lists for Chart.js
    subjects = [row[0] for row in top_scores]
    scores = [row[1] for row in top_scores]
    attempts = [row[1] for row in subject_wise_attempts]    
    return render_template('admin_summary.html', subjects=subjects, scores=scores, attempts=attempts)
    
#route for user_summary charts
@app.route('/user_summary',methods=["GET","POST"])
def user_summary():
    user = session.get('user')
    quizzes_given = db.session.execute(text("""
        SELECT s.name as subject, COUNT(DISTINCT q.id) as quiz_count
        FROM Score sc
        JOIN Quiz q ON sc.quiz_id = q.id
        JOIN Chapter c ON q.chapter_id = c.id
        JOIN Subject s ON c.subject_id = s.id
        WHERE sc.user_id = :user_id
        GROUP BY s.name
        ORDER BY quiz_count DESC;
    """), {'user_id': user['user_id']}).fetchall() 

    top_scores = db.session.execute(text("""
        SELECT s.name as subject, MAX(sc.total_score) as top_score
        FROM Score sc
        JOIN Quiz q ON sc.quiz_id = q.id
        JOIN Chapter c ON q.chapter_id = c.id
        JOIN Subject s ON c.subject_id = s.id
        WHERE sc.user_id = :user_id                                         
        GROUP BY s.name
        ORDER BY top_score DESC;
    """),{'user_id': user['user_id']}).fetchall()

    
    subjects = [row[0] for row in quizzes_given]
    quiz_count = [row[1] for row in quizzes_given]    
    scores = [row[1] for row in top_scores] 
    return render_template('user_summary.html',user=user, subjects=subjects, quiz_count=quiz_count, scores=scores)