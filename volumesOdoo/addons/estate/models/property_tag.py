from odoo import fields, models


class EstatePropertyTag(models.Model):
    """
    Modelo que representa categorías que se pueden
    asignar a las propiedades para clasificarlas mejor.
    """

    _name = "estate.property.tag"
    _description = "Etiqueta de Propiedad Inmobiliaria"
    _order = "name"

    # Nombre de la etiqueta/categoría
    name = fields.Char(string="Nombre", required=True)

    # Color para la etiqueta (selector de color)
    color = fields.Integer(string="Color")

    # Restricción SQL: nombre único (Odoo 19)
    _unique_tag_name = models.Constraint(
        "UNIQUE(name)",
        "El nombre de la etiqueta debe ser único.",
    )
