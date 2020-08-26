from flask import Flask, render_template, request, redirect, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashlib import sha256
import requests
import json

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
    res = db.session.query(sessions_t).filter_by(
        login=login, session=session).first()
    if res == None:
        return 0
    if int(res.time) + 12 * 3600 < time:
        block_session(session)
        return 0
    if res.blocked:
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
    today = ''
    counter = 2
    try:
        time = json.loads(data.timetable)[date]
    except:
        time = {}
    for i in time.keys():
    	if len(time[i]) == 2:
	        patient = db.session.query(patients_t).filter_by(
	            login=time[i][0]).first()
	        if patient != None:
	            patient_name = patient.surname + ' ' + patient.name
	            today += f'<a href="/patient?login={time[i][0]}&work={time[i][1]}"><button title="{time[i][1]}" class="btn btn-success btn-lg" type="button" style="opacity: 0.90;position: absolute;margin-top: {counter}3%;font-family: Ubuntu, sans-serif;font-size: 43px;margin-left: 6%;">{i} | <i>{patient_name}</i></button></a>'
	            counter += 1
    if counter == 2:
        today += '<button class="btn btn-success btn-lg" type="button" style="opacity: 0.90;position: absolute;margin-top: 23%;font-family: Ubuntu, sans-serif;font-size: 43px;margin-left: 6%;">Нет пациентов, расписания.</button>'
    return render_template('today.html', date=date, name=name, today=today)


@app.route("/patient", methods=['GET', 'POST'])
def patient():
    if request.method == 'GET':
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
        login = request.args.get('login')
        patient = db.session.query(patients_t).filter_by(login=login).first()
        return render_template('patient.html', login=login, work=request.args.get('work'), surname=patient.surname, name=patient.name + ' ' + patient.middle_name, cab=patient.cab, status=patient.status, sex=patient.sex, dr=patient.dr)
    else:
        login = request.args.get('login')
        for i in list(request.cookies):
            if check_session(i, request.cookies.get(i)):
	            data = db.session.query(doctors_t).filter_by(login=i).first()
	            if data == None:
	                block_session(request.cookies.get(i))
	            else:
	                doctor = data.login
	                timetable = json.loads(data.timetable)
	                break
            else:
                block_session(request.cookies.get(i))
        else:
            return redirect('/login')

        info = requests.get(
        'https://api.vk.com/method/utils.getServerTime?access_token=fb50e915fb50e915fb50e91553fb23a159ffb50fb50e915a474b724a592ee5ec0b5b399&v=5.122').json()
        time = datetime.utcfromtimestamp(info['response']).strftime('%d.%m.%Y')
        time_t = timetable[time]
        for i in time_t.keys():
            if time_t[i][0] == int(login):
                data = time_t[i]
                if int(request.form['patient']):
                    data.append('Пришел')
                    data.append(time)
                    break
                else:
                    data.append('Не пришел')
                    data.append(time)
                    break

        db.session.query(doctors_t).filter_by(login=doctor).update({'timetable': json.dumps(timetable)})
        db.session.commit()
        history = json.loads(db.session.query(patients_t).filter_by(login=login).first().history)
        history.append(data)
        db.session.query(patients_t).filter_by(login=login).update({'history': json.dumps(history)})
        db.session.commit()
        return redirect('today')


@app.route("/allergy", methods=['GET', 'POST'])
def allergy():
    if request.method == 'GET':
        for i in list(request.cookies):
            if check_session(i, request.cookies.get(i)):
                break
            else:
                block_session(request.cookies.get(i))
        else:
            return redirect('/login')
        login = request.args.get('login')
        patient = db.session.query(patients_t).filter_by(login=login).first()

        other = ''
        counter = 1
        if patient.products != '[]':
            for i in json.loads(patient.products):
                other += f'<h1 class="text-justify" style="position: absolute;color: rgb(255,255,255);font-family: Ubuntu, sans-serif;margin-top: 5%;padding-top: {counter}%;">{i}</h1>'
                counter += 5
        else:
            other = '<h1 class="text-justify" style="position: absolute;color: rgb(255,255,255);font-family: Ubuntu, sans-serif;margin-top: 5%;padding-top: 1%;">Нет</h1>'

        medications = ''
        counter = 1
        if patient.medications != '[]':
            for i in json.loads(patient.medications):
                medications += f'<h1 class="text-justify" style="position: absolute;color: rgb(255,255,255);font-family: Ubuntu, sans-serif;margin-top: 5%;padding-top: {counter}%;">{i}</h1>'
                counter += 5
        else:
            medications = '<h1 class="text-justify" style="position: absolute;color: rgb(255,255,255);font-family: Ubuntu, sans-serif;margin-top: 5%;padding-top: 1%;">Нет</h1>'

        return render_template('allergy.html', other=other, medications=medications, login=login)
    else:
        login = request.args.get('login')
        patient = db.session.query(patients_t).filter_by(login=login).first()
        if request.form['name'] != '':
            if request.form['allergy_type'] == 'med':
                data = json.loads(patient.medications)
                data.append(request.form['name'])
                data = json.dumps(data)
                db.session.query(patients_t).filter_by(login=login).update({'medications': data})
                db.session.commit()
            else:
                data = json.loads(patient.products)
                data.append(request.form['name'])
                data = json.dumps(data)
                db.session.query(patients_t).filter_by(login=login).update({'products': data})
                db.session.commit()
            return redirect(f'/allergy?login={login}')


@app.route("/documents")
def documents():
    for i in list(request.cookies):
        if check_session(i, request.cookies.get(i)):
            break
        else:
            block_session(request.cookies.get(i))
    else:
        return redirect('/login')
    login = request.args.get('login')
    patient = db.session.query(patients_t).filter_by(login=login).first()
    table = ''
    for i in json.loads(patient.docs):
	    table += f'''<tr>
	                <td style="background-color: #7fe68f;"><a href="{url_for('static', filename='docs/' + i["name"])}"><i class="fa fa-eye" style="font-size: 48px;"></i></a></td>
	                <td>{i["name"]}</td>
	                <td>{i["type"]}</td>
	                <td>{i["author"]}</td>
	                <td>{i["time"]}</td>
	            </tr>'''
    return render_template('documents.html', name=patient.surname + ' ' + patient.name, table=table, login=login)

@app.route("/upload_document", methods=['GET', 'POST'])
def upload_document():
    if request.method == 'GET':
        for i in list(request.cookies):
            if check_session(i, request.cookies.get(i)):
                break
            else:
                block_session(request.cookies.get(i))
        else:
            return redirect('/login')

        return render_template('upload_document.html')
    else:
        for i in list(request.cookies):
            if check_session(i, request.cookies.get(i)):
                data = db.session.query(doctors_t).filter_by(login=i).first()
                if data == None:
                    block_session(request.cookies.get(i))
                else:
                    author = data.surname +  ' ' + data.name + ' ' + data.middle_name
                    break
            else:
                block_session(request.cookies.get(i))
        else:
            return redirect('/login')


        ast = open('static/docs/' + request.files['file'].filename, 'wb')
        ast.write(request.files['file'].read())
        ast.close()


        info = requests.get(
        'https://api.vk.com/method/utils.getServerTime?access_token=fb50e915fb50e915fb50e91553fb23a159ffb50fb50e915a474b724a592ee5ec0b5b399&v=5.122').json()
        time = datetime.utcfromtimestamp(info['response']).strftime('%d.%m.%Y %H:%M')
        name = request.files['file'].filename
        typ = request.form['type']

        login = request.args.get('login')
        patient = db.session.query(patients_t).filter_by(login=login).first()

        docs = json.loads(patient.docs)
        docs.append({"name": name, "type": typ, "author": author, "time": time})
        db.session.query(patients_t).filter_by(login=login).update({'docs': json.dumps(docs)})
        db.session.commit()
        return redirect('/documents?login=' + login)


@app.route("/history")
def history():
    for i in list(request.cookies):
        if check_session(i, request.cookies.get(i)):
            break
        else:
            block_session(request.cookies.get(i))
    else:
        return redirect('/login')
    login = request.args.get('login')
    patient = db.session.query(patients_t).filter_by(login=login).first()
    table = ''
    for i in json.loads(patient.history):
        doctor = db.session.query(patients_t).filter_by(login=login).first()
        if i[2] == 'Пришел':
            table += f'''<tr>
                    <td>{i[1]}</td>
                    <td>{doctor.surname + ' ' + doctor.name + ' ' + doctor.middle_name}</td>
                    <td>{i[-1]}</td>
                    <td style="background-color: #a6ff7c;">Пришел</td>
                </tr>'''
        elif i[2] == 'Не пришел':
            table += f'''<tr>
                    <td>{i[1]}</td>
                    <td>{doctor.surname + ' ' + doctor.name + ' ' + doctor.middle_name}</td>
                    <td>{i[-1]}</td>
                    <td style="background-color: #ff7c7c;">Не пришел</td>
                </tr>'''
        else:
            table += f'''<tr>
                    <td>{i[1]}</td>
                    <td>{doctor.surname + ' ' + doctor.name + ' ' + doctor.middle_name}</td>
                    <td>{i[-1]}</td>
                    <td style="background-color: #7c91ff;">Зарегестрирован</td>
                </tr>'''
    return render_template('history.html', name=patient.surname + ' ' + patient.name, table=table, login=login)

app.run()
