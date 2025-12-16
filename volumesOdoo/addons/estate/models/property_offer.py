import datetime
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    """
    Obtiene las ofertas realizadas por los compradores para las propiedades.
    Cada oferta está vinculada a una propiedad específica y a un comprador.
    """

    _name = "estate.property.offer"
    _description = "Oferta de Propiedad Inmobiliaria"
    _order = "price desc"

    # Precio que ofrece el comprador por la propiedad
    price = fields.Float(string="Precio")

    # Restricción SQL: precio debe ser estrictamente positivo (Odoo 19)
    _check_price = models.Constraint(
        "CHECK(price > 0)",
        "El precio de la oferta debe ser estrictamente positivo.",
    )

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

    # Campo relacionado: tipo de propiedad (almacenado para búsquedas eficientes)
    property_type_id = fields.Many2one(
        "estate.property.type",
        related="property_id.property_type_id",
        string="Tipo de Propiedad",
        store=True,
    )

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
            record.validity = (record.date_deadline - create_date).days

    def create(self, vals_list):
        for vals in vals_list:
            if "property_id" in vals:
                property_id = self.env["estate.property"].browse(vals["property_id"])
                if property_id.state == "canceled":
                    raise UserError("Cannot create offers for canceled properties.")
                # Cambiar estado a "offer_received" cuando se crea una oferta
                if property_id.state == "new":
                    property_id.state = "offer_received"
        return super().create(vals_list)

    def action_accept(self):
        for record in self:
            if record.property_id.state == "canceled":
                raise UserError("Cannot accept an offer for a canceled property.")
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = "sold"
            # Rechazar todas las otras ofertas de la misma propiedad
            other_offers = record.property_id.offer_ids.filtered(
                lambda o: o.id != record.id
            )
            other_offers.action_refuse()
        return True

    def action_refuse(self):
        for record in self:
            if record.status == "accepted":
                raise UserError("Accepted offers cannot be refused.")
                raise UserError("Accepted offers cannot be refused.")
            record.status = "refused"
        return True
