from flask import Flask
from flask import jsonify
from flask import request
import json
app = Flask(__name__)

###### define ######
#tag
tagteacher_str = '@teacher'

#pkg parameter
pkg_content = 'content'
pkg_time = 'time'
pkg_user = 'user'
pkg_isperiod = 'pkg_isperiod' # 0: not reset , 1: reset 
pkg_question = 'question' # the question which was answered by teacher [question, time, user, solved, ans]
pkg_ans = 'ans' # the answer of the question
pkg_is_play = 'status' # check if the player is playing

#question status
question_unsolved = 0
question_solved = 1

#emotion query
reqular_query = 0
period_query = 1 # reset all emotion records

# error
error_base = 7100
chat_input_error = error_base + 0 # input string is empty
emotion_error = error_base + 1 # the string is not in emotion map
question_index_error = error_base + 2 # the question is not in questions list
player_time_error = error_base + 3 # the question is not in questions list


# statistics
questions = [] # a list consist of students' questions and submitted time [question, time, user, solved, ans]
emotion = [] # a list consist of students' emotion and submitted time [emotion, time, user]

total_students = 0

emotion_map = {
	'tooeasy': 0,
	'notunderstand': 0,
}

#player
is_play = 0 # stop
player_time = 0 # seconds

##### end define #####

##### chat room ######
# student

@app.route("/send_chat", methods=['POST'])
def send_chat():
	# data should be json style

	# content
	string = request.form[pkg_content]
	time = request.form[pkg_time]
	user = request.form[pkg_user]

	# check input
	if string == '':
		return jsonify({'result': 'error', 'error': chat_input_error})

	# find if @teacher exist (-1 means not exist)
	teacher =  string.find(tagteacher_str)

	# check teacher
	if teacher != -1:
		questions.append([string, time, user, question_unsolved, ''])
	
	return jsonify({'result': 'success'})

@app.route("/send_emotion", methods=['POST'])
def send_emotion():
	# data should be json style

	# content
	string = request.form[pkg_content]
	time = request.form[pkg_time]
	user = request.form[pkg_user]

	# check input
	if not string in emotion_map:
		return jsonify({'result': 'error', 'error': emotion_error})

	# add 
	emotion_map[string] += 1
	emotion.append([string, time, user])
		
	return jsonify({'result': 'success'})

@app.route("/get_player_time")
def get_player_time():
	return jsonify({'result': 'success', 'time': player_time, 'status': is_play})

# teacher
@app.route("/reset_emotion")
def reset_emotion(): 
	global emotion

	emotion = []

	for i in emotion_map.keys():
		emotion_map[i] = 0
	
	return jsonify({'result': 'success'})

@app.route("/get_question")
def get_question():
	# get sorted list by solved(3) and time(1)
	# [question, time, user, solved, ans]
	arr = sorted(questions, key=lambda x: (x[3], x[1]))
	return jsonify({'result': 'success', 'data': arr})

@app.route("/solve", methods=['POST'])
def solve():
	# data should be json style

	# content
	string = request.form[pkg_content]
	time = request.form[pkg_time]
	user = request.form[pkg_user]
	ans = request.form[pkg_ans]

	name = []
	name.append(string)
	name.append(time)
	name.append(user)
	name.append(0)
	name.append('')

	# not exist
	if not name in questions:
		return jsonify({'result': 'error', 'error': question_index_error})

	# get id
	getid = questions.index(name)
	
	# set solved and answer
	# [question, time, user, solved, ans]
	questions[getid][3] = 1 
	questions[getid][4] = ans

	return jsonify({'result': 'success'})

@app.route("/get_emotion")
def get_emotion():
	return jsonify({'result': 'success', 'emotion': emotion, 'statistics': emotion_map})

@app.route("/set_player_time", methods=['POST'])
def set_player_time():
	# data should be json style

	# content
	time = request.form[pkg_time]

	# time error
	if time < 0:
		return jsonify({'result': 'error', 'error': player_time_error})

	global player_time
	player_time = time

	return jsonify({'result': 'success'})

@app.route("/player_stop")
def player_stop():
	global is_play
	is_play = 0
	return jsonify({'result': 'success'})

@app.route("/player_start")
def player_start():
	global is_play
	is_play = 1
	return jsonify({'result': 'success'})
##### end chat #####

if __name__ == "__main__":
    app.run()