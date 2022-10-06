from google.cloud.sql.connector import Connector
import sqlalchemy
import os
import json
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


def fetchusertype(mobno):
    with pool.connect() as db_conn:
        results = db_conn.execute("SELECT * FROM User_Patient Where Mobile_No ="+mobno).fetchall()
        if len(results) > 0 :
            type = 'Patient'
        else :
            results = db_conn.execute("SELECT * FROM User_Doctor Where Mobile_No ="+mobno).fetchall()
            if len(results) > 0 :
                 type = 'Doctor'
    return type



def PatientData(mobno):
    with pool.connect() as db_conn:
        my_list = []
        results = db_conn.execute("SELECT * FROM Prescription Where Mobile_No ="+mobno).fetchall()
        if len(results) > 0 :
            for row in results:
                my_list.append(row._asdict())
        msg = "Here is the Medical Records you requested for 👇🏻\n\n"
        for item in my_list:
            msg = msg + "*Disease*: 🤒"+ item["Disease"] + "\n*Doctor Name* 🩺: " + item["DoctorName"] +"\n*Prescription* 📋: " + item["url"] + "\n*Date*  📅 :"+ item['Date']+"\n\n"
    return str(msg)

def InsertPrescription(jsondata):
    with pool.connect() as db_conn:
        a =json.loads(jsondata)
        insert_stmt = sqlalchemy.text("INSERT INTO Prescription (Disease, DoctorName, Date, Mobile_No, url) VALUES (:Disease, :DoctorName, :Date, :Mobile_No, :url)")
        db_conn.execute(insert_stmt, Disease=a["Disease"], DoctorName=a["DoctorName"], Date=a["Date"], Mobile_No=a["Mobile_No"], url=a["url"])
    
    return 'success'

def SearchHospitalName(strinput):
    with pool.connect() as db_conn:
        my_list = []
        hospitalname = []
        hosname = ''
        output = ''
        results = db_conn.execute("SELECT HospitalName FROM User_Hospital").fetchall()
        if len(results) > 0 :
            for row in results:
                my_list.append(row._asdict())
        print(my_list)
        for item in my_list:
            hospitalname.append(item["HospitalName"])
        for name in hospitalname :
            if name in strinput :
                hosname = name
                break

        if hosname != '':
            output = hosname
        else :
            output = 'Unverified Hospital'
    return str(output)


print(SearchHospitalName('dasasdGeetanjalijdasijasij adaudua'))