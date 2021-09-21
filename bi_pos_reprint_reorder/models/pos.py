# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import Warning
import random
from datetime import date, datetime


class pos_order(models.Model):
	_inherit = 'pos.order'

	def print_pos_receipt(self):
		orderlines = []
		paymentlines = []
		discount = 0

		for orderline in self.lines:
			new_vals = {
				'product_id': orderline.product_id.name,
				'total_price' : orderline.price_subtotal_incl,
				'qty': orderline.qty,
				'price_unit': orderline.price_unit,
				'discount': orderline.discount,
				}
				
			discount += (orderline.price_unit * orderline.qty * orderline.discount) / 100
			orderlines.append(new_vals)

		for payment in self.payment_ids:
			if payment.amount > 0:
				temp = {
					'amount': payment.amount,
					'name': payment.payment_method_id.name
				}
				paymentlines.append(temp)

		vals = {
			'discount': discount,
			'orderlines': orderlines,
			'paymentlines': paymentlines,
			'change': self.amount_return,
			'subtotal': self.amount_total - self.amount_tax,
			'tax': self.amount_tax,
			'barcode': self.barcode,
			'user_name' : self.user_id.name
		}

		return vals