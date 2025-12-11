from odoo import fields, models


class EstatePropertyType(models.Model):
    """
    Modelo que representa los tipos diferentes de propiedades inmobiliarias.
    """

    _name = "estate.property.type"
    _description = "Tipo de Propiedad Inmobiliaria"

    # Nombre del tipo de propiedad
    name = fields.Char(string="Nombre", required=True)
