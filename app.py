import datetime
import os
import uuid

from datetime import timedelta
from common.database import Database
from models.student_data import Students
from models.admin import Admin
# from src.models.user import User
from flask import Flask, render_template, request, session, make_response, send_from_directory, url_for
from werkzeug.utils import redirect

__author__ = "abhishekmadhu"
app = Flask(__name__)  # '__main__'
app.secret_key = "abhi"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/')  # www.myweb.com/api/login
def home_template():
    return render_template('home.html')


# @app.route('/login')  # www.myweb.com/api/login
# def login_template():
#     return render_template('scratchpad.html')
#     # return "Hello World"


@app.route('/register')  # www.myweb.com/api/register
def register_template():
    return render_template('register.html')


# initialize the database b4 any request, only once per session
@app.before_first_request
def initialize_database():
    Database.initialize()  # remove this after clearing the session


@app.route('/auth/login', methods=['POST'])
def login_user():                               # Refactoring DONE
    app.permanent_session_lifetime = timedelta(minutes=1)
    email = request.form['email']
    password = request.form['password']

    if Students.is_login_valid(email, password):        #is True
        Students.login(email)
        session['email'] = email
    else:
        session['email'] = "no email"
        return "INVALID USER, PLEASE CHECK YOUR CREDENTIALS, OR REGISTER (if you have not yet)"

    student = Students.from_mongo_by_email(email=email)

    id = student._id
    print(id)

    filename = id + ".jpg"
    print(filename)

    return render_template("student_data.html", email=session['email'], student=student, image_name=filename)
    # return session['email']


@app.route('/auth/register', methods=['POST'])      # Refactoring DONE
def register_user():
    email = request.form['email']
    password = request.form['password']
    institute = request.form['institute']
    guardian_name = request.form['guardian_name']
    student_name = request.form['student_name']
    course = request.form['course']
    created_date = datetime.datetime.utcnow()
    dos = request.form['dos']
    address = request.form['address']
    mobile = request.form['contact_number']
    branch = request.form['branch']
    remarks = request.form['remarks']
    semester = request.form['semester']
    year = request.form['year']
    reason = "N/A"
    approval_status = "Pending"
    _id = uuid.uuid4().hex

    reg_num = Database.count(collection='students', query={}) + 1

    registration_no = "RNC/2019/Intern/Batch1/" + (10000 + reg_num).__str__()
    print(registration_no)

    a = Students.register(email=email, password=password, institute=institute, guardian_name=guardian_name,
                          student_name=student_name, created_date=created_date, dos=dos,
                          address=address, mobile=mobile, branch=branch, remarks=remarks,
                          semester=semester, year=year,
                          approval_status=approval_status,
                          reason=reason,
                          registration_no=registration_no,
                          _id=_id, course=course)

    # ######### remove block if does not work
    # also return render_template("profile.html", email=session['email'])
    # ##########################################
    student = Students.from_mongo_by_email(session['email'])

    if a == 1:
        return render_template('upload.html', email=session['email'], student=student)
    elif a == 0:
        return "You are already registered, please log in"
    elif a == 100:
        return "Server is unresponsive, contact (+91)7063375758 immediately."


@app.route('/my_details/<string:_id>', methods=['GET'])  # ######################
def show_details_for_new_students(_id):
    student = Students.from_mongo_by_id(_id=_id)

    return render_template('student_data.html', email=session['email'], student=student)


# ####################################  routes for the admin

@app.route('/admin/login')
def admin_login_page():
    return render_template('admin_login_page.html')


@app.route('/admin/auth/login', methods=['POST'])
def login_admin(): # renders the overview page
    email = request.form['email']
    password = request.form['password']

    if Admin.is_login_valid(email, password):  # is True
        Admin.login(email)
        session['email'] = email
    else:
        session['email'] = "no email"
        return "ADMIN NOT FOUND, PLEASE CHECK YOUR CREDENTIALS, OR CONTACT SERVER ADMINISTRATOR"

    # collection = 'students'
    students = Database.find(collection='students', query={})
    # return "HELLO"
    return render_template("overview_page.html", email=session['email'], students=students)
    # return session['email']


# filter functions
# #########################################################
@app.route('/admin/auth/login/pending', methods=['GET'])
def overview_pending():

    # collection = 'students'
    students = Database.find(collection='students',
                             query={'approval_status': 'Pending'})
    # return "HELLO"
    return render_template("overview_page.html", email=session['email'], students=students)
    # return session['email']


@app.route('/admin/auth/login/approved', methods=['GET'])
def overview_approved():

    # collection = 'students'
    students = Database.find(collection='students',
                             query={'approval_status': 'Approved'})
    # return "HELLO"
    return render_template("overview_page.html", email=session['email'], students=students)
    # return session['email']


@app.route('/admin/auth/login/all', methods=['GET'])
def overview_all():

    # collection = 'students'
    students = Database.find(collection='students',
                             query={})
    # return "HELLO"
    return render_template("overview_page.html", email=session['email'], students=students)
    # return session['email']


@app.route('/student_details/<string:_id>', methods=['GET'])  # ########################
def show_details_for_student(_id):
    student = Students.from_mongo_by_id(_id=_id)
    filename = _id + ".jpg"

    return render_template('data_for_registered_candidates.html',
                           email=session['email'], student=student,
                           image_name=filename)


# ###############################################################
@app.route('/admin/overview/details/approval/<string:_id>', methods=['POST', 'GET'])
def approve_candidate_status(_id):
    Database.update_status_to_selected_by_id(collection='students', _id=_id)
    student = Students.from_mongo_by_id(_id=_id)
    filename = _id + ".jpg"
    return render_template('data_for_registered_candidates.html', email=session['email'], student=student,
                           image_name=filename)


@app.route('/admin/overview/details/rejection/<string:_id>', methods=['POST', 'GET'])
def reject_candidate_status(_id):
    reason = request.form['reason']

    Database.update_status_to_rejected_by_id(reason=reason,collection='students', _id=_id)
    student = Students.from_mongo_by_id(_id=_id)
    filename = _id + ".jpg"
    return render_template('data_for_registered_candidates.html', email=session['email'], student=student,
                           image_name=filename)


# ###############################################################
# route to add images via the web page
#   This route takes the image, and puts it in a
#   folder named /images in the src/
#   This can be latter used to render the picture of the candidate
#   in a web form, if the order is maintained
#       ie: if all images are stored with the id of the candidate.
@app.route('/register/add-image')
def add_image():
    return render_template('upload.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    # print(target)

    email = session['email']
    student = Students.from_mongo_by_email(email=email)
    id = student._id
    # print(id)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        # print(file)
        filename = id + ".jpg"
        destination = "/".join([target, filename])
        # print(destination)
        file.save(destination)
    return render_template("student_data.html", student=student, image_name=filename)


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


@app.route('/scratchpad')
def show_scratchpad():
    return  render_template("scratchpad.html")

@app.route('/logout')
def logout():
    session['email'] = None
    session.clear()
    # browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.w)
    return redirect(url_for('home_template'))


# running the app if it is called by itself
if __name__ == "__main__":
    app.run(debug=True)
