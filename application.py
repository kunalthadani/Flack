import os

from flask import Flask,render_template,redirect,request,session,jsonify
from flask_session import Session
from time import strftime
from datetime import datetime

from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app,debug = True)

class Message:
	def __init__(self,msg,sender,time):
		self.msg =  msg
		self.sender = sender
		self.time = time

class Channel:
	def __init__(self,name):
		self.name = name
		self.msglist = list()
		self.count = 0

users = list()
channels = list()
channels_data = dict()


@app.route("/login",methods = ['GET','POST'])
def login():
	if request.method == 'POST':
		name = request.form.get("user")
		if name in users:
			return render_template('login.html', message = "Display Name already taken")
		session['user'] = name
		users.append(name)
		print(users)
		print(f"Tried logging in {session['user']}")
		return redirect("/")
	else:
		return render_template("login.html", message = "")

@app.route("/")
def index():
	# if session.get('user') is None:
	# 	return redirect("/login")
	# else:
	return render_template("channel.html",channels = channels,users = users)

@app.route('/channel_data',methods = ['POST'])
def channel_data():
	channel_name = request.form.get('channel')
	current_channel = channels_data[channel_name]
	current_msglist = list()
	for msg in current_channel.msglist:
		current_message = {"msg":msg.msg,"disp_name":msg.sender,"time":msg.time}
		current_msglist.append(current_message)
	return jsonify({"msg":current_msglist,"channel":channel_name})


@app.route("/channel_add" , methods = ['POST'])
def add_channel():
	channel = request.form.get('name')
	channels.append(channel)
	new_channel = Channel(channel)
	channels_data[channel] = new_channel
	print(channels_data[channel].name)
	return render_template('/')
	# return jsonify({'channel':channel})

@socketio.on("send message")
def sendmsg(data):
	channel_object = channels_data[data['channel']]
	new_message = data['msg']
	new_channel_name = data['channel']
	new_name = data['disp_name']
	time = datetime.now().strftime('%d %b %H:%M')

	new_msg = Message(new_message,new_name,time)
	if channel_object.count > 99:
		for i in range(99):
			channel_object.msglist[i] = channel_object.msglist[i+1]
		channel_object.msglist[99] = new_msg
	else:
		channel_object.msglist.append(new_msg)
	emit("receive message",{'msg':data['msg'],'channel':data['channel'],'disp_name':data['disp_name'],'time':time},broadcast = True)

@socketio.on("add channel")
def add(data):
	success = False 
	if data['name'] not in channels:	
		channels.append(data['name'])
		new_channel = Channel(data['name'])
		channels_data[data['name']] = new_channel
		success = True
	# print(channels_data[data.name].name)
	emit("put channel",{'success':success, 'name':data['name']},broadcast=True)

# PING
@socketio.on("ping user")
def ping(data):
	sender = session['user']
	emit("send ping",{'sender':sender,'receiver' : data['receiver']},broadcast = True)

@app.route("/logout")
def logout():
	session.clear()
	return redirect('/')