# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class ResConfigSettings(models.TransientModel):
	_inherit = "res.config.settings"

	auto_merge_sale_orderlines = fields.Boolean(string="Auto Merge Sale Orderlines" , default= False)
	auto_merge_purchase_orderlines = fields.Boolean(string="Auto Merge Purchase Orderlines", default=False)


	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		auto_merge_sale_orderlines = self.env['ir.config_parameter'].sudo().get_param('order_merge.auto_merge_sale_orderlines')
		auto_merge_purchase_orderlines = self.env['ir.config_parameter'].sudo().get_param('order_merge.auto_merge_purchase_orderlines')
		res.update(
			auto_merge_sale_orderlines = auto_merge_sale_orderlines,
			auto_merge_purchase_orderlines=auto_merge_purchase_orderlines,
		)
		return res

	def set_values(self):
		super(ResConfigSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('order_merge.auto_merge_sale_orderlines', self.auto_merge_sale_orderlines)
		self.env['ir.config_parameter'].sudo().set_param('order_merge.auto_merge_purchase_orderlines',self.auto_merge_purchase_orderlines)

