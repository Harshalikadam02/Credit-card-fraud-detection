from twilio.rest import Client
import keys

client = Client(keys.account_sid, keys.auth_token) 

message = client.messages.create(

    body="A Suspicious Transaction has been detected!",
    from_=keys.twilio_number,
    to=keys.target_number,

)

print(message.body)