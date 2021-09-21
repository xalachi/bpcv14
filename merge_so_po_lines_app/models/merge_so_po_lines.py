# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

def ListCalculation(lists):
    result = {}
    for card,value in lists:
        total = result.get(card,0) + value
        result[card] = total
    return list(result.items())

class MergeSaleLine(models.TransientModel):
    _name="merge.sale.line"
    _description = "Merge Sale Line"
    

    def merge(self):
        line_obj = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for record in line_obj:
            if not record.order_line:
                raise UserError(_('Please add product on sale order.'))
        product_list = []
        same_product = []
        final_list = []
        no_duplicate = []
        qty = 0.0
        if all(child.state != 'draft' for child in line_obj):
            raise UserError(_('You cannot not merge sale order in "Confirm" Stage'))

        for record in line_obj.filtered(lambda r: r.state == 'draft'):
            for product in record.order_line:
                product_list.append([product.product_id.id,product.product_uom_qty])
        same_product = ListCalculation(product_list)
        for val in same_product:
            final_list.append(list(val))
        for record in line_obj.filtered(lambda r: r.state == 'draft'):
            for product in record.order_line:
                for val in final_list:
                    if val[0] == product.product_id.id:
                        if product.product_id.id not in no_duplicate:
                            no_duplicate.append(product.product_id.id)
                            if product.product_id:
                                product.copy(default={'product_uom_qty': val[1],'order_id' : product.order_id.id})  
                product.unlink()

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):

        res = super(SaleOrder, self).create(vals)

        if self.env['ir.config_parameter'].sudo().get_param('merge_so_po_lines_app.auto_merge_so_line'):
            product_list = []
            same_product = []
            final_list = []
            no_duplicate = []
            qty = 0.0
            for product in res.order_line:
                product_list.append([product.product_id.id,product.product_uom_qty])
            same_product = ListCalculation(product_list)
            for val in same_product:
                final_list.append(list(val))
            for product in res.order_line:
                for val in final_list:
                    if val[0] == product.product_id.id:
                        if product.product_id.id not in no_duplicate:
                            no_duplicate.append(product.product_id.id)
                            product.copy(default={'product_uom_qty': val[1],'order_id' : product.order_id.id})  
                product.unlink()
            return res
        else:
            return res


    def write(self, vals):
        if self.env['ir.config_parameter'].sudo().get_param('merge_so_po_lines_app.auto_merge_so_line'):
            new_products={}
            edited_products={}
            existed_products={}
            section_list=[]
            if "order_line" in vals.keys():
                so_line_list = vals['order_line']
                for line in so_line_list:
                    
                    #new products
                    if line[0] == 0:
                        if line[2]['product_id'] == False:
                            section_list.append([0,0,
                                {
                                    'discount': 0,
                                    'product_uom': False,
                                    'product_no_variant_attribute_value_ids': [[6, False, []]],
                                    'analytic_tag_ids': [[6, False, []]],
                                    'qty_delivered_manual': 0,
                                    'sequence': line[2]['sequence'],
                                    'name':line[2]['name'],
                                    'price_unit': 0,
                                    'display_type': line[2]['display_type'],
                                    'tax_id': [[6, False, []]],
                                    'product_id': False,
                                    'product_uom_qty': 1,
                                    'qty_delivered': 0,
                                    'customer_lead': 0
                                }
                            ])

                        else:
                            if line[2]['product_id'] not in new_products:
                                new_products.update({
                                    line[2]['product_id'] : {
                                        'qty':line[2]['product_uom_qty'],
                                        'price':line[2]['price_unit']
                                    }  
                                })
                            else:                        
                                new_products[line[2]['product_id']]['qty'] += line[2]['product_uom_qty']
                                new_products[line[2]['product_id']]['price'] += line[2]['price_unit']

                    #replaced products
                    if line[0] == 1:
                        so_line = self.order_line.browse(line[1])
                        product_id = so_line.product_id.id
                        
                        if not product_id:
                            new_name = line[2]['name']
                            display_type = so_line.display_type
                            seq = so_line.sequence

                            section_list.append([0,0,
                                {
                                    'discount': 0,
                                    'product_uom': False,
                                    'product_no_variant_attribute_value_ids': [[6, False, []]],
                                    'analytic_tag_ids': [[6, False, []]],
                                    'qty_delivered_manual': 0,
                                    'sequence': seq,
                                    'name':new_name,
                                    'price_unit': 0,
                                    'display_type': display_type,
                                    'tax_id': [[6, False, []]],
                                    'product_id': False,
                                    'product_uom_qty': 1,
                                    'qty_delivered': 0,
                                    'customer_lead': 0
                                }
                            ])

                        else:
                            if product_id not in edited_products.keys():
                                edited_products.update({
                                    product_id:{}
                                })

                                if 'product_uom_qty' in line[2].keys():
                                    if 'qty' not in edited_products[product_id].keys():
                                        edited_products[product_id]['qty'] = line[2]['product_uom_qty']
                                else:
                                    edited_products[product_id]['qty'] = so_line.product_uom_qty

                                if 'price_unit' in line[2].keys():
                                    if 'price' not in edited_products[product_id].keys():
                                        edited_products[product_id]['price'] = line[2]['price_unit']
                                else:
                                    edited_products[product_id]['price'] = so_line.price_unit

                            else:
                                if 'product_uom_qty' in line[2].keys():
                                    if 'qty' in edited_products[product_id].keys():
                                        edited_products[product_id]['qty'] += line[2]['product_uom_qty']
                                    else:
                                        edited_products[product_id]['qty'] = line[2]['product_uom_qty']
                                else:
                                    edited_products[product_id]['qty'] += so_line.product_uom_qty

                                if 'price_unit' in line[2].keys():
                                    if 'price' in edited_products[product_id].keys():
                                        edited_products[product_id]['price'] += line[2]['price_unit']
                                    else:
                                        edited_products[product_id]['price'] = line[2]['price_unit']
                                else:
                                    edited_products[product_id]['price'] += so_line.price_unit

                    #existed products
                    if line[0] == 4:
                        so_line = self.order_line.browse(line[1])
                        product_id = so_line.product_id.id

                        if not product_id:
                            old_name = so_line.name
                            display_type = so_line.display_type
                            seq = so_line.sequence
                            
                            section_list.append([0,0,
                                {
                                    'discount': 0,
                                    'product_uom': False,
                                    'product_no_variant_attribute_value_ids': [[6, False, []]],
                                    'analytic_tag_ids': [[6, False, []]],
                                    'qty_delivered_manual': 0,
                                    'sequence': seq,
                                    'name':old_name,
                                    'price_unit': 0,
                                    'display_type': display_type,
                                    'tax_id': [[6, False, []]],
                                    'product_id': False,
                                    'product_uom_qty': 1,
                                    'qty_delivered': 0,
                                    'customer_lead': 0
                                }
                            ])

                        else:
                            if product_id not in existed_products.keys():
                                existed_products.update({
                                    product_id:{
                                        'qty':so_line.product_uom_qty,
                                        'price':so_line.price_unit
                                    }
                                })
                            else:
                                existed_products[product_id]['qty'] += so_line.product_uom_qty
                                existed_products[product_id]['price'] += so_line.price_unit

            id_set=set()
            if new_products:
                for ids in new_products:
                    id_set.add(ids)

            if existed_products:
                for ids in existed_products:
                    id_set.add(ids)

            if edited_products:
                for ids in edited_products:
                    id_set.add(ids)


            new_vals={}
            for product_id in id_set:

                if new_products:
                    if 'new' not in new_vals.keys():
                        new_vals['new'] = 'ok'

                        for ids in new_products:
                            if ids not in new_vals.keys():
                                new_vals.update({
                                    ids:{
                                        'product_id':ids,
                                        'qty':new_products[ids]['qty'],
                                        'price':new_products[ids]['price']
                                    }
                                })

                if edited_products:
                    if 'edited' not in new_vals.keys():
                        new_vals['edited'] = 'ok'

                        for ids in edited_products:
                            if ids not in new_vals.keys():
                                new_vals.update({
                                    ids:{
                                        'product_id':ids,
                                        'qty':edited_products[ids]['qty'],
                                        'price':edited_products[ids]['price']
                                    }
                                })
                            else:
                                new_vals[ids]['qty'] += edited_products[ids]['qty']
                                new_vals[ids]['price'] += edited_products[ids]['price']

                if existed_products:
                    if 'existed' not in new_vals.keys():
                        new_vals['existed'] = 'ok'

                        for ids in existed_products:
                            if ids not in new_vals.keys():
                                new_vals.update({
                                    ids:{
                                        'product_id':ids,
                                        'qty':existed_products[ids]['qty'],
                                        'price':existed_products[ids]['price']
                                    }
                                })
                            else:
                                new_vals[ids]['qty'] += existed_products[ids]['qty']
                                new_vals[ids]['price'] += existed_products[ids]['price']

            if 'new' in new_vals:
                new_vals.pop('new')
            if 'edited' in new_vals:
                new_vals.pop('edited')
            if 'existed' in new_vals:
                new_vals.pop('existed')
                            
            product_vals_list=[]
            for ids in new_vals:
                if new_vals[ids]['product_id']:
                    product_vals_list.append([
                        0, 0, {
                            'product_id':new_vals[ids]['product_id'],
                            'product_uom_qty':new_vals[ids]['qty'],
                            'price_unit':new_vals[ids]['price']
                        }
                    ])

            if section_list:
                for section in section_list:
                    product_vals_list.append(section)            

            if new_vals or section_list:
                if self.state == 'draft' or self.state == 'sent':
                    if "order_line" in vals.keys():
                        so_line_list = vals['order_line']

                        for line in so_line_list:
                            if line[0] == 1 or line[0] == 4:
                                self.order_line.browse(line[1]).unlink()
                    vals['order_line'] = product_vals_list

        res = super(SaleOrder, self).write(vals)
        return res

