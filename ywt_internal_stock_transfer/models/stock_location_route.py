from odoo import fields, models, api


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'
    
    source_location_id = fields.Many2one('stock.location', string="Source Location")
    destination_location_id = fields.Many2one('stock.location', string="Destination Location")
    
    def create_internal_stock_location(self, location_id, location_dest_id, warehouse_id=False):
        stock_location_obj = self.env['stock.location']
        stock_warehouse_obj = self.env['stock.warehouse']
        if not warehouse_id:
            warehouse_id = location_id.get_warehouse()
            if not warehouse_id:
                warehouse_id = stock_warehouse_obj.search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        bridge_location_id = self.env.user.company_id.bridge_transfer_location_id
        stock_picking_type_id = warehouse_id.int_type_id
        stock_rule_vals1 = {'name': '%s To %s ' % (location_id.name, bridge_location_id.name),
                            'action': 'pull',
                            'procure_method': 'make_to_stock',
                            'location_src_id': location_id.id,
                            'location_id': bridge_location_id and bridge_location_id.id or False,
                            'picking_type_id': stock_picking_type_id and stock_picking_type_id.id or False,
                            'warehouse_id':warehouse_id.id}
           
        stock_rule_vals2 = {'name': '%s To %s ' % (bridge_location_id.name, location_dest_id.name),
                            'action': 'pull_push',
                            'procure_method': 'make_to_order',
                            'location_src_id': bridge_location_id and bridge_location_id.id or False,
                            'location_id': location_dest_id and location_dest_id.id or False,
                            'picking_type_id': stock_picking_type_id and stock_picking_type_id.id or False,
                            'warehouse_id':warehouse_id.id}
        
        stock_location_route_vals = {'name': '%s To %s' % (location_id.display_name, location_dest_id.display_name),
                                    'rule_ids': [(0, 0, stock_rule_vals1), (0, 0, stock_rule_vals2)],
                                    'source_location_id': location_id.id,
                                    'destination_location_id': location_dest_id.id}
        
        route_id = self.create(stock_location_route_vals)
        return route_id
