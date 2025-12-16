from odoo import api, fields, models


class EstatePropertyType(models.Model):
    """
    Modelo que representa los tipos diferentes de propiedades inmobiliarias.
    """

    _name = "estate.property.type"
    _description = "Tipo de Propiedad Inmobiliaria"
    _order = "sequence, name"

    # Campo para ordenamiento manual
    sequence = fields.Integer(string="Secuencia", default=10)

    # Nombre del tipo de propiedad
    name = fields.Char(string="Nombre", required=True)

    # Relación One2many con propiedades de este tipo
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )

    # Relación One2many inversa: todas las ofertas para propiedades de este tipo
    offer_ids = fields.One2many(
        "estate.property.offer", "property_type_id", string="Offers"
    )

    # Campo computado: cantidad de ofertas para este tipo de propiedad
    offer_count = fields.Integer(
        string="Número de Ofertas", compute="_compute_offer_count"
    )

    # Cálculo del número de ofertas
    @api.depends("offer_ids")
    def _compute_offer_count(self):
        """
        Calcula el número de ofertas asociadas a este tipo de propiedad.
        Se basa en la cantidad de registros en offer_ids.
        """
        for record in self:
            record.offer_count = len(record.offer_ids)

    # Restricción SQL: nombre único (Odoo 19)
    _unique_type_name = models.Constraint(
        "UNIQUE(name)",
        "El nombre del tipo de propiedad debe ser único.",
    )
