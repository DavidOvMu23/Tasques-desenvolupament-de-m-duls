from odoo import fields, models


class EstatePropertyTag(models.Model):
    """
    Modelo que representa categorías que se pueden
    asignar a las propiedades para clasificarlas mejor.
    """

    _name = "estate.property.tag"
    _description = "Etiqueta de Propiedad Inmobiliaria"

    # Nombre de la etiqueta/categoría
    name = fields.Char(string="Nombre", required=True)
