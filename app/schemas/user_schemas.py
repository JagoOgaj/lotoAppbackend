from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validates,
    validates_schema,
)
import re


class UserCreateSchema(Schema):
    """
    Schéma de validation et de sérialisation pour la création d'un utilisateur.

    Ce schéma est utilisé pour valider et formater les données lors de la création
    d'un nouvel utilisateur dans l'application. Il assure que les données fournies
    respectent les contraintes de longueur, de format d'email, et de force du mot de passe.

    Attributs:
        first_name (str): Le prénom de l'utilisateur. Doit avoir entre 2 et 50 caractères.
        last_name (str): Le nom de famille de l'utilisateur. Doit avoir entre 2 et 50 caractères.
        email (str): L'adresse email de l'utilisateur. Vérifiée pour un format valide.
        password (str): Le mot de passe de l'utilisateur, uniquement en mode "chargement" (load_only).

    Méthodes:
        validate_email(value: str):
            Valide l'email pour s'assurer qu'il respecte un format valide et qu'il est non vide.
            Lève une ValidationError si l'email est manquant ou incorrect.

        validate_password_strength(value: str):
            Valide la force du mot de passe. Il doit contenir au moins :
                - 8 caractères,
                - 1 lettre minuscule,
                - 1 lettre majuscule,
                - 1 chiffre,
                - 1 caractère spécial.
            Lève une ValidationError si ces critères ne sont pas respectés.

    Exceptions:
        ValidationError: Levée en cas de non-respect des règles de validation pour l'email ou le mot de passe.

    Usage:
        Utilisé pour créer un nouvel utilisateur, avec des contrôles rigoureux sur la validation des champs.
    """

    first_name = fields.Str(
        required=True,
        validate=[
            fields.Length(
                min=2,
                max=50,
                error="Le prénom doit contenir entre 2 et 50 caractères.",
            )
        ],
    )
    last_name = fields.Str(
        required=True,
        validate=[
            fields.Length(
                min=2,
                max=50,
                error="Le nom doit contenir entre 2 et 50 caractères.",
            )
        ],
    )
    email = fields.Str(
        required=True, error_messages={"required": "L'email est requis."}
    )
    password = fields.Str(load_only=True, required=True)

    @validates("email")
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis et ne peut pas être vide.")

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$", value):
            raise ValidationError("Format d'email invalide.")

    @validates("password")
    def validate_password_strength(self, value):
        if len(value) < 8:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )
        if not any(char.islower() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre minuscule."
            )
        if not any(char.isupper() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule."
            )
        if not any(char.isdigit() for char in value):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial."
            )

    @validates_schema
    def validate_name(self, data, **kwargs):
        if not data["first_name"].strip():
            raise ValidationError(
                "Le prénom ne peut pas être vide ou composé uniquement d'espaces.",
                field_name="first_name",
            )
        if not data["last_name"].strip():
            raise ValidationError(
                "Le nom ne peut pas être vide ou composé uniquement d'espaces.",
                field_name="last_name",
            )

    class Meta:
        fields = ("first_name", "last_name", "email", "password")


