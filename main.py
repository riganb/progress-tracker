from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from sql import Database
import scraper
import re

app = Flask(__name__)

data_obj = Database('datafile.db')

msg = "No data present yet!"
success_msg = "Item successfully inserted!"
update_msg = "Data successfully updated!"
fail_msg = "Unable to insert item, probable duplication of primary key."
fail_msg_ques_form = "Error! Possible reason: Server data-fetch issue."
del_msg = "Entry successfully deleted!"
del_fail = "Failed to delete entry."
qid_exists = "Question already exists in the database!"

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/css', methods=['GET'])
def bootstrap_css():
    filename = './assets/css/bootstrap.min.css'
    return send_file(filename)

@app.route('/bootstrap-js', methods=['GET'])
def bootstrap_js():
    filename = './assets/js/bootstrap.bundle.bootstrap.bundle.min.js'
    return send_file(filename)

@app.route('/bg', methods=['GET'])
def body_bg():
    filename = './assets/imgs/bg.png'
    return send_file(filename, mimetype='image/png')

@app.route('/carousel-1', methods=['GET'])
def carousel_1():
    filename = './assets/imgs/wall (1).png'
    return send_file(filename, mimetype='image/png')

@app.route('/carousel-2', methods=['GET'])
def carousel_2():
    filename = './assets/imgs/wall (2).png'
    return send_file(filename, mimetype='image/png')

@app.route('/carousel-3', methods=['GET'])
def carousel_3():
    filename = './assets/imgs/wall (3).png'
    return send_file(filename, mimetype='image/png')

@app.route('/users', methods=['GET'])
@app.route('/users/<uid>', methods=['POST'])
def users(uid=None):
	if request.method == 'GET':
		return render_template('users.html', headings=data_obj.get_headings('user'), data=data_obj.get_users(), msg=msg)
	else:
		deletion_success = data_obj.del_user(uid)
		if deletion_success:
			return render_template('users.html', headings=data_obj.get_headings('user'), data=data_obj.get_users(), del_msg=del_msg, msg=msg)
		else:
			return render_template('users.html', headings=data_obj.get_headings('user'), data=data_obj.get_users(), fail_msg=fail_msg, msg=msg)

@app.route('/questions/', methods=['GET'])
@app.route('/questions/<qid>', methods=['POST'])
def questions(qid=None):
	if request.method == 'GET':
		return render_template('questions.html', headings=data_obj.get_headings('question'), data=data_obj.get_questions(), msg=msg)
	else:
		deletion_success = data_obj.del_question(qid)
		if deletion_success:
			return render_template('questions.html', headings=data_obj.get_headings('question'), data=data_obj.get_questions(), del_msg=del_msg)
		else:
			return render_template('questions.html', headings=data_obj.get_headings('question'), data=data_obj.get_questions(), fail_msg=fail_msg)

@app.route('/attempts', methods=['GET', 'POST'])
def attempts():
	if request.method == 'GET':
		return render_template('attempts.html', headings=data_obj.get_headings('attempt'), data=data_obj.get_attempts(), msg=msg)
	else:
		uid, qid = request.form['uid'], request.form['qid']
		deletion_success = data_obj.del_attempt(uid, qid)
		if deletion_success:
			return render_template('attempts.html', headings=data_obj.get_headings('attempt'), data=data_obj.get_attempts(), del_msg=del_msg, msg=msg)
		else:
			return render_template('attempts.html', headings=data_obj.get_headings('attempt'), data=data_obj.get_attempts(), fail_msg=fail_msg, msg=msg)

@app.route('/platforms', methods=['GET'])
def platforms():
	return render_template('platforms.html', headings=data_obj.get_headings('platform'), data=data_obj.get_platforms(), msg=msg)

@app.route('/stats', methods=['GET'])
def total_scores():
	return render_template('stats.html', headings=data_obj.get_headings('stats'), data=data_obj.get_stats(), msg=msg)

@app.route('/create-user', methods=['GET', 'POST'])
def add_user():
	if request.method == 'POST':
		uid, uname, age, desg, email = request.form['uid'], request.form['uname'], request.form['age'], request.form['desg'], request.form['mail']
		if email != "":
			if not valid_email(email):
				return render_template('wrongMail.html')
		insert_success = data_obj.insert_user({'uid': uid, 'uname': uname, 'age': age, 'desg': desg, 'mail': email})
		if insert_success:
			return render_template('userForm.html', msg=success_msg.replace('Item', 'User'))
		else:
			return render_template('userForm.html', fail_msg=fail_msg)
	else:
		return render_template('userForm.html')

@app.route('/insert-question', methods=['GET', 'POST'])
def add_question():
	if request.method == 'POST':
		qlink = request.form['qlink']
		qdata = scraper.question_details(qlink)
		insert_success = data_obj.insert_question(qdata)
		if insert_success:
			return render_template('questions.html', headings=data_obj.get_headings('question'), data=data_obj.get_questions(), del_msg=success_msg, msg=msg)
		else:
			return render_template('questions.html', headings=data_obj.get_headings('question'), data=data_obj.get_questions(), del_fail=fail_msg_ques_form, msg=msg)
	else:
		qlink = request.args.get('qlink')
		qdata = scraper.question_details(qlink)
		if isinstance(qdata, dict):
			if data_obj.question_exists(qdata['qid']):
				return render_template('questions.html', headings=data_obj.get_headings('question'), data=data_obj.get_questions(), msg=msg, warning=qid_exists)
			return render_template('quesForm.html', qdata=qdata)
		else:
			return render_template('questions.html', headings=data_obj.get_headings('question'), data=data_obj.get_questions(), msg=msg, del_fail=qdata)

@app.route('/add-attempt', methods=['GET', 'POST'])
@app.route('/update-attempt', methods=['POST'])
def alter_attempt():
	if request.method == 'POST':
		uid, qid, solved = request.form['uid'], request.form['qid'], request.form['solved']
		insert_success = data_obj.insert_or_update_attempt({'uid': uid, 'qid': qid, 'solved': solved})
		temp_msg = update_msg if request.path == '/update-attempt' else success_msg
		if insert_success:
			return render_template('attempts.html', headings=data_obj.get_headings('attempt'), data=data_obj.get_attempts(), del_msg=temp_msg, msg=msg)
		else:
			return render_template('attForm.html', data=data_obj.get_attempts())
	else:
		return render_template('attForm.html', users=data_obj.get_users(), questions=data_obj.get_questions())

def valid_email(email):
	return re.match("[a-zA-Z0-9_\-.]+?@.+?\..+?", email) != None

@app.errorhandler(404)
def notfound(e):
    return render_template('404.html')

app.run(host='0.0.0.0', debug=True)

