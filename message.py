from twilio.twiml.messaging_response import MessagingResponse
from flask import Response
import os
from twilio import rest
from twilio.rest import Client
os.environ['TWILIO_ACCOUNT_SID'] = ""
os.environ['TWILIO_AUTH_TOKEN'] = ""
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']


client = Client(account_sid, auth_token)

def send_msg(st):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(st)

    print("####### In Msg ########")
    
    responded = True
    return resp
    
def send_template_msg(phone_id,st):
    client = rest.Client(account_sid, auth_token)
    message = client.messages.create(
                                from_='whatsapp:+14155238886',
                                body=st,
                                to='whatsapp:+91'+phone_id
                            )

    print("####### In template Msg ########")
    print(st)
    return Response("ok",status=200)


def send_file(phone_id,url,st='success'):
    
    client = rest.Client(account_sid, auth_token)

    message = client.messages.create(
                       media_url=url,
                       from_='whatsapp:+14155238886',
                       body = st,
                       to='whatsapp:+91'+phone_id
                       )

    return True
