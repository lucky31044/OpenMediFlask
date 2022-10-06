from flask import Flask,request,url_for,redirect,Response
from message import *
import sys, os
from google_ocr import *
from sqldb import *
from datetime import date
from google.cloud.sql.connector import Connector
import sqlalchemy
import json
from flask_cors import CORS

today = date.today()

app = Flask(__name__)
CORS(app)


class variables:
    emoji = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
    counter={}
    track = {}
    type = ''
    incoming_msg = {}
    name = {}
    user_dict = {}

os.environ['TWILIO_ACCOUNT_SID'] = "AC008781540ee7f99dc47e41bc3ab20448"
os.environ['TWILIO_AUTH_TOKEN'] = "5eb2b6e4d20cf3f14f0f3816f0ece6cd"
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="hacker-earth-ocr-3a73e2c36b99.json"
# initialize Connector object
connector = Connector()

# function to return the database connection object
def getconn():
    conn = connector.connect(
        'hacker-earth-ocr:us-central1:googlehack',
        "pymysql",
        user='openmediuser',
        password='root',
        db='Open_Medi1'
    )
    return conn

# create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)


@app.route('/whatsapp', methods=['POST','GET'])
def main():

    if request.method == 'GET':
        return 'Hiii'

    try:
        print('Got Json')
        incoming_json = request.get_json()
        text = ''
        pic_url = ''
        print(request.values)

        sender = request.values.get('From')
        phone_id = sender[12:]
        print(phone_id)
        variables.incoming_msg[phone_id] = request.values.get('Body').lower().strip()

        print('##############')
        print(variables.incoming_msg[phone_id])

        if variables.incoming_msg[phone_id] in ['hello','hi','hey','menu','hii']:
            print('----------In Hello---------')
            variables.counter[phone_id] = 0
            variables.track[phone_id] = {}
            variables.track[phone_id]['NLP'] = False
            variables.counter[phone_id] = variables.counter[phone_id] + 1

            # Check user type 
            print(phone_id)
            user_type = fetchusertype(phone_id)

            variables.track[phone_id]['user_type'] = user_type

            if user_type == 'Doctor':
                msg = "Hello Welcome to *OpenMedi1* 🏥 \n\nWe have detected you are a *Doctor* 🩺 \n\nWhich Patient 😷 record would you like to fetch 📋, \n\nPlease Enter their Patient Id 🔢"    
            elif user_type == "Patient":
                msg = "Hello Welcome to *OpenMedi1* 🏥 \n\nWe have detected you are a *Patient* \n\n What would you like to do today ? \n\n1️⃣ Add a medical record to the OpenMedi Centralised Database. 🖥️\n\n2️⃣ Fetch your medical records 📋"
            else :
                msg = "Sorry 😕, You are not registered with OpenMedi1"
            
            send_msg(phone_id,msg)
            return '200'

        elif variables.counter[phone_id] == 1:
            if variables.track[phone_id]['user_type'] == 'Patient':
                if variables.incoming_msg[phone_id] == "1":
                    msg = "What are you suffering from 🤒 ? "
                    send_msg(phone_id, msg)
                    variables.counter[phone_id] = variables.counter[phone_id] + 1
                    variables.track[phone_id]['flow_type'] = 'add record'
                    return '200'
                elif variables.incoming_msg[phone_id] == "2":
                    msg = PatientData(phone_id)
                    send_msg(phone_id, msg)
                    return '200'
            elif variables.track[phone_id]['user_type'] == 'Doctor':
                Patient_mobile_no = variables.incoming_msg[phone_id]
                msg = PatientData(Patient_mobile_no)
                send_msg(phone_id, msg)
                return '200'

        elif variables.counter[phone_id] == 2:
            if variables.track[phone_id]['user_type'] == 'Patient':
                if variables.track[phone_id]['flow_type'] == 'add record':
                    msg = "Send a photo of Doctor Prescription 📋"
                    variables.track[phone_id]['disease_name'] = variables.incoming_msg[phone_id]
                    send_msg(phone_id, msg)
                    variables.counter[phone_id] = variables.counter[phone_id] + 1
                    return '200'

        elif variables.counter[phone_id] == 3:
            if variables.track[phone_id]['user_type'] == 'Patient':
                if variables.track[phone_id]['flow_type'] == 'add record':
                    msg = "Enter Doctor's name 👩🏻‍⚕️"
                    send_msg(phone_id, msg)

                    #process incoming image here
                    pic_url = request.form.get('MediaUrl0')
                    variables.track[phone_id]['pic_url'] = pic_url
                    print('url',pic_url)
                    print('pic_url ',variables.track[phone_id]['pic_url'])
                    text = google_text_extraction(pic_url)
                    Hospitalnamefromocr = SearchHospitalName(text)
                    variables.track[phone_id]['Hospitalnamefromocr'] = Hospitalnamefromocr
                    # ocr text
                    print('ocr text',text)

                    variables.counter[phone_id] = variables.counter[phone_id] + 1
                    return '200'
        
        elif variables.counter[phone_id] == 4:
            if variables.track[phone_id]['user_type'] == 'Patient':
                if variables.track[phone_id]['flow_type'] == 'add record':
                    msg = ""
                    variables.track[phone_id]['Doctor_name'] = variables.incoming_msg[phone_id]

                    strpasstoprescription = '{"Disease" : "'+variables.track[phone_id]['disease_name']+'", "DoctorName" : "'+variables.track[phone_id]['Doctor_name']+'", "Date" : "'+str(today.strftime("%d/%m/%Y"))+'" , "Mobile_No" : "'+phone_id+'", "url" : "'+str(variables.track[phone_id]['pic_url'])+'"}'
                    print('strpasstoprescription',strpasstoprescription)
                    InsertPrescription(strpasstoprescription)

                    msg = "Record added to the Database for " +variables.track[phone_id]['Hospitalnamefromocr']+ ", Thank you 😄"
                    send_msg(phone_id, msg)
                    #process incoming image here

                    variables.counter[phone_id] = variables.counter[phone_id] + 1
                    return '200'



    except Exception as e:
        print('Got exception')
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return str('error')


@app.route('/signup',methods=['GET', 'POST'])
def signup():
    content = request.json
    print('cont', content)
    if content['hospital'] == 'Dummy' and content['license'] == 'Dummy':
        type = 'patient'
    elif content['hospital'] == 'Dummy' and content['license'] != 'Dummy':
        type = 'doctor'
    else :
        type = 'hospital'
    with pool.connect() as db_conn:
        if type == 'patient' :
            dateofbirth =  content["dateOfBirth"][:12]
            print('dateofbirth',dateofbirth)
            insert_stmt = sqlalchemy.text("INSERT INTO User_Patient (FirstName, LastName, Email, DOB, Mobile_No, Password) VALUES (:FirstName, :LastName, :Email, :DOB, :Mobile_No, :Password)")
            db_conn.execute(insert_stmt, FirstName = content["firstName"], LastName = content["lastName"], Email = content["email"], DOB = dateofbirth, Mobile_No = content["phone"], Password = content["password"])
            str = '{"result" : "success", "type" : "patient"}'

        elif type == 'doctor' :
            dateofbirth =  content["dateOfBirth"][:12]
            print('dateofbirth',dateofbirth)
            insert_stmt = sqlalchemy.text("INSERT INTO User_Doctor (FirstName, LastName, Email, DOB, Mobile_No, Password, Licence) VALUES (:FirstName, :LastName, :Email, :DOB, :Mobile_No, :Password, :Licence)")
            db_conn.execute(insert_stmt, FirstName = content["firstName"], LastName = content["lastName"], Email = content["email"], DOB = dateofbirth, Mobile_No = content["phone"], Password = content["password"], Licence = content["license"])
            str = '{"result" : "success", "type" : "doctor"}'

        else :
            insert_stmt = sqlalchemy.text("INSERT INTO User_Hospital (HospitalName, Address, Email, Mobile_No, Password, Licence) VALUES (:HospitalName, :Address, :Email, :Mobile_No, :Password, :Licence)")
            db_conn.execute(insert_stmt, HospitalName = content["hospital"], Address = content["address"], Email = content["email"], Mobile_No = content["phone"], Password = content["password"], Licence = content["license"])
            str = '{"result" : "success", "type" : "hospital"}'
        print(str)
    return str

@app.route('/login',methods=['GET', 'POST'])
def login():
    content = request.json
    print(content)
    with pool.connect() as db_conn:
        if content['type'] == 'Hospital' :
            results = db_conn.execute("SELECT * FROM User_Hospital Where Mobile_No ='"+content["phone"]+"' And Password ='"+content["password"]+"'").fetchall()
            if len(results) > 0 :
                str = '{"result" : "success", "type" : "hospital"}'
            else :
                str = '{"result" : "failure", "type" : "hospital"}'
        elif content['type'] == 'Doctor' :
            results = db_conn.execute("SELECT * FROM User_Doctor Where Mobile_No ='"+content["phone"]+"' And Password ='"+content["password"]+"'").fetchall()
            if len(results) > 0 :
                str = '{"result" : "success", "type" : "doctor"}'
            else :
                str = '{"result" : "failure", "type" : "doctor"}'
        elif content['type'] == 'Patient' :
            results = db_conn.execute("SELECT * FROM User_Patient Where Mobile_No ='"+content["phone"]+"' And Password ='"+content["password"]+"'").fetchall()
            if len(results) > 0 :
                str = '{"result" : "success", "type" : "patient"}'
            else :
                str = '{"result" : "failure", "type" : "patient"}'
        return str

@app.route('/fetchpatientdata',methods=['GET', 'POST'])
def fetchpatientdata():
    content = request.json
    print(content)
    print(type(content))
    with pool.connect() as db_conn:
        my_list = []
        results = db_conn.execute("SELECT * FROM Prescription Where Mobile_No ="+content["phone"]).fetchall()
        if len(results) > 0 :
            for row in results:
                my_list.append(row._asdict())
        output = '{"result" : '+str(my_list)+'}'
        output = output.replace("\'", "\"")
        print(output)
    return str(output)

@app.route('/fetchprofile',methods=['GET', 'POST'])
def fetchprofile():
    content = request.json
    print(content)
    with pool.connect() as db_conn:
        if content['type'] == 'Hospital' :
            results = db_conn.execute("SELECT * FROM User_Hospital Where Mobile_No ='"+content["email"]+"'").fetchall()
            if len(results) > 0 :
                for row in results:
                    strOutput = str(row._asdict())
            else :
                strOutput = '{"result" : "failure", "type" : "hospital"}'
        elif content['type'] == 'Doctor' :
            results = db_conn.execute("SELECT * FROM User_Doctor Where Mobile_No ='"+content["email"]+"'").fetchall()
            if len(results) > 0 :
                for row in results:
                    strOutput = str(row._asdict())
            else :
                strOutput = '{"result" : "failure", "type" : "doctor"}'
        elif content['type'] == 'Patient' :
            results = db_conn.execute("SELECT * FROM User_Patient Where Mobile_No ='"+content["email"]+"'").fetchall()
            if len(results) > 0 :
                for row in results:
                    strOutput = str(row._asdict())
            else :
                strOutput = '{"result" : "failure", "type" : "patient"}'
        strOutput = strOutput.replace("\'", "\"")
    return strOutput


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)