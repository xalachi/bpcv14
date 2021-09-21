from odoo import models, fields, api, _
from odoo.exceptions import UserError


class YWTInteralStockTransfer(models.Model):
    _name = 'ywt.internal.stock.transfer'
    _description = "Internal Stock Transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Stock Transfer Reference', default='/', copy=False, required=True, states={'processed': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed'), ('cancel', 'Cancel'), ('done', 'Done')], string='State', index=True, default='draft', track_visibility='onchange', copy=False)
    
    res_company_id = fields.Many2one('res.company', string="Company", default=lambda self:self.env.company)
    from_warehouse_id = fields.Many2one('stock.warehouse', string="From Warehouse")
    from_location_id = fields.Many2one('stock.location', "Source Location", domain=[('usage', '=', 'internal')])
    to_warehouse_id = fields.Many2one('stock.warehouse', string="To Warehouse")
    to_location_id = fields.Many2one('stock.location', "Destination Location", domain=[('usage', '=', 'internal')]) 
    procurement_group_id = fields.Many2one('procurement.group', string='Procurement Group', readonly=True, copy=False, ondelete='cascade')
    
    internal_stock_transfer_line_ids = fields.One2many('ywt.internal.stock.transfer.line', 'internal_stock_transfer_id', 'Internal Stock Transfer Line', ondelete='cascade', copy=False)
    
    @api.model
    def create(self, vals):
        vals['name'] = vals.get('name') or '/'
        if vals['name'].startswith('/'):
            vals['name'] = (self.env['ir.sequence'].next_by_code('ywt.internal.stock.transfer') or '/') + vals['name']
            vals['name'] = vals['name'][:-1] if vals['name'].endswith('/') and vals['name'] != '/' else vals['name']
        return super(YWTInteralStockTransfer, self).create(vals)
    
    def action_button_stock_transfer_cancel(self):
        picking_ids = self.env['stock.picking'].search([('group_id', '=', self.procurement_group_id.id), ('state', 'not in', ['done', 'cancel'])])
        if picking_ids:
            for picking in picking_ids:
                picking.action_cancel()
            self.write({'state':'cancel'})
            
    def action_button_stock_transfer_draft(self):
        if self.state == 'cancel':
            self.write({'state':'draft'})
    
    def unlink(self):
        for transfer in self:
            if transfer.state in ['processed', 'done']:
                raise UserError("You can not delete Processed or Done state Transfer!!!")
        return super(YWTInteralStockTransfer, self).unlink()
    
    def action_view_stock_picking(self):
        action = self.env.ref('stock.vpicktree').id
        form_action = self.env.ref('stock.view_picking_form').id
        return {'name': 'Stock Picking',
                'type': 'ir.actions.act_window',
                 'view_type': 'form',
                 'view_mode': 'form',
                 'res_model': 'stock.picking',
                'views': [(action, 'tree'), (form_action, 'form')],
                'view_id': action,
                'domain':[('group_id', 'in', self.procurement_group_id.ids)],
                'target': 'current',
                }
        
    def action_button_stock_transfer_validate(self):
        self.write({'state':'processed'})
        route_obj = self.env['stock.location.route']
        procurement_group_obj = self.env['procurement.group']
        stock_picking_type_obj = self.env['stock.picking.type']
        stock_picking_obj = self.env['stock.picking']
        
        from_location = self.from_location_id
        to_location = self.to_location_id
        
        if from_location.company_id != to_location.company_id:
            raise UserError("Please Select Same Company Location to Transfer Product")
        
        picking_type_id = stock_picking_type_obj.search([('code', '=', 'internal')], limit=1)
        if not picking_type_id:
            raise UserError("Please Configuration Internal Type Location")
           
        transfer_locationlines = self.internal_stock_transfer_line_ids
        if not transfer_locationlines:
            raise UserError("Please Add some Product in Internal Stock Transfer Lines")
           
        route = route_obj.search([('source_location_id', '=', from_location.id), ('destination_location_id', '=', to_location.id)])
        if not route:
            route = route_obj.create_internal_stock_location(from_location, to_location, picking_type_id.warehouse_id)
        procurement_group = procurement_group_obj.create({'name':self.name, 'move_type':'direct'})
        for line  in transfer_locationlines:
            lst_procu = []
            datas = {'route_ids':route,
                   'group_id':procurement_group,
                   'company_id':picking_type_id.warehouse_id.company_id.id,
                   'warehouse_id': picking_type_id.warehouse_id,
                   'priority': '1'}
              
            lst_procu.append(procurement_group_obj.Procurement(line.product_id, line.qty, line.product_id.uom_id, to_location, line.product_id.name, line.product_id.name, picking_type_id.warehouse_id.company_id, datas))
            procurement_group_obj.run(lst_procu)
        picking_ids = self.env['stock.picking'].search([('group_id', '=', procurement_group.id), ('state', 'in', ['assigned', 'confirmed'])])
        for picking_id in picking_ids:
            if picking_id.state == 'confirmed':
                picking_id.action_assign()
        if procurement_group:
            self.write({'state':'done', 'procurement_group_id':procurement_group.id})    
        return True
