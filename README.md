# Quiz master app

## Overview

The Quiz master app is a multi-user web application designed to facilitate the users with quizzes which helps them in their exam preparation process. The project is built with html css and bootstrap for front-end, flask for back end and sqlite for database.

## Technologies Used
- **Backend:** Flask, SQLAlchemy
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite
- **Libraries:** Flask-WTF for form handling, Jinja2 for templating

## Installation
1. Create a virtual environment:
   - python -m venv venv
   - source venv/bin/activate (On Windows use `venv\Scripts\activate`)
2. Install the required packages:
   - install all the dependencies(example: python -m pip install flask)   
3. Run the application
   - flask run (python app.py)

   ## Architecture and Features
## Architecture 
The whole project is inside the ‘MAD_1’ folder. Following is the flask app structure. 
1. The “model.py” containing the database schema related definitions. 
2. Templates folder is used to serve the html files. 
3. Static folder contains the .jpg images files for background.
4. The “Instance” folder has the database defined. 
5. The ‘application’ folder acts as the core package where the main logic is implemented.
6. The ‘__init__.py’ file initializes the Flask application and connects it to the database.
7. The ‘forms.py’ file defines Flask-WTF forms for implementing search feature.
8. The ‘routes.py’ file contains the controller logic. Manages user authentication, quiz flow, admin functionalities, and more.

## Features
1. User signup and login with validation (Signup only works if username doesn’t already exist, returns alert if already exists)
2. Admin can manage subjects, chapters, quizzes, questions and manages the registered users.
3. The operations admin can perform are add, delete, edit.
3. Users can register and login to the user dashboard and can attempt any quiz of their choice.
4. Summary charts are included to check the performance of the users and the admin.
5. Search feature is implemented for admin and users.
6. Timer is included with the quiz for real time exam experience.
7. Users can check their previous score of the attempted quizzes.
8. Users can check the solutions of the attempted quizzes
9. Admin can add images and audio to the questions
