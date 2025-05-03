import datetime
import base64
import os.path
import pickle
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', "https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE = 'token.pickle'

def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails_last_24h():
    service = authenticate()
    
    # Calculate the date 24 hours ago
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y/%m/%d')
    
    # Query for unread emails from the last 24 hours
    query = f'is:unread after:{yesterday_str}'
    
    try:
        # Get the list of messages
        results = service.users().messages().list(
            userId='me',
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        print(messages)

        if not messages:
            print('No unread messages found in the last 24 hours.')
            return []
        print()
        print()
        emails = []
        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            print(message)
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Get the email body
            body = ''
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
            
            emails.append({
                'id': message['id'],
                'subject': subject,
                'from': sender,
                'date': date,
                'snippet': msg['snippet'],
                'body': body
            })
        
        return emails
        
    except Exception as e:
        print(f'An error occurred: {e}')
        return []

def send_email(email_address, subj, email_body):
    msg = EmailMessage()
    msg.set_content(email_body)
    msg["To"] = email_address
    msg["From"] = "me"
    msg["Subject"] = subj
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode() #this is the content
    
    # Use the same authentication function to get the service
    service = authenticate() #auhtenticates getting toekn
    service.users().messages().send(userId="me", body={"raw": raw}).execute()#sends

if __name__ == "__main__":
    emails = get_unread_emails_last_24h() #list of email each is a dicontary 
    for email in emails:
        print("\nEmail Details:")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Date: {email['date']}")
        print(f"Body Preview: {email['body'][:200]}...")
        print("-" * 50)

send_email("vanechkay@gmail.com","test","test")

#have my tool method to send emails 

#this file includes all the required functions to pull the email 