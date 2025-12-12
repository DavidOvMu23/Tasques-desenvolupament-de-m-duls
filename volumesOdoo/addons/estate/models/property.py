from odoo import api, fields, models


class EstateProperty(models.Model):
    """
    Modelo principal que representa una propiedad inmobiliaria.
    Almacena toda la información relacionada con una propiedad,
    sus características y su estado en el proceso de venta.
    """

    _name = "estate.property"
    _description = "Propiedad Inmobiliaria"

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

    # Restricción SQL: el precio esperado debe ser siempre mayor a 0
    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0)",
            "El precio esperado debe ser positivo.",
        ),
    ]

    # Campos calculados
    total_area = fields.Integer(string="Área Total (m²)", compute="_compute_total_area")
    best_price = fields.Float(string="Mejor Oferta", compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = (
                max(record.offer_ids.mapped("price")) if record.offer_ids else 0
            )
