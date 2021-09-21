# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools
from odoo.exceptions import Warning
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class POSConfigInherit(models.Model):
	_inherit = 'pos.config'
	
	allow_partical_payment = fields.Boolean('Allow Partial Payment')
	partial_product_id = fields.Many2one("product.product",string="Partial Payment Product", domain = [('type', '=', 'service'),('available_in_pos', '=', True)])

	@api.model
	def create(self, vals):
		res=super(POSConfigInherit, self).create(vals)
		product=self.env['product.product'].browse(vals.get('partial_product_id',False))

		if vals.get('allow_partical_payment',False) and product:
			if product.available_in_pos != True:
				raise ValidationError(_('Please enable available in POS for the Partial Payment Product'))

			if product.taxes_id:
				raise ValidationError(_('You are not allowed to add Customer Taxes in the Partial Payment Product'))

		return res


	def write(self, vals):
		res=super(POSConfigInherit, self).write(vals)

		if self.allow_partical_payment:
			if self.partial_product_id.available_in_pos != True:
				raise ValidationError(_('Please enable available in POS for the Partial Payment Product'))

			if self.partial_product_id.taxes_id:
				raise ValidationError(_('You are not allowed to add Customer Taxes in the Partial Payment Product'))

		return res