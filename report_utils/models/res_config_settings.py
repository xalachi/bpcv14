# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def open_custom_template_report_utils(self):
        template_obj = self.env['reporting.custom.template']
        report_name = self._context['report_name']
        report_id = template_obj.search([('name', '=', report_name)])

        if not report_id:
            report_list = template_obj.get_report_list()
            if report_name not in report_list:
                raise UserError('We couldn\'t find report \'%s\'' % report_name)

            template_obj.reset_template(report_name)
            report_id = template_obj.search([('name', '=', report_name)])

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reporting.custom.template',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': report_id.id,
        }
