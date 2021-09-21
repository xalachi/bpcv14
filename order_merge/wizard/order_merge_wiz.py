# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
import copy


class SaleOrderMerge(models.TransientModel):
    _name = 'sale.order.merge'
    _description = 'Merge Sale orders'

    sale_order_to_merge = fields.Many2many(
        'sale.order', 'rel_sale_to_merge', 'sale_id', 'to_merge_id',
        string='Orders to merge')
    type = fields.Selection(
        [('new', 'New Order and Cancel Selected'), ('exist', 'New order and Delete all selected order'),
         ('exist_1', 'Merge order on existing selected order and cancel others'),
         ('exist_2', 'Merge order on existing selected order and delete others')], 'Merge Type', default='new',
        required=True)
    sale_order = fields.Many2one('sale.order', string='Merge with')
    merge_with_diff_partner = fields.Boolean(
        string='Merge with Different Customer')
    partner_id = fields.Many2one(
        'res.partner', 'Customer')

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrderMerge, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        if active_ids:
            sale_ids = []
            sales = self.env['sale.order'].browse(active_ids)

            if any(sale.state == 'done' for sale in sales):
                raise UserError('You can not merge done orders.')

            sale_ids = [sale.id for sale in sales]

            if 'sale_order_to_merge' in fields:
                rec.update({'sale_order_to_merge': [(6, 0, sale_ids)]})
        return rec

    @api.onchange('merge_with_diff_partner')
    def set_data(self):
        if self.merge_with_diff_partner:
            self.sale_order = False
            self.type = 'new'
        elif not self.merge_with_diff_partner:
            self.partner_id = False



    def merge_sale(self):
        sale_obj = self.env['sale.order']
        mod_obj = self.env['ir.model.data']
        line_obj = self.env['sale.order.line']
        action = mod_obj.xmlid_to_object('stock.stock_picking_action_picking_type')
        form_view_id = mod_obj.xmlid_to_res_id('sale.view_order_form')
        sales = sale_obj.browse(self._context.get('active_ids', []))
        partners_list = []
        partners_list_write = []
        line_list = []
        cancel_list = []
        copy_list = []
        vals = {}
        customer_ref = []
        partner_name = False
        myString = ''

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

        if not self.merge_with_diff_partner:
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
                return True

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
        else:
            partner_name = self.partner_id.id
            new_sale = sale_obj.create(
                {'partner_id': partner_name, 'client_order_ref': myString, 'origin': msg_origin, 'state': 'draft'})
            for sale in sales:
                partners_list.append(sale.partner_id)
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

        result = {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
        }
        return result


class PurchaseOrderMerge(models.TransientModel):
    _name = 'purchase.order.merge'
    _description = 'Merge Purchase orders'

    purchase_order = fields.Many2one(
        'purchase.order', 'Merge into')
    purchase_order_to_merge = fields.Many2many(
        'purchase.order', 'rel_purchase_to_merge', 'purchase_id', 'to_merge_id',
        'Orders to merge')
    type = fields.Selection(
        [('new', 'New Order and Cancel Selected'), ('exist', 'New order and Delete all selected order'),
         ('exist_1', 'Merge order on existing selected order and cancel others'),
         ('exist_2', 'Merge order on existing selected order and delete others')], 'Merge Type', default='new',
        required=True)
    merge_with_diff_partner = fields.Boolean(
        string='Merge with Different Partner')
    partner_id = fields.Many2one(
        'res.partner', 'Vendor')

    @api.model
    def default_get(self, fields):
        rec = super(PurchaseOrderMerge, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        if active_ids:
            purchase_ids = []
            purchases = self.env['purchase.order'].browse(active_ids)

            if any(pur.state == 'done' for pur in purchases):
                raise UserError('You can not merge done orders.')

            purchase_ids = [pur.id for pur in purchases]

            if 'purchase_order_to_merge' in fields:
                rec.update({'purchase_order_to_merge': [(6, 0, purchase_ids)]})
        return rec

    @api.onchange('merge_with_diff_partner')
    def set_data(self):
        if self.merge_with_diff_partner:
            self.purchase_order = False
            self.type = 'new'
        elif not self.merge_with_diff_partner:
            self.partner_id = False


    def merge_purchase(self):
        purchase_obj = self.env['purchase.order']
        mod_obj = self.env['ir.model.data']
        line_obj = self.env['purchase.order.line']
        form_view_id = mod_obj.xmlid_to_res_id('purchase.purchase_order_form')
        purchases = purchase_obj.browse(self._context.get('active_ids', []))
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

        if not self.merge_with_diff_partner:
            if self.purchase_order:
                self.purchase_order.write({'partner_ref': myString})
            if self.type == 'new':
                partner_name = purchases and purchases[0].partner_id.id
                new_purchase = purchase_obj.create(
                    {'partner_id': partner_name, 'partner_ref': myString or '', 'state': 'draft'})
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
                partner_name = purchases and purchases[0].partner_id.id
                new_purchase = purchase_obj.create(
                    {'partner_id': partner_name, 'partner_ref': myString or '', 'state': 'draft'})
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

        else:
            partner_name = self.partner_id.id
            new_purchase = purchase_obj.create(
                {'partner_id': partner_name, 'partner_ref': myString or '', 'state': 'draft'})
            for pur in purchases:
                partners_list.append(pur.partner_id)
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

        result = {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
        }
        return result
    
