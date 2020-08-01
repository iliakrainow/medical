from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashlib import sha256
import requests

import db.models.sessions as sessions
import db.models.patients as patients
import db.models.doctors as doctors
import db.models.logins as logins


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/base.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
sessions_t = sessions.config(db)
patients_t = patients.config(db)
doctors_t = doctors.config(db)
logins_t = logins.config(db)

db.create_all()


def create_session(login, password):
    time = requests.get(
        'https://api.vk.com/method/utils.getServerTime?access_token=fb50e915fb50e915fb50e91553fb23a159ffb50fb50e915a474b724a592ee5ec0b5b399&v=5.122').json()['response']
    pre = password + str(time)
    res = sha256(pre.encode('utf-8')).hexdigest()
    s = sessions_t(login, res, str(time), 0)
    db.session.add(s)
    db.session.commit()
    return res


def check_session(login, session):
    time = requests.get(
        'https://api.vk.com/method/utils.getServerTime?access_token=fb50e915fb50e915fb50e91553fb23a159ffb50fb50e915a474b724a592ee5ec0b5b399&v=5.122').json()['response']
    res = db.session.query(sessions_t).filter_by(login=login, session=session).first()
    if res == None:
        return 0
    if int(res.time) + 12 * 3600 < time:
    	block_session(session)
    	return 0
    return 1


def block_session(session):
    try:
        db.session.query(sessions_t).filter_by(
            session=session).update({'blocked': 1})
        db.session.commit()
    except:
        pass


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        for i in list(request.cookies):
            block_session(request.cookies.get(i))
        return render_template('login.html')
    else:
        result = db.session.query(logins_t).filter_by(
            login=str(request.form['login'])).first()
        if sha256(request.form['password'].encode('utf-8')).hexdigest() == result.hashed_password:
            res = make_response(redirect('/today'))
            res.set_cookie(result.login, create_session(
                result.login, result.hashed_password), max_age=12 * 3600)
            return res
        else:
            return redirect('/login')


@app.route("/today")
def today():
    for i in list(request.cookies):
        if check_session(i, request.cookies.get(i)):
            data = db.session.query(doctors_t).filter_by(login=i).first()
            if data == None:
            	block_session(request.cookies.get(i))
            else:
	            name = data.name + ' ' + data.middle_name
	            break
        else:
            block_session(request.cookies.get(i))
    else:
        return redirect('/login')
    info = requests.get(
        'https://api.vk.com/method/utils.getServerTime?access_token=fb50e915fb50e915fb50e91553fb23a159ffb50fb50e915a474b724a592ee5ec0b5b399&v=5.122').json()
    date = datetime.utcfromtimestamp(info['response']).strftime('%d.%m.%Y')
    return render_template('today.html', date=date, name=name)

app.run()
