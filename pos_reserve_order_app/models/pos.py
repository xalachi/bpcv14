# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
from functools import partial
import logging
import psycopg2
import pytz
_logger = logging.getLogger(__name__)


class POSOrderInherit(models.Model):
	_inherit = 'pos.order.line'

	old_qty = fields.Float('Old Qty' , default = 0.0)
	is_cancel_charge_line = fields.Boolean('Cancel Charge Line')

class POSOrderInherit(models.Model):
	_inherit = 'pos.order'

	is_reserved = fields.Boolean('Reserved Order')
	amount_due = fields.Float(string='Amount Due', readonly=True)
	delivery_date =fields.Date(string='Reserve Order delivery Date', readonly=True)

	state = fields.Selection(selection_add=[('reserved', 'Reserved')],string='Status', readonly=True, copy=False, default='draft')

	def unlink(self):
		for pos_order in self.filtered(lambda pos_order: pos_order.state in ['reserved']):
			pos_order.write({'state': 'cancel'})

		for pos_order in self.filtered(lambda pos_order: pos_order.state not in ['draft','cancel']):
			raise UserError(_('In order to delete a sale, it must be new or Reserved or cancelled.'))
		return super(POSOrderInherit, self).unlink()

	def action_pos_order_paid(self):
		# if not self._is_pos_order_paid() and self.state == 'reserved':
		# 	self.																																																																																																																																																																															()
		# 	raise UserError(_("Order %s is not fully paid.") % self.name)
		if not self._is_pos_order_paid():
			raise UserError(_("Order %s is not fully paid.") % self.name)
		self.write({'state': 'paid'})
		return self.create_picking()

	@api.model
	def _order_fields(self, ui_order):
		res = super(POSOrderInherit, self)._order_fields(ui_order)
		if ui_order['is_reserved'] == True:
			res['is_reserved'] = ui_order['is_reserved']
			res['state'] = 'reserved'
			res['amount_due'] = ui_order['amount_due']
			res['delivery_date'] = ui_order['delivery_date']
		return res

	def write(self, vals):
		for order in self:
			if vals.get('state') and vals['state'] == 'paid' and order.name == '/':
				vals['name'] = order.config_id.sequence_id._next()
			else:
				vals['name'] = self.env['ir.sequence'].next_by_code('pos.order')
		return super(POSOrderInherit, self).write(vals)



	@api.model
	def create_from_ui(self, orders, draft=False):
		""" Create and update Orders from the frontend PoS application.

		Create new orders and update orders that are in draft status. If an order already exists with a status
		diferent from 'draft'it will be discareded, otherwise it will be saved to the database. If saved with
		'draft' status the order can be overwritten later by this function.

		:param orders: dictionary with the orders to be created.
		:type orders: dict.
		:param draft: Indicate if the orders are ment to be finalised or temporarily saved.
		:type draft: bool.
		:Returns: list -- list of db-ids for the created and updated orders.
		"""
		order_ids = []
		for order in orders:
			existing_order = False
			if 'server_id' in order['data']:
				existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
			if (existing_order and existing_order.state == 'draft') or not existing_order:
				order_ids.append(self._process_order(order, draft, existing_order))

			pos_order_ids = self.env['pos.order'].search([('id','in',order_ids)])
			for pos_order in pos_order_ids:
				if pos_order.is_reserved:
					for line in pos_order.lines:
						self.update_stock_qty(line)
				order_ids.append(pos_order.id)

		return self.env['pos.order'].search_read(domain = [('id', 'in', order_ids)], fields = ['id', 'pos_reference'])

	def create_pos_order(self,create_order):
		pos_session = self.env['pos.session'].browse(create_order['pos_session_id'])
		pos_order = self._process_order(create_order)
		for line in pos_order.lines:
			self.update_stock_qty(line)
		return pos_order.id

	def update_stock_qty(self,line):
		if line.product_id.type == 'product' :
			stock_quant = self.env['stock.quant'].sudo()
			picking_type = line.order_id.picking_type_id
			config_loc = picking_type.default_location_src_id.id
			reserved_loc = line.order_id.config_id.reservation_location.id
			config_loc_stock = stock_quant.search([('product_id','=',line.product_id.id),('location_id','=',config_loc)])
			reserved_loc_stock= stock_quant.search([('product_id','=',line.product_id.id),('location_id','=',reserved_loc)])
			config_loc_qty = 0
			reserved_loc_qty = 0
			if config_loc_stock:
				for stock in config_loc_stock:
					config_loc_qty = stock.quantity
					config_loc_stock.write({
						'quantity' : config_loc_qty + abs(line.old_qty - line.qty) if line.old_qty > line.qty  else config_loc_qty - abs(line.old_qty - line.qty)
						})
			else:
				updt_config_qty = {
					'product_id' :line.product_id.id,
					'location_id': config_loc,
					'quantity': config_loc_qty + line.qty if line.old_qty > line.qty  else config_loc_qty - line.qty ,
					}
				config_loc_quant = stock_quant.create(updt_config_qty)

			if reserved_loc_stock:
				for reserve in reserved_loc_stock:
					reserved_loc_qty = reserve.quantity
					reserved_loc_stock.write({
						'quantity' : reserved_loc_qty - abs(line.old_qty - line.qty) if line.old_qty > line.qty else reserved_loc_qty + abs(line.old_qty - line.qty),
						})
			else:
				updt_reserve_qty = {
				'product_id' :line.product_id.id,
				'location_id':reserved_loc,
				'quantity': reserved_loc_qty - line.qty if line.old_qty > line.qty else reserved_loc_qty + line.qty,
				}
				reserve_loc_quant = stock_quant.create(updt_reserve_qty)
			line.write({'old_qty' : line.qty})
	
	def remove_line_update_stock_qty(self,line):
		if line.product_id.type == 'product' :
			stock_quant = self.env['stock.quant'].sudo()
			picking_type = line.order_id.picking_type_id
			config_loc = picking_type.default_location_src_id.id
			reserved_loc = line.order_id.config_id.reservation_location.id
			config_loc_stock = stock_quant.search([('product_id','=',line.product_id.id),('location_id','=',config_loc)])
			reserved_loc_stock= stock_quant.search([('product_id','=',line.product_id.id),('location_id','=',reserved_loc)])

			config_loc_qty = 0
			reserved_loc_qty = 0
			if config_loc_stock:
				for stock in config_loc_stock:
					config_loc_qty = stock.quantity
					config_loc_stock.write({
						'quantity' : config_loc_qty + line.qty
						})

			if reserved_loc_stock:
				for reserve in reserved_loc_stock:
					reserved_loc_qty = reserve.quantity
					reserved_loc_stock.write({
						'quantity' : reserved_loc_qty -  line.qty
						})

	def change_reserve_date(self,changed_date):
		DATETIME_FORMAT = "%Y-%m-%d"
		i_date = datetime.strptime(changed_date, DATETIME_FORMAT)
		self.write({'delivery_date':changed_date})

	def change_or_remove_product(self,cancelorder_products,removedline,config_id,is_del_all):
		lines = []
		config = self.env['pos.config'].search([('id','=',int(config_id))])
		if is_del_all:
			if config.cancel_charge_type == 'percentage' :
				temp_charge = (self.amount_total * config.cancel_charges)/100.0;
			else :
				temp_charge = config.cancel_charges;

			for line in self.lines:
				if line.is_cancel_charge_line == False :
					self.remove_line_update_stock_qty(line)
					line.update({'price_subtotal' : 0,
						'price_subtotal_incl' : 0,
						'price_unit':0})
			vals = {
				'discount': 0,
				'order_id': self.id,
				'price_unit':temp_charge,
				'product_id': config.cancel_charges_product.id,
				'qty': 1,
				'is_cancel_charge_line' : True,
				'price_subtotal' : temp_charge,
				'price_subtotal_incl' : temp_charge,
			}
			self.env['pos.order.line'].create(vals)
		else:
			if removedline:
				for line in removedline:
					rline = self.env['pos.order.line'].search([('id','=',int(line))])
					if config.cancel_charge_type == 'percentage' :
						temp_charge = (rline.price_subtotal_incl * config.cancel_charges)/100.0;
					else :
						temp_charge = config.cancel_charges;
					self.remove_line_update_stock_qty(rline)
					rline.update({'price_subtotal' : 0,
						'price_subtotal_incl' : 0,
						'price_unit':0})
					vals = {
						'discount': 0,
						'order_id': self.id,
						'price_unit':temp_charge,
						'product_id': config.cancel_charges_product.id,
						'qty': 1,
						'is_cancel_charge_line' : True,
						'price_subtotal' : temp_charge,
						'price_subtotal_incl' : temp_charge,
					}
					self.env['pos.order.line'].create(vals)
			else:	
				for k,v in cancelorder_products.items():
					pos_line =self.env['pos.order.line'].search([('id','=',int(k))])
					fpos = pos_line.order_id.fiscal_position_id
					tax_ids_after_fiscal_position = fpos.map_tax(pos_line.tax_ids, pos_line.product_id, pos_line.order_id.partner_id) if fpos else pos_line.tax_ids
					price = pos_line.price_unit * (1 - (pos_line.discount or 0.0) / 100.0)
					taxes = tax_ids_after_fiscal_position.compute_all(price, pos_line.order_id.pricelist_id.currency_id,v, product=pos_line.product_id, partner=pos_line.order_id.partner_id)
					if pos_line.qty > v :
						if config.cancel_charge_type == 'percentage' :
							diff_price = (pos_line.qty - v) * pos_line.price_unit
							temp_charge = (diff_price * config.cancel_charges)/100.0;
						else :
							temp_charge = config.cancel_charges;
						vals = {
							'discount': 0,
							'order_id': self.id,
							'price_unit':temp_charge,
							'product_id': config.cancel_charges_product.id,
							'qty': 1,
							'is_cancel_charge_line' : True,
							'price_subtotal' : temp_charge,
							'price_subtotal_incl' : temp_charge,
						}
						self.env['pos.order.line'].create(vals)
					pos_line.write({
						'qty':v,
						'price_subtotal_incl': taxes['total_included'],
						'price_subtotal': taxes['total_excluded'],
						})
				for line in self.lines :
					if line.is_cancel_charge_line == False :
						self.update_stock_qty(line)

		currency = self.pricelist_id.currency_id
		amount_tax = currency.round(sum(self._amount_line_tax(line, self.fiscal_position_id) for line in self.lines))
		amount_untaxed = currency.round(sum(line.price_subtotal for line in self.lines))
		amount_total = amount_tax + amount_untaxed
		self.write({
			'amount_tax': amount_tax,
			'amount_total' : amount_total,
			'amount_due' : amount_total - self.amount_paid,
			})
		

	def get_reserved_lines(self):
		reserved_orders = self.env['pos.order'].search([('state','=','reserved')])
		line_list = []
		for odr in reserved_orders:
			for line in odr.lines:
				line_list.append({
					'product' : line.product_id.name,
					'qty' : line.qty,
					'order_id' : odr.name,
					'delivery_date' : odr.delivery_date,
					'date_order' : odr.date_order
					})
		return line_list
	
	def pay_reserved_amount(self,select_journal_id,pay_amount,cash_jrnl_id,session_id):
		jounral = self.env['account.journal'].browse(select_journal_id)
		statement_id = 0
		cash_journal = self.env['account.journal'].browse(cash_jrnl_id)
		session = self.env['pos.session'].browse(session_id)
		for i in self.payment_ids:
			statement_id = i.payment_method_id
			break
		args = {
				'amount': float(pay_amount),
				'pos_order_id': self.id,	
				'payment_date': fields.Date.context_today(self),
				'payment_method_id':statement_id.id,
				'name': self.name,
				'partner_id': self.env["res.partner"]._find_accounting_partner(self.partner_id).id or False,
			}
		self.env['pos.payment'].create(args)

		if pay_amount > self.amount_due :
			return_amount = {
				'amount': self.amount_due - pay_amount,
				'pos_order_id': self.id,	
				'payment_date': fields.Date.context_today(self),
				'payment_method_id':statement_id.id,
				'name': self.name + ': ' + 'return',
				'partner_id': self.env["res.partner"]._find_accounting_partner(self.partner_id).id or False,
			}
			self.env['pos.payment'].create(return_amount)
			self.write({
				'state': 'paid',
				'amount_paid' : sum(payment.amount for payment in self.payment_ids),
				'amount_due': 0.0,
			})
			for line in self.lines:
				if line.price_unit > 0 : 
					self.remove_line_update_stock_qty(line)

			self._create_order_picking()

		if pay_amount == self.amount_due :
			for line in self.lines:
				if line.price_unit > 0 : 
					self.remove_line_update_stock_qty(line)
			self.write({
				'state': 'paid',
				'amount_paid' : sum(payment.amount for payment in self.payment_ids),
				'amount_due': 0.0,
			})
			self._create_order_picking()
		else :
			self.write({
			'amount_paid' : sum(payment.amount for payment in self.payment_ids),
			'amount_due': self.amount_due - pay_amount,
			})
		

