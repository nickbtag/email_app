''' For checking emails '''
from dataclasses import field
from distutils.log import debug
from operator import is_
from validate_email import validate_email
from flask import Flask, render_template, request, send_file
import csv
import pandas as pd
import os
import smtplib
from email import message
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import urllib.request
import socket
import re
import dns.resolver

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'nicks-secret'
#app.config['DATABASE_URL'] = 'postgres://duvsvrrssismzi:792e6507bf8b234745da05aa5d52fac4e7c5f3c52c88882aed350b219db916b9@ec2-54-147-33-38.compute-1.amazonaws.com:5432/ddd97qvhel1m78'
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#db = SQLAlchemy(app)

#class User(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(120), index=True, unique=True)
#    csv_file = db.Column(db.String(150))

@app.route('/', methods=['GET','POST'])
def index():
    global file, name_of_file
    return render_template('index.html')

@app.route('/datamultipleemails',methods=['GET','POST'])
def data():
    global file, name_of_file
    data = []
    if request.method == 'POST':
        file = request.files['upload-file']
        #rs_username = request.form['username']
        # must create a username input from index.html
        name_of_file = secure_filename(file.filename)
        file.save(file.filename)
        with open(file.filename) as f:
            print(f)
            for i in csv.DictReader(f):
                data.append(i)

            dict_from_csv = list(data)[0]
            list_of_column_names = list(dict_from_csv.keys())
            list_of_column_names.append('Valid')

        i = 0
        while i < len(data):
            #valid = False
            #addressToVerify = data[i]['Email']
            #match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)

            #if match == None:
            #    print('Bad Syntax')
            #    valid = False
            #else:
            #    valid = True

            #records = dns.resolver.query(addressToVerify.split("@",1)[1], 'MX')
            #mxRecord = records[0].exchange
            #mxRecord = str(mxRecord)

            # Get local server hostname
            #host = socket.gethostname()
            
            # SMTP lib setup (use debug level for full output)
            #server = smtplib.SMTP()
            #server.set_debuglevel(0)
            
            # SMTP Conversation
            #server.connect(mxRecord)
            #server.helo(host)
            #server.mail('me@domain.com')
            #code, message = server.rcpt(str(addressToVerify))
            #server.quit()
            
            # Assume 250 as Success
            #if code == 250:
            #    data[i]['Valid'] = "YES"
            #    i += 1
            #else:
            #    data[i]['Valid'] = "NO"
            #    i += 1
             
            is_valid = validate_email(data[i]['Email'],verify=True)
            if is_valid:
                data[i]['Valid'] = "YES"
                i += 1
            else:
                data[i]['Valid'] = "NO"
                i += 1
        
        i = 0
        good_emails = []
        bad_emails = []
        while i < len(data):
            if data[i]['Valid'] == "YES":
                good_emails.append(data[i]['Email'])
                i += 1
            else:
                bad_emails.append(data[i]['Email'])
                i += 1
        
        with open(file.filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = list_of_column_names)
            writer.writeheader()
            writer.writerows(data)
        
        #newFile = User(csv_file=file.filename, username=rs_username)
        #db.session.add(newFile)
        #db.session.commit()

        table_data = pd.read_csv(file.filename)
                
        return render_template('dataMultipleEmails.html', data=data, columns=list_of_column_names,good_emails=good_emails, bad_emails=bad_emails, csv_file=file, tables=[table_data.to_html()],titles=[''], name_of_file=name_of_file)

@app.route('/dataoneemail',methods=['GET','POST'])
def data2():
    global file
    if request.method == 'POST':
        email = request.form['email']
        
        is_valid = validate_email(email,verify=True)
        if is_valid:
            data = "YES! {} is a valid email.".format(email)
        else:
            data = "NO:( {} is NOT a valid email. Keep Searching...".format(email)

        return render_template('dataOneEmail.html', data=data)


@app.route('/download',methods=['GET','POST'])
def data4():
    global name_of_file
    if request.method == 'POST':
       
        return send_file(name_of_file, as_attachment=True), render_template('download.html')


@app.route('/clearEmail',methods=['GET','POST'])
def data3():
    global file
    data = []
    list_of_column_names = []
    if request.method == 'POST':
        
        with open(name_of_file) as f:
            for i in csv.DictReader(f):
                data.append(i)       
        dict_from_csv = list(data)[0]
        list_of_column_names = list(dict_from_csv.keys())
        
        i = 0
        while i < len(data):
            if data[i]['Valid'] == "YES":
                i += 1
            else:
                data[i]['Email'] = ""
                i += 1
        
        list_of_column_names.remove('Valid')
        i = 0
        while i < len(data):
            data[i].pop('Valid')
            i += 1
            
        with open(name_of_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = list_of_column_names)
            writer.writeheader()
            writer.writerows(data)
            

        
        table_data = pd.read_csv(name_of_file)


        return render_template('cleared.html', data=data, tables=[table_data.to_html()],titles=[''])


if __name__ == '__main__':
    app.run(debug=True)
    
