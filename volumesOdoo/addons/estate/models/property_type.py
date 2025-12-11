from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipo de Propiedad Inmobiliaria"

    name = fields.Char(string="Nombre", required=True)
