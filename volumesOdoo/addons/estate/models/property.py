from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Propiedad Inmobiliaria"

    name = fields.Char(string="Título", required=True)
    property_type_id = fields.Many2one("estate.property.type", string="Tipo de Propiedad")
    buyer_id = fields.Many2one("res.partner", string="Comprador", copy=False)
    seller_id = fields.Many2one("res.users", string="Vendedor", default=lambda self: self.env.user)
    description = fields.Text(string="Descripción")
    postcode = fields.Char(string="Código Postal")
    date_availability = fields.Date(
        string="Fecha de Disponibilidad",
        copy=False,
        default=fields.Date.today(),
    )
    expected_price = fields.Float(string="Precio Esperado", required=True)
    selling_price = fields.Float(string="Precio de Venta", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Dormitorios", default=2)
    living_area = fields.Integer(string="Área de Vivienda (m²)")
    facades = fields.Integer(string="Fachadas")
    garage = fields.Boolean(string="Garaje")
    garden = fields.Boolean(string="Jardín")
    garden_area = fields.Integer(string="Área de Jardín (m²)")
    garden_orientation = fields.Selection(
        selection=[
            ("north", "Norte"),
            ("south", "Sur"),
            ("east", "Este"),
            ("west", "Oeste"),
        ],
        string="Orientación del Jardín",
    )
    active = fields.Boolean(default=True)
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

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0)",
            "El precio esperado debe ser positivo.",
        ),
    ]
