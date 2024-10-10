import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
import sys
import os
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.tools import (
    email_sender_new_tirage,
    email_sender_results_available,
    email_sender_contact_us,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from app.config import Config

app_email = Config.MAIL_APP
app_email_password = Config.APP_EMAIL_PASSWORD


class TestEmailSender(unittest.TestCase):
    @patch("smtplib.SMTP_SSL")
    def test_email_sender_new_tirage(self, mock_smtp):
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        receiver = "test@example.com"

        # Appeler la fonction avec un seul argument
        email_sender_new_tirage(receiver)

        # Vérification que le SMTP_SSL a été appelé correctement
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465, context=mock.ANY)
        mock_instance.login.assert_called_once_with(
            Config.MAIL_APP, Config.APP_EMAIL_PASSWORD
        )
        mock_instance.sendmail.assert_called_once()

        # Récupération du corps de l'email envoyé
        email_body = mock_instance.sendmail.call_args[0][2]

        # Corps de l'email attendu
        expected_content = (
            "Bonjour,\n\n"
            "Nous avons le plaisir de vous informer qu'un nouveau tirage vient d'être lancé sur AppLoto.\n"
            "C'est l'occasion parfaite pour tenter votre chance et peut-être remporter le gros lot !\n\n"
            "Rendez-vous dès maintenant sur notre application pour participer.\n\n"
            "Ne manquez pas cette opportunité ! Que la chance soit avec vous !\n\n"
            "Cordialement,\n"
            "L'équipe AppLoto\n"
        ).strip()

        # Vérification que le contenu de l'email envoyé contient le contenu attendu
        self.assertIn(expected_content, email_body.strip())

    @patch("smtplib.SMTP_SSL")
    def test_email_sender_results_available(self, mock_smtp):
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        receiver = "test@example.com"
        tirage_name = "Tirage 123"

        # Appeler la fonction avec deux arguments
        email_sender_results_available(receiver, tirage_name)

        # Vérification que le SMTP_SSL a été appelé correctement
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465, context=mock.ANY)
        mock_instance.login.assert_called_once_with(
            Config.MAIL_APP, Config.APP_EMAIL_PASSWORD
        )
        mock_instance.sendmail.assert_called_once()

        # Récupération du corps de l'email envoyé
        email_body = mock_instance.sendmail.call_args[0][2]

        # Corps de l'email attendu
        expected_content = (
            "Bonjour,\n\n"
            "Nous sommes heureux de vous informer que les résultats du tirage Tirage 123 sont maintenant disponibles sur AppLoto.\n"
            "Consultez votre compte pour voir si vous avez gagné !\n\n"
            "Merci de faire partie de notre communauté et bonne chance pour le prochain tirage !\n\n"
            "Cordialement,\n"
            "L'équipe AppLoto\n"
        ).strip()

        # Vérification que le contenu de l'email envoyé contient le contenu attendu
        self.assertIn(expected_content, email_body.strip())

    @patch("smtplib.SMTP_SSL")
    def test_email_sender_contact_us(self, mock_smtp):
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        user_email = "user@example.com"
        user_message = "Hello, I need help!"

        # Appeler la fonction pour envoyer l'email
        email_sender_contact_us(user_email, user_message)

        # Vérification que le SMTP_SSL a été appelé correctement
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465, context=mock.ANY)
        mock_instance.login.assert_called_once_with(
            Config.MAIL_APP, Config.APP_EMAIL_PASSWORD
        )
        mock_instance.sendmail.assert_called_once()

        # Récupération du corps de l'email envoyé
        email_body = mock_instance.sendmail.call_args[0][2]

        # Corps de l'email attendu
        expected_body = f"""\
Vous avez reçu un nouveau message de l'utilisateur :

E-mail : {user_email}
Message :
{user_message}
""".strip()

        # Vérification que le corps de l'email contient les éléments attendus
        self.assertIn("Nouveau message de Contactez-nous", email_body)
        self.assertIn(user_email, email_body)
        self.assertIn(user_message, email_body)
        self.assertEqual(email_body.strip(), expected_body)


if __name__ == "__main__":
    unittest.main()
