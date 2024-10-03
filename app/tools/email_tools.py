from app import Config
from email.message import EmailMessage
import ssl
import smtplib


def email_sender(receiver):
    app_mail = Config.MAIL_APP
    app_mail_password = Config.APP_EMAIL_PASSWORD
    subject = "Un nouveau tirage est disponible"
    body = """
    Bonjour,

    Nous avons le plaisir de vous informer qu'un nouveau tirage vient d'être lancé sur AppLoto.
    C'est l'occasion parfaite pour tenter votre chance et peut-être remporter le gros lot !

    Rendez-vous dès maintenant sur notre application pour participer.

    Ne manquez pas cette opportunité ! Que la chance soit avec vous !

    Cordialement,
    L'équipe AppLoto
    """

    em = EmailMessage()
    em["From"] = app_mail
    em["To"] = receiver
    em["Subject"] = subject
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(app_mail, app_mail_password)
        smtp.sendmail(app_mail, receiver, em.as_string())
