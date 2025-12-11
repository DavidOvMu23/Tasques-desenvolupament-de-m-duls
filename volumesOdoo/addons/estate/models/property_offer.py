from odoo import fields, models


class EstatePropertyOffer(models.Model):
    """
    Obtiene las ofertas realizadas por los compradores para las propiedades.
    Cada oferta está vinculada a una propiedad específica y a un comprador.
    """

    _name = "estate.property.offer"
    _description = "Oferta de Propiedad Inmobiliaria"

    # Precio que ofrece el comprador por la propiedad
    price = fields.Float(string="Precio")

    # Estado de la oferta
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        string="Estado",
        copy=False,
    )

    # Relación many2one con el comprador que realiza la oferta
    partner_id = fields.Many2one("res.partner", string="Comprador", required=True)

    # Relación many2one con la propiedad sobre la cual se realiza la oferta
    property_id = fields.Many2one("estate.property", string="Propiedad", required=True)
