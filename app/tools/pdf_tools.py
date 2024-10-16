import base64
import pdfkit
from flask import render_template, make_response
from app import Config
import random
import os
import qrcode
from io import BytesIO

pdf_config = pdfkit.configuration(wkhtmltopdf=Config.PATH_WHHTMLTOPDF)


def generate_pdf(user_name, reward, draw_name):
    """
    Génère un PDF contenant les détails de la récompense de l'utilisateur, incluant un code QR.

    Cette fonction crée un PDF à partir d'un modèle HTML qui contient des informations
    sur la récompense de l'utilisateur, le nom du tirage, ainsi qu'un code QR
    représentant ces informations. Le PDF est ensuite retourné en tant que réponse
    HTTP, prêt à être téléchargé par l'utilisateur.

    Args:
        user_name (str): Le nom de l'utilisateur qui a gagné.
        reward (float): Le montant de la récompense gagnée.
        draw_name (str): Le nom du tirage auquel l'utilisateur a participé.

    Returns:
        response: Un objet de réponse Flask contenant le PDF à télécharger.

    Raises:
        Exception: Si une erreur se produit lors de la génération du PDF.
    """
    try:
        reward = round(reward, 2)
        qr_data = (
            f"Récompense: {reward} | Tirage: {draw_name} | Utilisateur: {user_name}"
        )
        qr_img = qrcode.make(qr_data)

        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_code_base64 = (
            f"data:image/png;base64,{base64.b64encode(qr_buffer.getvalue()).decode()}"
        )

        css_path = os.path.join(os.getcwd(), "app", "static", "pdf.css")
        render_html = render_template(
            "pdf.html",
            user_name=user_name,
            id=generate_id(),
            reward=reward,
            draw_name=draw_name,
            css_path=css_path,
            qr_code=qr_code_base64,
        )

        options = {
            "enable-local-file-access": None,
            "no-stop-slow-scripts": None,
        }

        pdf = pdfkit.from_string(
            render_html, False, configuration=pdf_config, options=options, css=css_path
        )

        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename=recompense_{draw_name}_{user_name}.pdf"

        return response

    except Exception as e:
        raise Exception(str(e))


def generate_id():
    """
    Génère un identifiant aléatoire composé de 10 chiffres uniques.

    Cette fonction utilise la fonction `random.sample` pour créer un identifiant
    de 10 chiffres, choisis aléatoirement à partir de la plage 0-49.

    Returns:
        str: Une chaîne représentant un identifiant aléatoire unique de 10 chiffres.
    """
    return "".join(str(n) for n in random.sample(range(50), 10))