class UserUpdateSchema(Schema):
    """
    Schéma de validation pour la mise à jour des informations d'un utilisateur.

    Ce schéma est utilisé pour valider et formater les données lors de la mise à jour
    des informations d'un utilisateur dans l'application. Tous les champs sont optionnels,
    mais lorsqu'ils sont fournis, ils doivent respecter des règles spécifiques.

    Attributs:
        first_name (str): Prénom de l'utilisateur. Doit contenir au moins 2 caractères et ne pas être vide si fourni.
        last_name (str): Nom de famille de l'utilisateur. Doit contenir au moins 2 caractères et ne pas être vide si fourni.
        email (str): Adresse email de l'utilisateur. Vérifiée pour un format valide si fournie.
        notification (bool): Indicateur d'activation des notifications pour l'utilisateur.

    Méthodes:
        validate_email(value: str):
            Valide l'email pour s'assurer qu'il respecte un format valide.
            Lève une ValidationError si l'email est manquant ou incorrect.

        validate_first_name(value: str):
            Valide le prénom pour s'assurer qu'il contient au moins 2 caractères
            et qu'il n'est pas vide. Lève une ValidationError si ces critères ne sont pas respectés.

        validate_last_name(value: str):
            Valide le nom de famille pour s'assurer qu'il contient au moins 2 caractères
            et qu'il n'est pas vide. Lève une ValidationError si ces critères ne sont pas respectés.

    Exceptions:
        ValidationError: Levée en cas de non-respect des règles de validation pour l'email,
        le prénom ou le nom de famille.

    Usage:
        Utilisé pour mettre à jour les informations de l'utilisateur existant tout en s'assurant
        que les valeurs fournies sont valides.
    """

    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    email = fields.Email(required=False)
    notification = fields.Boolean(required=False)

    @validates("email")
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis.")

        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")

    @validates("first_name")
    def validate_first_name(self, value):
        if value is not None:  # Vérifie uniquement si la valeur est fournie
            if not value.strip():
                raise ValidationError(
                    "Le prénom ne peut pas être vide ou composé uniquement d'espaces."
                )
            if len(value) < 2:
                raise ValidationError("Le prénom doit avoir 2 character au minimum")

    @validates("last_name")
    def validate_last_name(self, value):
        if value is not None:  # Vérifie uniquement si la valeur est fournie
            if not value.strip():
                raise ValidationError(
                    "Le nom ne peut pas être vide ou composé uniquement d'espaces."
                )
            if len(value) < 2:
                raise ValidationError(
                    "Le nom de famille doit avoir 2 character au minimum"
                )


class UserPasswordUpdateSchema(Schema):
    """
    Schéma de validation pour la mise à jour du mot de passe d'un utilisateur.

    Ce schéma est utilisé pour valider les informations fournies lors de la mise à jour
    du mot de passe d'un utilisateur. Il garantit que le nouveau mot de passe respecte
    des règles de sécurité spécifiques.

    Attributs:
        old_password (str): L'ancien mot de passe de l'utilisateur. Doit être fourni
        lors de la mise à jour du mot de passe, mais n'est pas retourné dans les réponses.

        new_password (str): Le nouveau mot de passe de l'utilisateur. Doit être fourni
        lors de la mise à jour du mot de passe et sera validé pour assurer sa force.

    Méthodes:
        validate_password_strength(value: str):
            Valide le nouveau mot de passe pour s'assurer qu'il respecte les règles suivantes:
            - Doit contenir au moins 8 caractères.
            - Doit contenir au moins une lettre minuscule.
            - Doit contenir au moins une lettre majuscule.
            - Doit contenir au moins un chiffre.
            - Doit contenir au moins un caractère spécial (ex. !@#$%^&*).

            Lève une ValidationError si l'une de ces conditions n'est pas remplie.

    Exceptions:
        ValidationError: Levée en cas de non-respect des règles de validation
        pour le nouveau mot de passe.

    Usage:
        Utilisé pour mettre à jour le mot de passe d'un utilisateur tout en
        garantissant que le nouveau mot de passe est suffisamment fort pour
        assurer la sécurité de l'utilisateur.
    """

    old_password = fields.Str(load_only=True, required=True)
    new_password = fields.Str(load_only=True, required=True)

    @validates("new_password")
    def validate_password_strength(self, value):
        if len(value) < 8:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )
        if not any(char.islower() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre minuscule."
            )
        if not any(char.isupper() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule."
            )
        if not any(char.isdigit() for char in value):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial."
            )


