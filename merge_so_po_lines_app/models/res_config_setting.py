# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	auto_merge_so_line = fields.Boolean("Auto Merge Sale Order Lines", config_parameter='merge_so_po_lines_app.auto_merge_so_line')
	auto_merge_po_line = fields.Boolean("Auto Merge Purchase Order Lines", config_parameter='merge_so_po_lines_app.auto_merge_so_line')
	
	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		ICPSudo = self.env['ir.config_parameter'].sudo()
		auto_merge_so_line = ICPSudo.get_param('merge_so_po_lines_app.auto_merge_so_line')
		auto_merge_po_line = ICPSudo.get_param('merge_so_po_lines_app.auto_merge_po_line')
		res.update(
			auto_merge_so_line=auto_merge_so_line,
			auto_merge_po_line=auto_merge_po_line,
			)
		return res


	def set_values(self):
		super(ResConfigSettings, self).set_values()
		ICPSudo = self.env['ir.config_parameter'].sudo()
		ICPSudo.set_param('merge_so_po_lines_app.auto_merge_so_line',self.auto_merge_so_line)
		ICPSudo.set_param('merge_so_po_lines_app.auto_merge_po_line',self.auto_merge_po_line)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: