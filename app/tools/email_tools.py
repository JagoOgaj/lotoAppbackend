from app import Config
from email.message import EmailMessage
import ssl
import smtplib


def email_sender_new_tirage(receiver):
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


def email_sender_results_available(receiver, tirage_name):
    app_mail = Config.MAIL_APP
    app_mail_password = Config.APP_EMAIL_PASSWORD
    subject = "Les résultats du tirage sont disponibles"
    body = f"""
    Bonjour,

    Nous sommes heureux de vous informer que les résultats du tirage {tirage_name} sont maintenant disponibles sur AppLoto.
    Consultez votre compte pour voir si vous avez gagné !

    Merci de faire partie de notre communauté et bonne chance pour le prochain tirage !

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


def email_sender_contact_us(user_email, user_message):
    app_mail = Config.MAIL_APP
    app_mail_password = Config.APP_EMAIL_PASSWORD
    subject = "Nouveau message de Contactez-nous"
    body = f"""
    Vous avez reçu un nouveau message de l'utilisateur :

    E-mail : {user_email}
    Message :
    {user_message}
    """

    em = EmailMessage()
    em["From"] = app_mail
    em["To"] = app_mail  # L'adresse de l'application
    em["Subject"] = subject
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(app_mail, app_mail_password)
        smtp.sendmail(app_mail, app_mail, em.as_string())
