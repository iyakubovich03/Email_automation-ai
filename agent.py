from emailc import get_unread_emails_last_24h, send_email
import requests
import json

def agent():
    emails = get_unread_emails_last_24h()# list of dicitonaries 
    print(emails)
    for email in emails:
        print(email)
        print()
        data={
            "model":"llama3.2",
            "prompt":f"Classify whether this text is asking how about 'how I am doing? checking up on me? Seeing what's new?' things of this nature, respond with just a 'yes' or 'no' dont include a period, {email['body']}",
            "stream": False
        }
        url="http://localhost:11434/api/generate"

        response = requests.post(url,json=data)
        respj=(json.loads(response.text))["response"]# gets yes or no classifciatoin

        if respj in ["yes","Yes"]:
            addy=(email['from'].split("<"))[1][:len((email['from'].split("<"))[1])-1]
            name=email['from'].split("<")[0]
            #generate custuom reponse
            pay={
            "model":"llama3.2",
            "prompt":f"Create a couple sentence response to this message be specific, refrence their name based on the message,if they dont directly mention their name, use their fist name associated with their email,  and only include the message, {email['body']}, the name associated with the email is {name}",
            "stream": False
            }
            cont_response = requests.post(url,json=pay)
            cont = json.loads(cont_response.text)['response']
          
            
            send_email(addy,"Checking up",cont)
            #then send custom email

    
       

        #need to classify the email here
        #if classifeid, then generate content then send email 

    return 
agent()
