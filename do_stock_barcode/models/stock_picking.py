# -*- coding: utf-8 -*-

# from odoo import _, models
from odoo import _, api, fields, models


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'barcodes.barcode_events_mixin']

    product_barcode_scan = fields.Char(string='Barcode')

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search(
            ['|', ('barcode', '=', barcode), ('default_code', '=', barcode)], limit=1)
        if product:
            moveLines = self.move_ids_without_package.filtered(
                lambda r: r.product_id == product)
            for line in moveLines:
                line.quantity_done = line.move_line_ids.qty_done + 1
                self.env.cr.commit()
                return {'warning': {'title': _('Successfully Added'),
                                    'message': _(' %s - %s/%s.') % (product.name,  line.quantity_done,  line.product_uom_qty)
                                    },
                        }

            else:
                return {'warning': {'title': _('User Error'),
                                    'message': _('This product %s with barcode %s is not present in this picking.') % (product.name, barcode)},
                        }
            return
        else:
            return {'warning': {'title': _('User Error'),
                                'message': _('This barcode %s is not related to any product.') % barcode},
                    }

    @api.onchange('product_barcode_scan')
    def onchange_product_barcode_scan(self):
        barcode = self.product_barcode_scan
        if barcode:
            self.product_barcode_scan = ''
            return self.on_barcode_scanned(barcode)
        else:
            self.product_barcode_scan = ''
            pass
