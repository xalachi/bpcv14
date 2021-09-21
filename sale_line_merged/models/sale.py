# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def check_same_product_available(self):
        order_line = self.env['sale.order.line'].search([
            ('order_id', '=', self.id)])
        product_wise_sol = {}
        for line in order_line:
            if line.product_id.id not in product_wise_sol:
                product_wise_sol[line.product_id.id]= [line.id]
            else:
                product_wise_sol[line.product_id.id].append(line.id)
        msg = ""
        attach_vals = {
                'sale_id': self.id,
                'error_message': msg,
            }
        act_id = self.env['existing.sale.final'].with_context({'pass':1}).create(attach_vals)
        line_create = []
        for i in product_wise_sol:
            if len(product_wise_sol[i]) > 1:
                for line in product_wise_sol[i]:
                    sol = self.env['sale.order.line'].browse(line)
                    val = {
                        'product_id': sol.product_id.id,
                        'qty': sol.product_uom_qty,
                        'sline_id': line,
                        'existing_sale_final_id':act_id.id
                    }
                    w = self.env['sale.line.wiz'].create(val)
                    line_create.append(w.id)
        if not line_create:
            raise Warning(_('Sorry! No any product have same/duplicate.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'existing.sale.final',
            'view_type': 'form',
            'res_id': act_id.id,
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
