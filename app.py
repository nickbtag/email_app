''' For checking emails '''
from dataclasses import field
from distutils.log import debug
from operator import is_
from validate_email import validate_email
from flask import Flask, render_template, request
import csv
import pandas as pd
import os
import smtplib
from email import message
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = Flask(__name__)

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
        name_of_file = str(file.filename)
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
        

        table_data = pd.read_csv(file.filename)
                
        return render_template('dataMultipleEmails.html', data=data, columns=list_of_column_names,good_emails=good_emails, bad_emails=bad_emails, csv_file=file, tables=[table_data.to_html()],titles=[''])

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


@app.route('/sendEmail',methods=['GET','POST'])
def data4():
    global name_of_file
    if request.method == 'POST':
        sender_address = request.form['sender']
        from_address = 'battaglia@cua.edu'
        subject = 'CSV Email List'
        content = 'Thank you for using my application, enjoy your valid email list!'
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = sender_address
        msg['Subject'] = subject
        body = MIMEText(content, 'plain')
        msg.attach(body)
        with open(name_of_file, 'r') as f:
            attachment = MIMEApplication(f.read(), Name=basename(name_of_file))
            attachment['Content-Disposition'] = 'attachment: filename="{}"'.format(basename(name_of_file))
        msg.attach(attachment)

        server = smtplib.SMTP('smtp-relay.sendinblue.com', 587)
        server.login(from_address, 'rSMfysqbap4Cv9Xh')
        server.send_message(msg, from_addr=from_address, to_addrs=[sender_address])

        return render_template('emailSent.html',sender=sender_address)


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
    
