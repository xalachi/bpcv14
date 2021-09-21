# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
import copy


class SaleOrderLineMerge(models.TransientModel):
    _name = 'sale.orderline.merge.wizard'
    _description = 'Sale Orderline Merge'

    def merge_orderlines(self):
        active_id = self._context.get('active_id')
        sale_order = self.env['sale.order'].search([('id', '=', active_id)])
        order_new_lines = []
        exists = []

        for rec in sale_order:
            if rec.state != 'draft':
                raise ValidationError('Operation can only be perform when the sale order is in Quatation only')
            else:
                for order in sale_order.order_line:
                    if order.product_id not in [i.product_id for i in order_new_lines]:
                        order_new_lines.append(order)
                    elif order.product_id in [i.product_id for i in order_new_lines]:
                        a = [order_new_lines.index(i) for i in order_new_lines if (i.product_id == order.product_id) and (i.price_unit == order.price_unit)]
                        print(a)
                        if len(a) == 1:
                            order_new_lines[a[0]].product_uom_qty += order.product_uom_qty
                            order_new_lines[a[0]].tax_id += order.tax_id
                        else:
                            order_new_lines.append(order)

        sale_order.order_line = [(6, 0, [i.id for i in set(order_new_lines)])]

        return

