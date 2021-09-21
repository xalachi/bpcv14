# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
import copy


class MergeSameVendorPurchaseOrder(models.TransientModel):
    _name = 'merge.same.vendor.purchase.order.wizard'
    _description = 'Merge Same Vendor Purchase orders'

    partner_id = fields.Many2one('res.partner', string='Vendor')
    purchase_order = fields.Many2one(
        'purchase.order', 'Merge into')
    purchase_order_to_merge = fields.Many2many(
        'purchase.order',
        string='Orders to merge')
    type = fields.Selection(
        [('new', 'New Order and Cancel Selected'), ('exist', 'New order and Delete all selected order'),
         ('exist_1', 'Merge order on existing selected order and cancel others'),
         ('exist_2', 'Merge order on existing selected order and delete others')], 'Merge Type', default='new',
        required=True)

    @api.onchange('partner_id')
    def update_po_list(self):
        if self.partner_id:
            orders = self.env['purchase.order'].search([('partner_id','=',self.partner_id.id),('state','=', 'draft')])
            self.purchase_order_to_merge = orders

    @api.onchange('purchase_order_to_merge')
    def update_po_value(self):
        if self.partner_id:
            self.purchase_order = False



    def merge_same_vendor_purchase_orders(self):
        purchase_obj = self.env['purchase.order']
        mod_obj = self.env['ir.model.data']
        line_obj = self.env['purchase.order.line']
        form_view_id = mod_obj.xmlid_to_res_id('purchase.purchase_order_form')
        purchases = purchase_obj.browse(self.purchase_order_to_merge.ids)
        partners_list = []
        partners_list_write = []
        line_list = []
        cancel_list = []
        copy_list = []
        vendor_ref = []
        myString = ''
        new_purchase = False
        if len(purchases) < 2:
            raise UserError('Please select multiple orders to merge in the list view.')

        if any(pur.state in ['done', 'purchase', 'cancel'] for pur in purchases):
            raise UserError('You can not merge this order with existing state.')
        for pur in purchases:
            if pur.partner_ref:
                vendor_ref.append(pur.partner_ref)
                if len(vendor_ref) > 1:
                    myString = ",".join(vendor_ref)
                else:
                    myString = vendor_ref[0]

        msg_origin = ""
        origin_list = []

        for pur in purchases:
            origin_list.append(pur.name)
        if self.purchase_order:
            origin_list.append(self.purchase_order.name)

        if len(origin_list) == 1:
            msg_origin = msg_origin + origin_list[0] + "."
        elif len(origin_list) > 1:
            msg_origin = ', '.join(set(origin_list))

        for pur in purchases:
            origin_list.append(pur.name)

        if self.purchase_order:
            self.purchase_order.write({'partner_ref': myString})
        if self.type == 'new':
            partner_name = self.partner_id.id
            new_purchase = purchase_obj.create({'partner_id': partner_name, 'partner_ref': myString or '','state': 'draft'})
            for pur in purchases:
                partners_list.append(pur.partner_id)

                if not partners_list[1:] == partners_list[:-1]:
                    raise UserError('You can only merge orders of same partners.')

                else:
                    cancel_list.append(pur)
                    merge_ids = line_obj.search([('order_id', '=', pur.id)])
                    for line in merge_ids:
                        vals = {
                            'date_planned': line.date_planned or False,
                            'name': line.product_id.name or False,
                            'product_id': line.product_id.id or False,
                            'product_qty': line.product_qty or False,
                            'product_uom': line.product_uom.id or False,
                            'price_unit': line.price_unit or False,
                            'taxes_id': [(6, 0, [tax.id for tax in line.taxes_id if line.taxes_id])] or False,
                            'order_id': new_purchase.id,
                        }
                        line_obj.create(vals)

            msg_body = _("This purchases order has been created from: <b>%s</b>") % (msg_origin)
            new_purchase.message_post(body=msg_body)
            new_purchase.write({'partner_id': partner_name})

            for orders in cancel_list:
                orders.button_cancel()
        if self.type == 'exist':
            partner_name = self.partner_id.id
            new_purchase = purchase_obj.create({'partner_id': partner_name, 'partner_ref': myString or '','state': 'draft'})
            for pur in purchases:
                partners_list_write.append(pur.partner_id)

                if not partners_list_write[1:] == partners_list_write[:-1]:
                    raise UserError('You can only merge orders of same partners.')

                else:
                    partner_name = pur.partner_id.id
                    cancel_list.append(pur)
                    merge_ids = line_obj.search([('order_id', '=', pur.id)])
                    for line in merge_ids:
                        vals = {
                            'date_planned': line.date_planned or False,
                            'name': line.product_id.name or False,
                            'product_id': line.product_id.id or False,
                            'product_qty': line.product_qty or False,
                            'product_uom': line.product_uom.id or False,
                            'price_unit': line.price_unit or False,
                            'taxes_id': [(6, 0, [tax.id for tax in line.taxes_id if line.taxes_id])] or False,
                            'order_id': new_purchase.id,
                        }
                        line_obj.create(vals)

            msg_body = _("This purchases order has been created from: <b>%s</b>") % (msg_origin)
            new_purchase.message_post(body=msg_body)
            new_purchase.write({'partner_id': partner_name})

            for orders in cancel_list:
                orders.button_cancel()
            for orders in cancel_list:
                orders.unlink()

        if self.type == 'exist_1':
            for pur in purchases:
                partners_list_write.append(pur.partner_id)
                partners_list_write.append(self.purchase_order.partner_id)
                cancel_list.append(pur.id)

                user = partners_list_write
                set1 = set(partners_list_write)
                if len(set1) > 1:
                    raise UserError('You can only merge orders of same partners.')
                else:
                    partner_name = pur.partner_id.id
                    merge_ids = line_obj.search([('order_id', '=', pur.id)])
                    for line in merge_ids:
                        line.write({'order_id': self.purchase_order.id})

            msg_body = _("This purchases order has been created from: <b>%s</b>") % (msg_origin)
            self.purchase_order.message_post(body=msg_body)
            self.purchase_order.write({'partner_id': partner_name})

            if self.purchase_order.id in cancel_list:
                cancel_list.remove(self.purchase_order.id)
            for orders in cancel_list:
                for s_order in self.env['purchase.order'].browse(orders):
                    s_order.button_cancel()
            return True

        if self.type == 'exist_2':
            for pur in purchases:
                partners_list_write.append(pur.partner_id)
                partners_list_write.append(self.purchase_order.partner_id)
                cancel_list.append(pur.id)

                user = partners_list_write
                set1 = set(partners_list_write)
                if len(set1) > 1:
                    raise UserError('You can only merge orders of same partners.')
                else:
                    partner_name = pur.partner_id.id
                    merge_ids = line_obj.search([('order_id', '=', pur.id)])
                    for line in merge_ids:
                        if self.purchase_order.state in ['done', 'purchase', 'to approve', 'cancel']:
                            raise UserError('You can not merge oredrs with Done, Cancel and Purchase order orders.')
                        else:
                            line.write({'order_id': self.purchase_order.id})

            msg_body = _("This purchases order has been created from: <b>%s</b>") % (msg_origin)
            self.purchase_order.message_post(body=msg_body)
            self.purchase_order.write({'partner_id': partner_name})

            if self.purchase_order.id in cancel_list:
                cancel_list.remove(self.purchase_order.id)
            for orders in cancel_list:
                p_order = self.env['purchase.order'].browse(orders)
                p_order.button_cancel()
                p_order.unlink()

        result = {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
        }
        return result

