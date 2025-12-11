from odoo import fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Oferta de Propiedad Inmobiliaria"

    price = fields.Float(string="Precio")
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        string="Estado",
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Comprador", required=True)
    property_id = fields.Many2one("estate.property", string="Propiedad", required=True)
