from flask import Flask
from flask_mail import Mail ,Message


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'mwangiryan12@gmail.com'
app.config['MAIL_PASSWORD'] = 'faov jubb tgvs yquq'
app.config['MAIL_DEFAULT_SENDER'] = 'mwangiryan12@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)

@app.route('/')
def index():
    msg = Message("Test Email", recipients = ["dicksonmurith155@gmail.com"])  # Replace with your own recipient email address.
    msg.body = "Hello, this is a test email from the Flask-Mail application."
    mail.send(msg)
    return "Email sent successfully!"
    
    mail.send(msg)

    msg = Message(
        subject = '',
        recipients = [],
        body = '',
        sender= '',
        cc= '',
        bcc= '',
        attachments='',
        html='',
        charset='',
        headers='',
        reply_to= '',
        date= '',
    )
# when the user wants to send multiple emails at once
@app.route('/bulk')
def bulk():
    users = [{'name': 'ryan', 'email': 'email@example.com'}]
    with mail.connect()as conn:
        for user in users:
            msg = Message("Test Email", sender = "mwangiryan12@gmail.com", recipients = [user['email']])
            msg.body = f"Hello, {user['name']}. This is a test email from the Flask-Mail application."
            conn.send(msg)

if __name__ == "__main__":
    app.run()