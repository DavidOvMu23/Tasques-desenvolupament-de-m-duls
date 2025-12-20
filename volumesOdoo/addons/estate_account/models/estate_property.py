from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        # Lógica de facturación al vender la propiedad
        res = super().action_sold()
        # Solo crear factura si hay comprador y precio de venta
        for property in self:
            print(
                "DEBUG estate_account: Entrando en facturación para propiedad",
                property.id,
            )
            # Buscar la oferta aceptada
            accepted_offer = property.offer_ids.filtered(
                lambda o: o.status == "accepted"
            )
            if property.buyer_id and accepted_offer:
                selling_price = accepted_offer[0].price
                print(
                    "DEBUG estate_account: Hay comprador y oferta aceptada, precio:",
                    selling_price,
                )
                # Buscar diario de ventas
                journal = self.env["account.journal"].search(
                    [
                        ("type", "=", "sale"),
                    ],
                    limit=1,
                )
                if not journal:
                    print("DEBUG estate_account: No hay diario de ventas")
                    continue  # No hay diario de ventas
                invoice_vals = {
                    "partner_id": property.buyer_id.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Comisión inmobiliaria (6%)",
                                "quantity": 1,
                                "price_unit": selling_price * 0.06,
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
                print("DEBUG estate_account: Creando factura con valores", invoice_vals)
                self.env["account.move"].create(invoice_vals)
            else:
                print("DEBUG estate_account: Sin comprador o sin oferta aceptada")
        for property in self:
            print(
                "DEBUG estate_account: Entrando en facturación para propiedad",
                property.id,
            )
            # Si hay ofertas, aceptar automáticamente la mayor
            if property.offer_ids:
                best_offer = max(property.offer_ids, key=lambda o: o.price)
                if best_offer.status != "accepted":
                    best_offer.status = "accepted"
                    property.buyer_id = best_offer.partner_id
                    property.selling_price = best_offer.price
                    print(
                        f"DEBUG estate_account: Oferta aceptada automáticamente: {best_offer.price} para {best_offer.partner_id.name}"
                    )
            # Buscar la oferta aceptada
            accepted_offer = property.offer_ids.filtered(
                lambda o: o.status == "accepted"
            )
            if property.buyer_id and accepted_offer:
                selling_price = accepted_offer[0].price
                print(
                    "DEBUG estate_account: Hay comprador y oferta aceptada, precio:",
                    selling_price,
                )
                # Buscar diario de ventas
                journal = self.env["account.journal"].search(
                    [
                        ("type", "=", "sale"),
                    ],
                    limit=1,
                )
                if not journal:
                    print("DEBUG estate_account: No hay diario de ventas")
                    continue  # No hay diario de ventas
                invoice_vals = {
                    "partner_id": property.buyer_id.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Comisión inmobiliaria (6%)",
                                "quantity": 1,
                                "price_unit": selling_price * 0.06,
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
                print("DEBUG estate_account: Creando factura con valores", invoice_vals)
                self.env["account.move"].create(invoice_vals)
            else:
                print("DEBUG estate_account: Sin comprador o sin oferta aceptada")
