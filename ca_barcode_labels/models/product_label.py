from reportlab.graphics import barcode

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProdcutLabel(models.TransientModel):
    _name = 'product.label'

    def _get_default_barcode_template(self):
        template = self.env['barcode.configuration.template'].search([('select_default', '=', True)])
        if not template:
            template = self.env['barcode.configuration.template'].search([], limit=1)
            if not template:
                raise ValidationError(_('Please Create Product Label Template From: Sales --> Configuration --> Barcode Configuration Template'))
        return template.id if template else False

    product_lines = fields.One2many('product.label.line', 'wizard_id', string='Products')
    barcode_template = fields.Many2one('barcode.configuration.template', string="Select Template",
                                       required=True, default=_get_default_barcode_template)

    @api.model
    def create_report_format(self, barcode_config):
        report_action_id = self.env['ir.actions.report'].sudo().search([('report_name', '=', 'ca_barcode_labels.report_product_label')])
        if not report_action_id:
            raise ValidationError(_('Deleted Reference View Of Report, Please Update Module.'))

        self._cr.execute(""" DELETE FROM report_paperformat WHERE name='Dynamic Product Barcode Paper Format' """)
        paperformat_id = self.env['report.paperformat'].sudo().create({
            'custom_report': True,
            'name': 'Dynamic Product Barcode Paper Format',
            'format': 'custom',
            'header_spacing': barcode_config.header_spacing or 1,
            'orientation': 'Portrait',
            'dpi': barcode_config.dpi or 90,
            'page_height': barcode_config.label_height or 10,
            'page_width': barcode_config.label_width or 10,
            'margin_bottom': barcode_config.margin_bottom or 1,
            'margin_top': barcode_config.margin_top or 1,
            'margin_left': barcode_config.margin_left or 1,
            'margin_right': barcode_config.margin_right or 1,
        })
        report_action_id.sudo().write({'paperformat_id': paperformat_id.id})
        return True

    @api.model
    def default_get(self, fields):
        return_dict = {}
        product_lines = []
        active_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model')

        barcode_template = self.env['barcode.configuration.template'].search([('select_default', '=', True)], limit=1)
        if not barcode_template:
            barcode_template = self.env['barcode.configuration.template'].search([], limit=1)
            if not barcode_template:
                raise ValidationError(_('Please Create Product Label Template From: Sales --> Configuration --> Barcode Configuration Template'))

        return_dict.update({'barcode_template': barcode_template.id})
        if active_ids and active_model:

            if active_model == 'product.template':
                for template in self.env['product.template'].browse(active_ids):
                    product_lines += [(0, 0, {'product_id': product.id, 'qty': 1.0}) for product in template.product_variant_ids]
            elif active_model == 'product.product':
                products = self.env['product.product'].browse(active_ids)
                product_lines = [(0, 0, {'product_id': product.id, 'qty': 1.0}) for product in products]
            elif active_model == 'stock.picking':
                for picking in self.env['stock.picking'].browse(active_ids):
                    for line in picking.move_lines:
                        if line.product_id and line.product_id.type != 'service':
                            order_qty = int(abs(line.product_qty)) or 1.0
                            if barcode_template.default_qty_labels and barcode_template.default_qty_labels == 'one_qty':
                                order_qty = 1.0
                            product_lines += [(0, 0, {'product_id': line.product_id.id, 'qty': order_qty})]
            elif active_model == 'sale.order':
                for so in self.env['sale.order'].browse(active_ids):
                    for line in so.order_line:
                        if line.product_id and line.product_id.type != 'service':
                            order_qty = int(abs(line.product_uom_qty)) or 1.0
                            if barcode_template.default_qty_labels and barcode_template.default_qty_labels == 'one_qty':
                                order_qty = 1.0
                            product_lines += [(0, 0, {'product_id': line.product_id.id, 'qty': order_qty})]
            elif active_model == 'purchase.order':
                for po in self.env['purchase.order'].browse(active_ids):
                    for line in po.order_line:
                        if line.product_id and line.product_id.type != 'service':
                            order_qty = int(abs(line.product_qty)) or 1.0
                            if barcode_template.default_qty_labels and barcode_template.default_qty_labels == 'one_qty':
                                order_qty = 1.0
                            product_lines += [(0, 0, {'product_id': line.product_id.id, 'qty': order_qty})]
            return_dict.update({'product_lines': product_lines})

            view_id = self.env['ir.ui.view'].search([('name', '=', 'report_product_label')])
            if not view_id.arch:
                raise ValidationError(_('Deleted Reference View Of Report, Please Update Module.'))
        return return_dict

    def print_product_barcode_label(self):
        if not self.env.user.has_group('ca_barcode_labels.group_allow_barcode_labels'):
            raise ValidationError(_("You Have Insufficient Access Rights"))
        if not self.product_lines:
            raise ValidationError(_(""" No Product Lines To Print."""))
        qty_set_one = False

        if self.barcode_template.default_qty_labels and self.barcode_template.default_qty_labels == 'one_qty':
            qty_set_one = True

        product_ids = []
        for line in self.product_lines:
            product_ids.append({
                'product_id': line.product_id.id,
                'lot_id': line.lot_id and line.lot_id.id or False,
                'lot_number': line.lot_id and line.lot_id.name or False,
                'qty': qty_set_one and 1.0 or line.qty,
            })

        datas = {
            'barcode_template': self.barcode_template.id,
            'ids': [x.product_id.id for x in self.product_lines],
            'model': 'product.product',
            'product_ids': product_ids,
            'symbol': self.barcode_template.currency_id.symbol if self.barcode_template.currency_id else self.env.user.company_id.currency_id.symbol
        }
        product_list = [x.product_id for x in self.product_lines]
        for product in product_list:
            barcode_value = product[self.barcode_template.barcode_field]
            if not barcode_value:
                raise ValidationError(_('Please define barcode for %s!' % (product['name'])))
            try:
                barcode.createBarcodeDrawing(self.barcode_template.barcode_type, value=barcode_value, format='png',
                                             width=int(self.barcode_template.barcode_height),
                                             height=int(self.barcode_template.barcode_width),
                                             humanReadable=self.barcode_template.humanreadable or False)
            except:
                raise ValidationError(_('Select valid barcode type according barcode field value or check value in field!'))

        self.sudo().create_report_format(self.barcode_template)
        return self.env.ref('ca_barcode_labels.product_dynamic_labels').report_action([], data=datas)


