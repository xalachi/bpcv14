from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ReportPaperformat(models.Model):
    _inherit = "report.paperformat"

    custom_report = fields.Boolean('My Format', default=False)


class BarcodeConfigurationTemplate(models.Model):
    _name = 'barcode.configuration.template'

    @api.model
    def _prduct_barcode_field(self):
        field_list = []
        ir_model_id = self.env['ir.model'].search([('model', '=', 'product.product')])
        for field in self.env['ir.model.fields'].search([
            ('field_description', '!=', 'unknown'), ('readonly', '=', False),
            ('model_id', '=', ir_model_id.id), ('ttype', '=', 'char')]):
            field_list.append((field.name, field.field_description))
        return field_list

    name = fields.Char('Name', required=True)
    select_default = fields.Boolean("Use As Defualt Template", default=False)
    margin_top = fields.Float(string="Margin(Top)", required=True)
    # label_height = fields.Integer('Page Height(MM)', required=True, help="Page Height in(mm) please check calculated in(Px). Px is calculated by using DPI and Page Height")
    # label_width = fields.Integer('Page Width(MM)', required=True, help="Page Width in(mm) please check calculated in(Px). Px is calculated by using DPI and Page Width")
    label_height = fields.Float('Page Height(MM)', required=True,
                                help="Page Height in(mm) please check calculated in(Px). Px is calculated by using DPI and Page Height")
    label_width = fields.Float('Page Width(MM)', required=True,
                               help="Page Width in(mm) please check calculated in(Px). Px is calculated by using DPI and Page Width")

    label_height_px = fields.Integer('Page Height(Px)', readonly=True, compute='_compute_height_width_px',
                                     help="Page Height in(mm) please check calculated in(Px). Px is calculated by using DPI and Page Height")
    label_width_px = fields.Integer('Page Width(Px)', readonly=True, compute='_compute_height_width_px',
                                    help="Page Width in(mm) please check calculated in(Px). Px is calculated by using DPI and Page Width")
    margin_bottom = fields.Float(string="Margin(Bottom)", required=True)
    dpi = fields.Integer(string="Output DPI", required=True)
    margin_left = fields.Float(string="Margin(Left)", required=True)
    margin_right = fields.Float(string="Margin(Right)", required=True)
    header_spacing = fields.Integer(string="Header Spacing", required=True)
    barcode_type = fields.Selection(
        [('Codabar', 'Codabar'), ('Code11', 'Code11'), ('Code128', 'Code128'), ('EAN13', 'EAN13'), ('Extended39', 'Extended39'),
         ('EAN8', 'EAN8'), ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'), ('I2of5', 'I2of5'), ('UPCA', 'UPCA'), ('QR', 'QR')],
        string='Type', required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id)
    currency_position = fields.Selection([('after', 'After Amount'), ('before', 'Before Amount')], 'Symbol Position',
                                         help="Determines where the currency symbol should be placed after or before the amount.", default='before')
    barcode_width = fields.Integer(string="Width", help="Width of barcode.")
    barcode_height = fields.Integer(string="Height", help="Height of barcode.")
    barcode_field = fields.Selection('_prduct_barcode_field', string="Barcode Field")
    display_width = fields.Integer(string="Display Width (px)", help="This width will required for display barcode in label.")
    display_height = fields.Integer(string="Display Height (px)", help="This height will required for display barcode in label.")
    humanreadable = fields.Boolean("Human Readable")

    product_desc = fields.Boolean('Product Description', default=True)
    company_name = fields.Char('Company Name', default=lambda self: self.env.user.company_id.name)
    product_name = fields.Boolean('Product Name', default=True)

    price_display = fields.Boolean('Price')
    barcode = fields.Boolean('Barcode Label')
    product_variant = fields.Boolean('Attributes')
    product_code = fields.Boolean('Product Default Code')
    default_qty_labels = fields.Selection([('order_qty', 'Base On Order Qty'), ('one_qty', 'Default 1 Qty')],
                                          string="Print List Of Barcodes", default="order_qty")
    lot = fields.Boolean('Production Lot')

    product_name_size = fields.Char('Product Font Size', default='10px')
    product_desc_size = fields.Char('Description Font Size', default='10px')
    product_variant_size = fields.Char('Attributes Font Size', default='10px')
    company_name_size = fields.Char('Company Font Size', default='10px')
    price_display_size = fields.Char('Price Font Size', default='10px')
    product_code_size = fields.Char('ProductCode Font Size', default='10px', help='ProductCode Font Size In Px')

    @api.onchange('label_height', 'label_width', 'dpi')
    def _onchange_height_width_px(self):
        for obj in self:
            if self.dpi:
                if obj.label_height:
                    try:
                        obj.label_height_px = (obj.label_height * self.dpi) / 25.4
                    except Exception as e:
                        obj.label_height_px = 0.0
                else:
                    obj.label_height_px = 0.0
                if obj.label_width:
                    try:
                        obj.label_width_px = (obj.label_width * self.dpi) / 25.4
                    except Exception as e:
                        obj.label_width_px = 0.0
                else:
                    obj.label_width_px = 0.0

    @api.depends('label_height', 'label_width', 'dpi')
    def _compute_height_width_px(self):
        for obj in self:
            if self.dpi:
                if obj.label_height:
                    try:
                        obj.label_height_px = (obj.label_height * self.dpi) / 25.4
                    except Exception as e:
                        obj.label_height_px = 0.0
                else:
                    obj.label_height_px = 0.0
                if obj.label_width:
                    try:
                        obj.label_width_px = (obj.label_width * self.dpi) / 25.4
                    except Exception as e:
                        obj.label_width_px = 0.0
                else:
                    obj.label_width_px = 0.0

    @api.constrains('select_default')
    def _check_multiple_default_template(self):
        if len(self.search([('select_default', '=', True)])) > 1:
            raise ValidationError(_('Only One Template Can Be Used As A Default Template'))

    @api.onchange('dpi')
    def onchange_dpi(self):
        if self.dpi < 80:
            self.dpi = 80

    @api.onchange('product_name_size', 'product_desc_size', 'product_variant_size', 'company_name_size', 'price_display_size', 'product_code_size')
    def onchange_font_size(self):
        if self.product_name_size and not (self.product_name_size.endswith('px') or self.product_name_size.endswith('Px')
                                           or self.product_name_size.endswith('PX')):
            raise ValidationError(_('Please add suffix as a px'))
        if self.product_desc_size and not (self.product_desc_size.endswith('px') or self.product_desc_size.endswith('Px')
                                           or self.product_desc_size.endswith('PX')):
            raise ValidationError(_('Please add suffix as a px'))
        if self.product_variant_size and not (self.product_variant_size.endswith('px') or self.product_variant_size.endswith('Px')
                                              or self.product_variant_size.endswith('PX')):
            raise ValidationError(_('Please add suffix as a px'))
        if self.company_name_size and not (self.company_name_size.endswith('px') or self.company_name_size.endswith('Px')
                                           or self.company_name_size.endswith('PX')):
            raise ValidationError(_('Please add suffix as a px'))
        if self.price_display_size and not (self.price_display_size.endswith('px') or self.price_display_size.endswith('Px')
                                            or self.price_display_size.endswith('PX')):
            raise ValidationError(_('Please add suffix as a px'))
        if self.product_code_size and not (self.product_code_size.endswith('px') or self.product_code_size.endswith('Px')
                                           or self.product_code_size.endswith('PX')):
            raise ValidationError(_('Please add suffix as a px'))
