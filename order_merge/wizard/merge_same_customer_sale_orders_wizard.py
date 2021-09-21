# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
import copy


class MergeSameCustomerSaleOrder(models.TransientModel):
    _name = 'merge.same.customer.sale.order.wizard'
    _description = 'Merge Same Customer Sale orders'

    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_order = fields.Many2one(
        'sale.order', 'Merge into')
    sale_order_to_merge = fields.Many2many(
        'sale.order',
        string='Orders to merge')
    type = fields.Selection(
        [('new', 'New Order and Cancel Selected'), ('exist', 'New order and Delete all selected order'),
         ('exist_1', 'Merge order on existing selected order and cancel others'),
         ('exist_2', 'Merge order on existing selected order and delete others')], 'Merge Type', default='new',
        required=True)

    @api.onchange('partner_id')
    def update_so_list(self):
        if self.partner_id:
            orders = self.env['sale.order'].search([('partner_id','=',self.partner_id.id),('state','=', 'draft')])
            self.sale_order_to_merge = orders

    @api.onchange('sale_order_to_merge')
    def update_so_value(self):
        if self.partner_id:
            self.sale_order = False



    def merge_same_customer_sale_orders(self):
        sale_obj = self.env['sale.order']
        mod_obj = self.env['ir.model.data']
        line_obj = self.env['sale.order.line']
        action = mod_obj.xmlid_to_object('stock.stock_picking_action_picking_type')
        form_view_id = mod_obj.xmlid_to_res_id('sale.view_order_form')
        sales = sale_obj.browse(self.sale_order_to_merge.ids)
        partners_list = []
        partners_list_write = []
        line_list = []
        cancel_list = []
        copy_list = []
        vals = {}
        customer_ref = []
        partner_name = False
        myString = ''
        new_sale = False
        if len(sales) < 2:
            raise UserError('Please select multiple orders to merge in the list view.')

        if any(sale.state in ['done', 'sale', 'confirmed', 'cancel'] for sale in sales):
            raise UserError('You can not merge Done and Sale order orders.')
        for sale in sales:
            if sale.client_order_ref:
                customer_ref.append(sale.client_order_ref)
                if len(customer_ref) > 1:
                    myString = ",".join(customer_ref)
                else:
                    myString = customer_ref[0]

        msg_origin = ""
        origin_list = []

        for sale in sales:
            origin_list.append(sale.name)
        if self.sale_order:
            origin_list.append(self.sale_order.name)

        if len(origin_list) == 1:
            msg_origin = msg_origin + origin_list[0] + "."
        elif len(origin_list) > 1:
            msg_origin = ', '.join(set(origin_list))

        if self.sale_order:
            self.sale_order.write({'client_order_ref': myString})
        if self.type == 'new':
            partner_name = sales and sales[0].partner_id.id
            new_sale = sale_obj.create(
                {'partner_id': partner_name, 'client_order_ref': myString, 'origin': msg_origin, 'state': 'draft'})
            for sale in sales:
                partners_list.append(sale.partner_id)
                if not partners_list[1:] == partners_list[:-1]:
                    raise UserError('You can only merge orders of same partners.')

                else:
                    cancel_list.append(sale)
                    merge_ids = line_obj.search([('order_id', '=', sale.id)])
                    for line in merge_ids:
                        vals = {
                            'product_id': line.product_id.id or False,
                            'product_uom_qty': line.product_uom_qty or False,
                            'price_unit': line.price_unit or False,
                            'tax_id': [(6, 0, [tax.id for tax in line.tax_id if line.tax_id])] or False,
                            'order_id': new_sale.id,
                        }
                        line_obj.create(vals)
            msg_body = _("This sale order has been created from: <b>%s</b>") % (msg_origin)
            new_sale.message_post(body=msg_body)
            new_sale.write({'partner_id': partner_name})
            for orders in cancel_list:
                orders.action_cancel()
        if self.type == 'exist':
            partner_name = sales and sales[0].partner_id.id
            new_sale = sale_obj.create(
                {'partner_id': partner_name, 'client_order_ref': myString, 'origin': msg_origin, 'state': 'draft'})
            for sale in sales:
                partners_list_write.append(sale.partner_id)

                if not partners_list_write[1:] == partners_list_write[:-1]:
                    raise UserError('You can only merge orders of same partners.')

                else:
                    cancel_list.append(sale)
                    merge_ids = line_obj.search([('order_id', '=', sale.id)])
                    for line in merge_ids:
                        vals = {
                            'product_id': line.product_id.id or False,
                            'product_uom_qty': line.product_uom_qty or False,
                            'price_unit': line.price_unit or False,
                            'tax_id': [(6, 0, [tax.id for tax in line.tax_id if line.tax_id])] or False,
                            'order_id': new_sale.id,
                        }
                        line_obj.create(vals)
            msg_body = _("This sale order has been created from: <b>%s</b>") % (msg_origin)
            new_sale.message_post(body=msg_body)
            new_sale.write({'partner_id': partner_name})

            for orders in cancel_list:
                orders.action_cancel()
            for orders in cancel_list:
                orders.unlink()

        if self.type == 'exist_1':
            for sale in sales:
                partners_list_write.append(sale.partner_id)
                partners_list_write.append(self.sale_order.partner_id)
                cancel_list.append(sale.id)

                user = partners_list_write
                set1 = set(partners_list_write)
                if len(set1) > 1:
                    raise UserError('You can only merge orders of same partners.')
                else:
                    partner_name = sale.partner_id.id
                    merge_ids = line_obj.search([('order_id', '=', sale.id)])
                    for line in merge_ids:
                        if self.sale_order.state in ['done', 'sale', 'confirmed', 'cancel']:
                            raise UserError('You can not merge oredrs with Done, Cancel and Sale order orders.')
                        else:
                            if sale.id != self.sale_order.id:
                                vals = {
                                    'product_id': line.product_id.id or False,
                                    'product_uom_qty': line.product_uom_qty or False,
                                    'price_unit': line.price_unit or False,
                                    'tax_id': [(6, 0, [tax.id for tax in line.tax_id if line.tax_id])] or False,
                                    'order_id': self.sale_order.id,
                                }
                                line_obj.create(vals)

            msg_body = _("This sale order has been created from: <b>%s</b>") % (msg_origin)
            self.sale_order.message_post(body=msg_body)
            self.sale_order.write({'partner_id': partner_name, 'origin': msg_origin})

            if self.sale_order.id in cancel_list:
                cancel_list.remove(self.sale_order.id)

            for orders in cancel_list:
                for s_order in self.env['sale.order'].browse(orders):
                    s_order.action_cancel()

        if self.type == 'exist_2':
            for sale in sales:
                partners_list_write.append(sale.partner_id)
                partners_list_write.append(self.sale_order.partner_id)
                cancel_list.append(sale.id)

                user = partners_list_write
                set1 = set(partners_list_write)

                if len(set1) > 1:
                    raise UserError('You can only merge orders of same partners.')
                else:
                    partner_name = sale.partner_id.id
                    if self.sale_order.state in ['done', 'sale', 'confirmed', 'cancel']:
                        raise UserError('You can not merge orders with Done, Cancel and Sale order orders.')
                    else:
                        merge_ids = line_obj.search([('order_id', '=', sale.id)])
                        for line in merge_ids:
                            line.write({
                                'order_id': self.sale_order.id
                            })

            msg_body = _("This sale order has been created from: <b>%s</b>") % (msg_origin)
            self.sale_order.message_post(body=msg_body)
            self.sale_order.write({'partner_id': partner_name, 'origin': msg_origin})

            if self.sale_order.id in cancel_list:
                cancel_list.remove(self.sale_order.id)

            for orders in cancel_list:
                for s_order in self.env['sale.order'].browse(orders):
                    s_order.action_cancel()
                    s_order.unlink()

        result = {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
        }
        return result

