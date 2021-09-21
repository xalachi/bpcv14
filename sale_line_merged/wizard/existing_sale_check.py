# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleLineWiz(models.TransientModel):
    _name = 'sale.line.wiz'
    _description = 'Line'

    product_id = fields.Many2one("product.product")
    qty = fields.Float()
    sline_id = fields.Many2one('sale.order.line')
    existing_sale_final_id = fields.Many2one('existing.sale.final')


class ExistingsaleFinal(models.TransientModel):
    _name = 'existing.sale.final'
    _description = 'Sale Line Final wizard'

    sale_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
    order_line = fields.One2many("sale.line.wiz", 'existing_sale_final_id')
    error_message = fields.Char()
    
    def action_sale_yes(self):
        self.ensure_one()
        sale = self.sale_id
        order_line = self.env['sale.order.line'].search([('order_id','=',sale.id)])
        line_dict = {}
        for a in order_line:
            if a.product_id.id not in line_dict:
                line_dict[a.product_id.id]= [a.product_uom_qty]
            else:
                line_dict[a.product_id.id].append(a.product_uom_qty)
        order_line.unlink()
        for i in line_dict:
            order_list = {
                'product_id':i,
                'product_uom_qty':sum(line_dict[i]),
                'order_id': sale.id,
            }
            sale_line = self.env['sale.order.line'].create(order_list)
