# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.tools import float_is_zero


class PosConfigInherit(models.Model):
	_inherit = "pos.config"

	multi_currency = fields.Boolean(string="Enable Multi Currency")
	curr_conv = fields.Boolean(string="Enable Multi Currency Conversation")
	selected_currency = fields.Many2many("res.currency", string="pos")


class CurrencyInherit(models.Model):
	_inherit = "res.currency"

	rate_in_company_currency = fields.Float(compute='_compute_company_currency_rate', string='Company Currency Rate',
											digits=0)

	def _compute_company_currency_rate(self):
		company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
		company_currency = company.currency_id
		for currency in self:
			price = currency.rate
			if company_currency.id != currency.id:
				new_rate = (price) / company_currency.rate
				price = round(new_rate, 6)
			else:
				price = 1
			currency.rate_in_company_currency = price


class ExchangeRate(models.Model):
	_name = "currency.rate"
	_description = "Exchange Rate"

	currency_id = fields.Many2one("res.currency", string="Currency")
	symbol = fields.Char(related="currency_id.symbol", string="currency symbol")
	date = fields.Datetime(string="current Date", default=datetime.today())
	rate = fields.Float(related="currency_id.rate", string="Exchange Rate")
	pos = fields.Many2one("pos.config")


class ExchangeRate(models.Model):
	_inherit = "pos.payment"

	account_currency = fields.Float("Amount currency")
	currency = fields.Char("currency")


class ExchangeRate(models.Model):
	_inherit = "account.bank.statement.line"

	account_currency = fields.Monetary("Amount currency")
	currency = fields.Char("currency")


class PosOrder(models.Model):
	_inherit = "pos.order"

	cur_id = fields.Many2one("res.currency")

	@api.model
	def _payment_fields(self, order, ui_paymentline):
		res = super(PosOrder, self)._payment_fields(order, ui_paymentline)
		account_currency = ui_paymentline.get('currency_amount',0)
		if ui_paymentline.get('amount',0) < 0 and  ui_paymentline.get('currency_amount',0) > 0 :
			account_currency = - account_currency
		res.update({
			'account_currency': account_currency if account_currency != 0 else  ui_paymentline.get('amount',0),
			'currency' : ui_paymentline['currency_name'] or order.pricelist_id.currency_id.name,
		})
		return res

	def _process_payment_lines(self, pos_order, order, pos_session, draft):
		"""Create account.bank.statement.lines from the dictionary given to the parent function.

		If the payment_line is an updated version of an existing one, the existing payment_line will first be
		removed before making a new one.
		:param pos_order: dictionary representing the order.
		:type pos_order: dict.
		:param order: Order object the payment lines should belong to.
		:type order: pos.order
		:param pos_session: PoS session the order was created in.
		:type pos_session: pos.session
		:param draft: Indicate that the pos_order is not validated yet.
		:type draft: bool.
		"""
		prec_acc = order.pricelist_id.currency_id.decimal_places

		order_bank_statement_lines = self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
		order_bank_statement_lines.unlink()
		for payments in pos_order['statement_ids']:
			if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
				order.add_payment(self._payment_fields(order, payments[2]))

		order.amount_paid = sum(order.payment_ids.mapped('amount'))

		if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
			cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
			if not cash_payment_method:
				raise UserError(_("No cash statement found for this session. Unable to record returned cash."))

			return_amount = pos_order.get('amount_return',0)
			sc = order.pricelist_id.currency_id
			if  pos_order.get('currency_amount') and pos_order.get('currency_symbol'):
				oc = self.env['res.currency'].search([('name','=',pos_order.get('currency_name',''))])
				if oc != sc:
					return_amount = sc._convert(pos_order.get('amount_return',0), oc, order.company_id, order.date_order)

			return_payment_vals = {
				'name': _('return'),
				'pos_order_id': order.id,
				'amount': -pos_order['amount_return'],
				'payment_date': fields.Datetime.now(),
				'payment_method_id': cash_payment_method.id,
				'account_currency': -return_amount or 0.0,
				'currency' : pos_order.get('currency_name',order.pricelist_id.currency_id.name),
			}
			order.add_payment(return_payment_vals)
