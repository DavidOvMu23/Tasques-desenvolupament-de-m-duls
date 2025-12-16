from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    """
    Modelo principal que representa una propiedad inmobiliaria.
    Almacena toda la información relacionada con una propiedad,
    sus características y su estado en el proceso de venta.
    """

    _name = "estate.property"
    _description = "Propiedad Inmobiliaria"
    _order = "id desc"

    # Campo de nombre de la propiedad
    name = fields.Char(string="Título", required=True)

    # Relación many2one con el tipo de propiedad
    property_type_id = fields.Many2one(
        "estate.property.type", string="Tipo de Propiedad"
    )

    # Relación many2many con etiquetas (una propiedad puede tener varias etiquetas)
    tag_ids = fields.Many2many("estate.property.tag", string="Etiquetas")

    # Relación one2many con las ofertas recibidas (una propiedad puede tener varias ofertas)
    offer_ids = fields.One2many(
        "estate.property.offer", "property_id", string="Ofertas"
    )

    # Comprador asociado a la propiedad (no se copia al duplicar registros)
    buyer_id = fields.Many2one("res.partner", string="Comprador", copy=False)

    # Vendedor (asignado automáticamente al usuario actual por defecto)
    seller_id = fields.Many2one(
        "res.users",
        string="Vendedor",
        default=lambda self: self.env.user,  # la funcion labda devuelve el usuario actual
    )

    # Descripción la propiedad
    description = fields.Text(string="Descripción")

    # Código postal
    postcode = fields.Char(string="Código Postal")

    # Fecha a partir de la cual la propiedad está disponible
    date_availability = fields.Date(
        string="Fecha de Disponibilidad",
        copy=False,
        default=fields.Date.today(),
    )

    # Precio solicitado por el vendedor
    expected_price = fields.Float(string="Precio Esperado", required=True)

    # Precio final de venta (solo lectura, se actualiza cuando se vende)
    selling_price = fields.Float(string="Precio de Venta", readonly=True, copy=False)

    # Número de dormitorios (por defecto 2)
    bedrooms = fields.Integer(string="Dormitorios", default=2)

    # Área de la vivienda en metros cuadrados
    living_area = fields.Integer(string="Área de Vivienda (m²)")

    # Número de fachadas
    facades = fields.Integer(string="Fachadas")

    # Indicador si tiene garaje
    garage = fields.Boolean(string="Garaje")

    # Indicador si tiene jardín
    garden = fields.Boolean(string="Jardín")

    # Área del jardín en metros cuadrados
    garden_area = fields.Integer(string="Área de Jardín (m²)")

    # Orientación del jardín (Norte, Sur, Este, Oeste)
    garden_orientation = fields.Selection(
        selection=[
            ("north", "Norte"),
            ("south", "Sur"),
            ("east", "Este"),
            ("west", "Oeste"),
        ],
        string="Orientación del Jardín",
    )

    # Indica si la propiedad está activa en el sistema
    active = fields.Boolean(default=True)

    # Estado del proceso de venta: Nuevo, Oferta Recibida, Oferta Aceptada, Vendido, Cancelado
    state = fields.Selection(
        selection=[
            ("new", "Nuevo"),
            ("offer_received", "Oferta Recibida"),
            ("offer_accepted", "Oferta Aceptada"),
            ("sold", "Vendido"),
            ("canceled", "Cancelado"),
        ],
        string="Estado",
        required=True,
        copy=False,
        default="new",
    )

    # Restricciones SQL (Odoo 19)
    _check_expected_price = models.Constraint(
        "CHECK(expected_price > 0)",
        "El precio esperado debe ser estrictamente positivo.",
    )
    _check_selling_price = models.Constraint(
        "CHECK(selling_price >= 0)",
        "El precio de venta debe ser positivo.",
    )
    _check_bedrooms = models.Constraint(
        "CHECK(bedrooms >= 0)",
        "El número de dormitorios debe ser positivo.",
    )
    _check_living_area = models.Constraint(
        "CHECK(living_area >= 0)",
        "El área de vivienda debe ser positiva.",
    )
    _check_facades = models.Constraint(
        "CHECK(facades >= 0)",
        "El número de fachadas debe ser positivo.",
    )
    _check_garden_area = models.Constraint(
        "CHECK(garden_area >= 0)",
        "El área de jardín debe ser positiva.",
    )

    # Restricción Python: el precio de venta no puede ser inferior al 90% del precio esperado
    @api.constrains("selling_price", "expected_price")
    def _check_selling_price_percentage(self):
        """
        Valida que el precio de venta sea al menos el 90% del precio esperado.
        Utiliza float_compare para evitar problemas de precisión con decimales.
        """
        for record in self:
            # Solo validar si hay precio de venta (no es 0)
            if record.selling_price > 0:
                min_price = record.expected_price * 0.90
                if (
                    float_compare(record.selling_price, min_price, precision_digits=2)
                    < 0
                ):
                    raise ValidationError(
                        "El precio de venta no puede ser inferior al 90%% del precio esperado (%.2f)."
                        % min_price
                    )

    # Campos calculados
    total_area = fields.Integer(string="Área Total (m²)", compute="_compute_total_area")
    best_price = fields.Float(string="Mejor Oferta", compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        """
        Calcula el área total sumando el área de vivienda y el área de jardín.
        """
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        """
        Calcula la mejor oferta (precio más alto) entre todas las ofertas recibidas.
        Retorna 0 si no hay ofertas.
        """
        for record in self:
            record.best_price = (
                max(record.offer_ids.mapped("price")) if record.offer_ids else 0
            )

    def action_sold(self):
        """
        Marca la propiedad como vendida.
        Valida que no esté cancelada y rechaza todas las ofertas no aceptadas.
        """
        for record in self:
            if record.state == "canceled":
                raise UserError("Canceled properties cannot be sold.")
            # Rechazar todas las ofertas que no estén aceptadas
            for offer in record.offer_ids:
                if offer.status != "accepted":
                    offer.status = "refused"
            record.state = "sold"
        return True

    def action_cancel(self):
        """
        Cancela la propiedad.
        Valida que no esté vendida y rechaza todas las ofertas pendientes.
        """
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be canceled.")
            # Rechazar todas las ofertas
            for offer in record.offer_ids:
                offer.status = "refused"
            record.state = "canceled"
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        """
        Previene la eliminación de propiedades que no estén en estado 'new' o 'canceled'.
        Solo se pueden eliminar propiedades nuevas o canceladas.
        """
        for record in self:
            if record.state not in ["new", "canceled"]:
                raise UserError(
                    "Solo se pueden eliminar propiedades en estado Nuevo o Cancelado."
                )

    @api.onchange("garden")
    def _onchange_garden(self):
        """
        Al activar el jardín, establece valores por defecto:
        - Área de jardín: 10 m²
        - Orientación: Norte
        Al desactivarlo, limpia los valores.
        """
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = None
