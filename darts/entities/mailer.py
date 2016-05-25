from darts import app
from flask_mail import Mail, Message

class Mailer():

	def send(self, subject, body, html, recipient):
		mail = Mail(app)
		messages = Message(subject, sender = ("XPX Darts App", "brettmeyerxpx@gmail.com"), recipients = [recipient])
		messages.body = body
		messages.html = html
		mail.send(messages)
