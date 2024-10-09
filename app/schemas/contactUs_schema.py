from marshmallow import Schema, fields, validate, ValidationError


class ContactUsSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
