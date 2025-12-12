import datetime
from datetime import timedelta

from odoo import api, fields, models


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

    # Campos para validez y fecha límite
    validity = fields.Integer(string="Validez (días)", default=7)
    date_deadline = fields.Date(
        string="Fecha Límite",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            # Convertir a date si es datetime
            if isinstance(create_date, datetime.datetime):
                create_date = create_date.date()
            record.date_deadline = create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            # Convertir a date si es datetime
            if isinstance(create_date, datetime.datetime):
                create_date = create_date.date()
            record.validity = (record.date_deadline - create_date.date()).days
