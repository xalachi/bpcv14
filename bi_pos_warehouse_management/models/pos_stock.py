# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api,tools, _
from datetime import datetime, timedelta
import json
from odoo.exceptions import RedirectWarning, UserError, ValidationError ,Warning
import logging
from odoo.tools import float_is_zero
_logger = logging.getLogger(__name__)


class POSConfigShop(models.Model):
	_inherit = 'pos.config'

	def _get_default_location(self):
		return self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id
	
	display_stock_pos = fields.Boolean('Display Stock in POS')
	stock_location_id = fields.Many2one(
		'stock.location', string='Stock Location',
		domain=[('usage', '=', 'internal')], default=_get_default_location)
	unavailable_msg = fields.Char('Unavailable Message')
	warehouse_available_ids = fields.Many2many('stock.location', string='Related Stock Location',domain=[('usage', '=', 'internal')])
	
	def get_locations(self):    
		warehouse_loc_obj = self.env['stock.location'].search([('id', 'in', self.warehouse_available_ids)]) 
		return warehouse_loc_obj

	@api.model
	def create(self, vals):
		res=super(POSConfigShop, self).create(vals)
		if vals.get('display_stock_pos'):
			if vals.get('stock_location_id') not in vals.get('warehouse_available_ids'):
				raise ValidationError(_('Please add default location in available locations'))
		return res


	def write(self, vals):
		res=super(POSConfigShop, self).write(vals)
		if self.display_stock_pos :
			if self.stock_location_id.id  not in self.warehouse_available_ids.ids:
				raise ValidationError(_('Please add default location in available locations'))

		return res
		

class PosOrderLineInherit(models.Model):
	_inherit = 'pos.order.line'

	stock_location_id = fields.Char(string="stock location id")


class RelatedPickingsPos(models.Model):
	_inherit = 'pos.order'

	def _create_order_picking(self):
		self.ensure_one()
		if not self.session_id.update_stock_at_closing or (self.company_id.anglo_saxon_accounting and self.to_invoice):
			picking_type = self.config_id.picking_type_id
			if self.partner_id.property_stock_customer:
				destination_id = self.partner_id.property_stock_customer.id
			elif not picking_type or not picking_type.default_location_dest_id:
				destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
			else:
				destination_id = picking_type.default_location_dest_id.id

			different = self.lines.filtered(lambda l: l.stock_location_id)
			normal = self.lines - different

			pickings = self.env['stock.picking']._create_picking_from_pos_order_lines(destination_id, normal, picking_type, self.partner_id)
			pickings.write({'pos_session_id': self.session_id.id, 'pos_order_id': self.id, 'origin': self.name})

			if different:
				for line in different:
					diff_pick = self.env['stock.picking'].with_context(diff_loc=line.stock_location_id)._create_picking_from_pos_order_lines(destination_id, line, picking_type, self.partner_id)
					diff_pick.write({'pos_session_id': self.session_id.id, 'pos_order_id': self.id, 'origin': self.name})
	

class RelatedPosStock(models.Model):
	_inherit = 'stock.picking'
	
	pos_id = fields.Many2one('pos.order', 'Related POS')

	@api.model
	def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False):
		"""We'll create some picking based on order_lines"""

		pickings = self.env['stock.picking']
		stockable_lines = lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding))
		if not stockable_lines:
			return pickings
		positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
		negative_lines = stockable_lines - positive_lines

		if positive_lines:
			location_id = picking_type.default_location_src_id.id
			if self._context.get('diff_loc'):
				location_id = self._context.get('diff_loc')
			positive_picking = self.env['stock.picking'].create(
				self._prepare_picking_vals(partner, picking_type, location_id, location_dest_id)
			)

			positive_picking._create_move_from_pos_order_lines(positive_lines)
			try:
				with self.env.cr.savepoint():
					positive_picking._action_done()
			except (UserError, ValidationError):
				pass

			pickings |= positive_picking
		if negative_lines:
			if picking_type.return_picking_type_id:
				return_picking_type = picking_type.return_picking_type_id
				return_location_id = return_picking_type.default_location_dest_id.id
			else:
				return_picking_type = picking_type
				return_location_id = picking_type.default_location_src_id.id

			negative_picking = self.env['stock.picking'].create(
				self._prepare_picking_vals(partner, return_picking_type, location_dest_id, return_location_id)
			)
			negative_picking._create_move_from_pos_order_lines(negative_lines)
			try:
				with self.env.cr.savepoint():
					negative_picking._action_done()
			except (UserError, ValidationError):
				pass
			pickings |= negative_picking
		return pickings


class WarehouseStockQty(models.Model):
	_inherit = 'stock.quant'


	def get_product_stock(self, location, other_locations, product):
		quants1 = self.env['stock.quant'].search([('product_id', '=', product),('location_id','=', location[0])])
		if len(quants1) > 1:
				qty = 0.0
				for quant in quants1:
					qty += quant.quantity
		else:
			qty = quants1.quantity
		
		res = []
		for locations in other_locations:
			quants2 = self.env['stock.quant'].search([('product_id', '=', product),('location_id','=', locations['id'])])
			if len(quants2) > 1:
				qty1 = 0.0
				for quant in quants2:
					qty1 += quant.quantity
				res.append({'quantity': qty1, 'location': locations})
				
			else:
				qty1 = quants2.quantity
				res.append({'quantity' : qty1, 'location': locations})
		
		return [qty, res]
		
	def get_loc_stock(self,location_id, product_id):
		quants1 = self.env['stock.quant'].search([('product_id', '=', int(product_id)),('location_id','=', int(location_id))])
		if quants1:
			return quants1.quantity	
	

class Product(models.Model):
	_inherit = 'product.product'

	quant_ids = fields.One2many("stock.quant","product_id",string="Quants",
		domain=[('location_id.usage','=','internal')])

	quant_text = fields.Text('Quant Qty',compute='_compute_avail_locations',store=False)

	@api.depends('quant_ids','quant_ids.location_id','quant_ids.quantity')
	def _compute_avail_locations(self):
		for rec in self:
			rec.quant_text = ''
			qnt = dict(zip( rec.quant_ids.mapped('location_id.id') , rec.quant_ids.mapped('quantity') ))
			rec.quant_text = json.dumps(qnt)
	
	
	

