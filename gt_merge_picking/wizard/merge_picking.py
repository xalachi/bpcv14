# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    Globalteckz                                                              #
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)        #
#                                                                             #   
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU Affero General Public License for more details.                      #
#                                                                             #  
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #           
###############################################################################
from odoo.exceptions import UserError
from odoo import models, fields, api

class MergePicking(models.TransientModel):
    _name = 'merge.picking'

    merge_picking_line = fields.One2many('merge.pickingline','partner_id',string="New Line")

    @api.model
    def default_get(self, vals):
        res = super(MergePicking,self).default_get(vals)
        picking_obj = self.env['stock.picking']
        stock_ids=self.env.context.get('active_ids')
        stock_vals=[]
        stock_info=picking_obj.browse(stock_ids)
        for stock in stock_info:
            if stock.state=='done':
                    raise UserError(('Merging is not allowed on done picking.'))			
            stock_vals.append((0,0,{
            'pick_name':stock.name,
            'partner_id':stock.partner_id.id,
            'origin':stock.origin,
            'state':stock.state
            }))

            res.update({'merge_picking_line': stock_vals})
        return res


    def Create_new_picking_record(self):
        picking_obj = self.env['stock.picking']
        wizard_stock=self.env.context.get('active_ids')
        if len(wizard_stock)==1:
            raise UserError(('Please select multiple picking to create a list view.'))	
        stock_info=picking_obj.browse(wizard_stock)
        partner_list=[]
        state_list=[]
        picking_type_list=[]
        for partner_li in stock_info:
            partner_list.append(partner_li.partner_id.id)
        for picking_type_li in stock_info:
            picking_type_list.append(picking_type_li.picking_type_id.id)
        for state_li in stock_info:
            state_list.append(state_li.state)
        if state_list[1:] != state_list[:-1]:
            raise UserError(('Merging is only allowed on picking of same state'))
        if stock_info:
            move_line_val=[]
            origin=''
            for info in stock_info:
                if partner_list[0] !=info.partner_id.id :
                    raise UserError(('Merging is only allowed on picking of same partner.'))
                if picking_type_list[0] !=info.picking_type_id.id :
                    raise UserError(('Merging is only allowed on picking of same Types.'))
                if origin:
                    origin = origin +'-'+info.name
                else:
                    origin = info.name
                for product_line in info.move_lines:
                    move_line_val.append((0,0,{
                        'product_id':product_line.product_id.id,
                        'product_uom_qty':product_line.product_uom_qty,
                        'state':product_line.state,
                        'product_uom':product_line.product_id.uom_id.id,
                        'name':product_line.product_id.name,
                        'date_deadline':product_line.date_deadline
                        }))
                info.action_cancel()

            vals={
            'partner_id':stock_info[0].partner_id.id,
            'origin':origin,
            'scheduled_date':stock_info[0].scheduled_date,
            'move_lines':move_line_val,
            'move_type':stock_info[0].move_type,
            'picking_type_id':stock_info[0].picking_type_id.id,
            'priority':stock_info[0].priority,
            'location_id':stock_info[0].location_id.id,
            'location_dest_id':stock_info[0].location_dest_id.id
            }
            picking = picking_obj.create(vals)
        return True

class MergePickingLine(models.TransientModel):
    _name='merge.pickingline'


    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")	

    pick_name=fields.Char('Reference')
    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'), ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")


	

   
