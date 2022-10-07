from twilio.twiml.messaging_response import MessagingResponse
from flask import Response
import os
from twilio import rest
from twilio.rest import Client
os.environ['TWILIO_ACCOUNT_SID'] = ""
os.environ['TWILIO_AUTH_TOKEN'] = ""
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
import requests

def send_msg(st,mobno):
    
    url = "https://api.twilio.com/2010-04-01/Accounts/AC691257116d7e79d5ef694cbb3771f512/Messages.json"

    payload='From=whatsapp%3A%2B14155238886&Body='+st+'&To=whatsapp%3A%2B91'+mobno
    headers = {
    'Authorization': 'Basic QUM2OTEyNTcxMTZkN2U3OWQ1ZWY2OTRjYmIzNzcxZjUxMjplYTYwOGZjNzA0M2JkNjVjZWViMGVkNTUyMDkzZTcyMA==',
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


client = Client(account_sid, auth_token)

# def send_msg(st):
#     resp = MessagingResponse()
#     msg = resp.message()
#     msg.body(st)

#     print("####### In Msg ########")
    
#     responded = True
#     return resp

# def send_template_msg(phone_id,st):
#     client = rest.Client(account_sid, auth_token)
#     message = client.messages.create(
#                                 from_='whatsapp:+14155238886',
#                                 body=st,
#                                 to='whatsapp:+91'+phone_id
#                             )

#     print("####### In template Msg ########")
#     print(st)
#     return Response("ok",status=200)


def send_file(phone_id,url,st='success'):
    
    client = rest.Client(account_sid, auth_token)

    message = client.messages.create(
                       media_url=url,
                       from_='whatsapp:+14155238886',
                       body = st,
                       to='whatsapp:+91'+phone_id
                       )

    return True