class MergePurchaseLine(models.TransientModel):
    _name="merge.purchase.line"
    

    def merge(self):
        line_obj = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        for record in line_obj:
            if not record.order_line:
                raise UserError(_('Please add product on purchase order.'))
        product_list = []
        same_product = []
        final_list = []
        no_duplicate = []
        qty = 0.0

        if all(child.state != 'draft' for child in line_obj):
            raise UserError(_('You cannot not merge purchase order in "Confirm" Stage'))

        for record in line_obj.filtered(lambda r: r.state == 'draft'):
            for product in record.order_line:
                product_list.append([product.product_id.id,product.product_qty])
        same_product = ListCalculation(product_list)
        for val in same_product:
            final_list.append(list(val))
        for record in line_obj.filtered(lambda r: r.state == 'draft'):
            for product in record.order_line:
                for val in final_list:
                    if val[0] == product.product_id.id:
                        if product.product_id.id not in no_duplicate:
                            no_duplicate.append(product.product_id.id)
                            if product.product_id:
                                product.copy(default={'product_qty': val[1],'order_id' : product.order_id.id})  
                if product.product_id:
                    product.unlink()

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if self.env['ir.config_parameter'].sudo().get_param('merge_so_po_lines_app.auto_merge_po_line'):
            product_list = []
            same_product = []
            final_list = []
            no_duplicate = []
            qty = 0.0
            for product in res.order_line:
                product_list.append([product.product_id.id,product.product_qty])
            same_product = ListCalculation(product_list)
            for val in same_product:
                final_list.append(list(val))
            for product in res.order_line:
                for val in final_list:
                    if val[0] == product.product_id.id:
                        if product.product_id.id not in no_duplicate:
                            no_duplicate.append(product.product_id.id)
                            product.copy(default={'product_qty': val[1],'order_id' : product.order_id.id})  
                product.unlink()
            return res
        else:
            return res


    def write(self, vals):
        if self.env['ir.config_parameter'].sudo().get_param('merge_so_po_lines_app.auto_merge_po_line'):
            new_products={}
            edited_products={}
            existed_products={}
            if "order_line" in vals.keys():
                so_line_list = vals['order_line']

                for line in so_line_list:

                    #new products
                    if line[0] == 0:
                        if line[2]['product_id'] not in new_products:
                            new_products.update({
                                line[2]['product_id'] : {
                                    'qty':line[2]['product_qty'],
                                    'price':line[2]['price_unit'],
                                    'name':line[2]['name'],
                                    'date_planned':line[2]['date_planned'],
                                    'product_uom':line[2]['product_uom']
                                }  
                            })
                        else:                        
                            new_products[line[2]['product_id']]['qty'] += line[2]['product_qty']
                            new_products[line[2]['product_id']]['price'] += line[2]['price_unit']

                    #replaced products
                    if line[0] == 1:
                        so_line = self.order_line.browse(line[1])
                        product_id = so_line.product_id.id
                        
                        if product_id not in edited_products.keys():
                            edited_products.update({
                                product_id:{
                                    'name':so_line.name,
                                    'date_planned':so_line.date_planned,
                                    'product_uom':so_line.product_uom.id
                                }
                            })

                            if 'product_qty' in line[2].keys():
                                if 'qty' not in edited_products[product_id].keys():
                                    edited_products[product_id]['qty'] = line[2]['product_qty']
                            else:
                                edited_products[product_id]['qty'] = so_line.product_qty

                            if 'price_unit' in line[2].keys():
                                if 'price' not in edited_products[product_id].keys():
                                    edited_products[product_id]['price'] = line[2]['price_unit']
                            else:
                                edited_products[product_id]['price'] = so_line.price_unit

                        else:
                            if 'product_qty' in line[2].keys():
                                if 'qty' in edited_products[product_id].keys():
                                    edited_products[product_id]['qty'] += line[2]['product_qty']
                                else:
                                    edited_products[product_id]['qty'] = line[2]['product_qty']
                            else:
                                edited_products[product_id]['qty'] += so_line.product_qty

                            if 'price_unit' in line[2].keys():
                                if 'price' in edited_products[product_id].keys():
                                    edited_products[product_id]['price'] += line[2]['price_unit']
                                else:
                                    edited_products[product_id]['price'] = line[2]['price_unit']
                            else:
                                edited_products[product_id]['price'] += so_line.price_unit

                    #existed products
                    if line[0] == 4:
                        so_line = self.order_line.browse(line[1])
                        product_id = so_line.product_id.id

                        if product_id not in existed_products.keys():
                            existed_products.update({
                                product_id:{
                                    'name':so_line.name,
                                    'qty':so_line.product_qty,
                                    'price':so_line.price_unit,
                                    'date_planned':so_line.date_planned,
                                    'product_uom':so_line.product_uom.id
                                }
                            })
                        else:
                            existed_products[product_id]['qty'] += so_line.product_qty
                            existed_products[product_id]['price'] += so_line.price_unit

            id_set=set()
            if new_products:
                for ids in new_products:
                    id_set.add(ids)

            if existed_products:
                for ids in existed_products:
                    id_set.add(ids)

            if edited_products:
                for ids in edited_products:
                    id_set.add(ids)


            new_vals={}
            for product_id in id_set:

                if new_products:
                    if 'new' not in new_vals.keys():
                        new_vals['new'] = 'ok'

                        for ids in new_products:
                            if ids not in new_vals.keys():
                                new_vals.update({
                                    ids:{
                                        'product_id':ids,
                                        'name':new_products[ids]['name'],
                                        'qty':new_products[ids]['qty'],
                                        'price':new_products[ids]['price'],
                                        'date_planned':new_products[ids]['date_planned'],
                                        'product_uom':new_products[ids]['product_uom']
                                    }
                                })

                if edited_products:
                    if 'edited' not in new_vals.keys():
                        new_vals['edited'] = 'ok'

                        for ids in edited_products:
                            if ids not in new_vals.keys():
                                new_vals.update({
                                    ids:{
                                        'product_id':ids,
                                        'name':edited_products[ids]['name'],
                                        'qty':edited_products[ids]['qty'],
                                        'price':edited_products[ids]['price'],
                                        'date_planned':edited_products[ids]['date_planned'],
                                        'product_uom':edited_products[ids]['product_uom']
                                    }
                                })
                            else:
                                new_vals[ids]['qty'] += edited_products[ids]['qty']
                                new_vals[ids]['price'] += edited_products[ids]['price']

                if existed_products:
                    if 'existed' not in new_vals.keys():
                        new_vals['existed'] = 'ok'

                        for ids in existed_products:
                            if ids not in new_vals.keys():
                                new_vals.update({
                                    ids:{
                                        'product_id':ids,
                                        'name':existed_products[ids]['name'],
                                        'qty':existed_products[ids]['qty'],
                                        'price':existed_products[ids]['price'],
                                        'date_planned':existed_products[ids]['date_planned'],
                                        'product_uom':existed_products[ids]['product_uom']
                                    }
                                })
                            else:
                                new_vals[ids]['qty'] += existed_products[ids]['qty']
                                new_vals[ids]['price'] += existed_products[ids]['price']

            if 'new' in new_vals:
                new_vals.pop('new')
            if 'edited' in new_vals:
                new_vals.pop('edited')
            if 'existed' in new_vals:
                new_vals.pop('existed')
                            
            product_vals_list=[]
            for ids in new_vals:
                product_vals_list.append([
                    0, 0, {
                        'product_id':new_vals[ids]['product_id'],
                        'name':new_vals[ids]['name'],
                        'product_qty':new_vals[ids]['qty'],
                        'price_unit':new_vals[ids]['price'],
                        'date_planned':new_vals[ids]['date_planned'],
                        'product_uom':new_vals[ids]['product_uom']
                    }
                ])

            if self.state == 'draft' or self.state == 'sent':
                if "order_line" in vals.keys():
                    so_line_list = vals['order_line']

                    for line in so_line_list:
                        if line[0] == 1 or line[0] == 4:
                            self.order_line.browse(line[1]).unlink()
                vals['order_line'] = product_vals_list

        res = super(PurchaseOrder, self).write(vals)
        return res
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: