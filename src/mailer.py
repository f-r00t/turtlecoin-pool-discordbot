import requests
def send_email(email, pool, error):
    return requests.post(
            "https://api.mailgun.net/v3/sandbox-xxx-.mailgun.org/messages",
            auth=("api", "key-xxx"),
            data={
              "from": "Mailgun Sandbox <postmaster@sandbox-xxx-.mailgun.org>",
              "to": email,
              "subject": pool + "is down!",
              "text": "Hello! \n The pool " + pool + " just went down."
             }
    )