class ProductLabelLine(models.TransientModel):
    _name = 'product.label.line'

    qty = fields.Integer('Barcode Labels Qty', default=1, required=True)
    wizard_id = fields.Many2one('product.label', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Production Lot')

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if not self.lot_id:
            return {}
        self.qty = self.lot_id.product_qty or 0.0

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {}
        return {'domain': {'lot_id': [('product_id', '=', self.product_id.id)]}, }


class ReportProductLabel(models.AbstractModel):
    _name = 'report.ca_barcode_labels.report_product_label'

    def check_hr(self, barcode_config):
        return barcode_config.humanreadable and 1 or 0

    @api.model
    def _get_report_values(self, docids, data=None):
        # if not data.get('form'):
        #     raise UserError(_("Form content is missing, this report cannot be printed."))
        barcode_config = self.env['barcode.configuration.template'].search([('id', '=', data.get('barcode_template'))])
        if not barcode_config:
            raise ValidationError(_(" Please configure barcode data from configuration menu"))
        docs = []

        if barcode_config.barcode_field:
            barcode_field = barcode_config.barcode_field
        else:
            barcode_field = 'name'
        for rec in data['product_ids']:
            for loop in range(0, int(rec['qty'])):
                product = self.env['product.product'].browse(int(rec['product_id']))
                barcode_value = getattr(product, barcode_field, '')
                docs.append((product, rec['lot_number'], product.name_get()[0][1], barcode_value))
        return {
            'is_humanreadable': self.check_hr(barcode_config),
            'docs': docs,
            'barcode_config': barcode_config,
            'data': data,
        }
