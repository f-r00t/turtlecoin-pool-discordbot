import requests
def send_email(email, subject, message):
    return requests.post(
            "https://api.mailgun.net/v3/sandbox-xxx-.mailgun.org/messages",
            auth=("api", "key-xxx"),
            data={
              "from": "Mailgun Sandbox <postmaster@sandox-xxx-.mailgun.org>",
              "to": email,
              "subject": subject,
              "text": message
             }
    )