class UserLoginSchema(Schema):
    """
    Schéma de validation pour la connexion d'un utilisateur.

    Ce schéma est utilisé pour valider les informations fournies lors de la tentative
    de connexion d'un utilisateur à son compte. Il garantit que l'email et le mot de
    passe fournis respectent des règles spécifiques.

    Attributs:
        email (str): L'email de l'utilisateur. Doit être fourni lors de la connexion.

        password (str): Le mot de passe de l'utilisateur. Doit être fourni lors de
        la connexion, mais ne sera pas retourné dans les réponses.

    Méthodes:
        validate_email(value: str):
            Valide l'email pour s'assurer qu'il respecte le format correct.
            Lève une ValidationError si l'email est vide ou ne correspond pas
            au format attendu.

        validate_password(value: str):
            Valide le mot de passe pour s'assurer qu'il n'est pas vide.
            Lève une ValidationError si le mot de passe est vide.

    Exceptions:
        ValidationError: Levée en cas de non-respect des règles de validation
        pour l'email ou le mot de passe.

    Usage:
        Utilisé pour authentifier les utilisateurs lors de la connexion, en
        garantissant que les informations fournies sont valides et conformes
        aux critères de sécurité.
    """

    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

    @validates("email")
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis et ne peut pas être vide.")
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")

    @validates("password")
    def validate_password(self, value):
        if not value:
            raise ValidationError(
                "Le mot de passe est requis et ne peut pas être vide."
            )


class UserOverviewInfoSchema(Schema):
    """
    Schéma de validation pour les informations d'aperçu d'un utilisateur.

    Ce schéma est utilisé pour valider les informations essentielles d'un utilisateur,
    telles que le prénom, le nom, l'email et les préférences de notification.
    Il garantit que ces informations sont correctement formatées et complètes.

    Attributs:
        first_name (str): Le prénom de l'utilisateur. Doit être fourni et
        ne peut pas être vide.

        last_name (str): Le nom de famille de l'utilisateur. Doit être
        fourni et ne peut pas être vide.

        email (str): L'adresse email de l'utilisateur. Doit être fournie
        et doit respecter le format d'email valide.

        notification (bool): Indique si l'utilisateur souhaite recevoir
        des notifications. Ce champ est requis.

    Exceptions:
        ValidationError: Levée en cas de non-respect des règles de validation
        pour le prénom, le nom, l'email ou les préférences de notification.

    Usage:
        Utilisé pour afficher ou manipuler les informations d'un utilisateur
        dans des contextes où un aperçu de ses détails est nécessaire,
        comme dans les interfaces administratives ou les profils d'utilisateur.
    """

    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    notification = fields.Boolean(required=True)


class UserOverviewAdvancedSchema(Schema):
    """
    Schéma de validation pour les informations avancées d'aperçu d'un utilisateur.

    Ce schéma est utilisé pour valider et sérialiser les informations détaillées
    d'un utilisateur, y compris son prénom, nom, email, rôle et dates de création
    et de mise à jour. Il est particulièrement utile pour les interfaces administratives
    ou les tableaux de bord d'utilisateur où des informations détaillées sont nécessaires.

    Attributs:
        first_name (str): Le prénom de l'utilisateur. Peut être vide.

        last_name (str): Le nom de famille de l'utilisateur. Peut être vide.

        email (str): L'adresse email de l'utilisateur. Doit être au format d'email valide.

        role_name (str): Le nom du rôle de l'utilisateur. Champ en lecture seule.

        created_at (datetime): La date et l'heure de création du compte de l'utilisateur.
        Champ en lecture seule.

        update_at (datetime): La date et l'heure de la dernière mise à jour du compte
        de l'utilisateur. Champ en lecture seule.

    Exceptions:
        ValidationError: Levée si les données fournies ne respectent pas les règles
        de validation, notamment pour l'email.

    Usage:
        Utilisé pour afficher des informations détaillées sur un utilisateur dans
        les interfaces administratives, permettant aux administrateurs de gérer
        les utilisateurs et leurs rôles.
    """

    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    role_name = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    update_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = (
            "first_name",
            "last_name",
            "email",
            "role_name",
            "created_at",
            "update_at",
        )
        dump_only = ("created_at", "update_at")
