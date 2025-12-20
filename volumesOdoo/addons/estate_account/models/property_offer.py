from odoo import models, Command


class EstatePropertyOffer(models.Model):
    _inherit = "estate.property.offer"

    def action_accept(self):
        res = super().action_accept()
        # Crear factura al aceptar la oferta (si la propiedad está vendida y tiene comprador)
        for offer in self:
            property = offer.property_id
            if property.state == "sold" and property.buyer_id:
                journal = self.env["account.journal"].search(
                    [("type", "=", "sale")], limit=1
                )
                if not journal:
                    continue
                invoice_vals = {
                    "partner_id": property.buyer_id.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Comisión inmobiliaria (6%)",
                                "quantity": 1,
                                "price_unit": offer.price * 0.06,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Gastos administrativos",
                                "quantity": 1,
                                "price_unit": 100.0,
                            }
                        ),
                    ],
                }
                self.env["account.move"].create(invoice_vals)
        return res
