# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
import copy

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order Inherit'

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            for rec in self:
                if rec.state == 'draft':
                    order_lines = self.auto_merge()
                    vals['order_line'] = [(6, 0, [i.id for i in set(order_lines)])]
                    res = super(SaleOrder, self).write(vals)
                else:
                    pass

        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            order_new_lines = []
            if res.state == 'draft':
                for order in res.order_line:
                    if order.product_id not in [i.product_id for i in order_new_lines]:
                        order_new_lines.append(order)
                    elif order.product_id in [i.product_id for i in order_new_lines]:
                        a = [order_new_lines.index(i) for i in order_new_lines if
                             (i.product_id == order.product_id) and (i.price_unit == order.price_unit)]
                        print(a)
                        if len(a) == 1:
                            order_new_lines[a[0]].product_uom_qty += order.product_uom_qty
                            order_new_lines[a[0]].tax_id += order.tax_id
                        else:
                            order_new_lines.append(order)

                res.order_line = [(6, 0, [i.id for i in set(order_new_lines)])]
            else:
                pass
        return res


    def action_confirm(self):
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            for rec in self:
                if rec.state == 'draft':
                    order_lines = self.auto_merge()
                    rec.order_line = [(6, 0, [i.id for i in set(order_lines)])]
            res = super(SaleOrder, self).action_confirm()
        else:
            res = super(SaleOrder, self).action_confirm()
        return res

    def action_quotation_send(self):
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            for rec in self:
                if rec.state == 'draft':
                    order_lines = self.auto_merge()
                    rec.order_line = [(6, 0, [i.id for i in set(order_lines)])]
            res = super(SaleOrder, self).action_quotation_send()
        else:
            res = super(SaleOrder, self).action_quotation_send()
        return res

    def auto_merge(self):
        order_new_lines = []
        for rec in self:
            if rec.state == 'draft':
                for order in rec.order_line:
                    if order.product_id not in [i.product_id for i in order_new_lines]:
                        order_new_lines.append(order)
                    elif order.product_id in [i.product_id for i in order_new_lines]:
                        a = [order_new_lines.index(i) for i in order_new_lines if
                             (i.product_id == order.product_id) and (i.price_unit == order.price_unit)]
                        print(a)
                        if len(a) == 1:
                            order_new_lines[a[0]].product_uom_qty += order.product_uom_qty
                            order_new_lines[a[0]].tax_id += order.tax_id
                        else:
                            order_new_lines.append(order)
                return set(order_new_lines)