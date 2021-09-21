# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def get_domain(self):
        domain = []
        model_id = self.env['ir.model'].search([('model', '=', 'pos.session')])
        domain += [('model_id', '=', model_id.id)]
        return domain

    enable_close_session = fields.Boolean(string="Enable Close Session")
    z_report_pdf = fields.Boolean(string="Z Report Pdf")
    email_close_session_report = fields.Boolean(string="Email Z Report")
    allow_with_zero_amount = fields.Boolean(string="Allow With 0 Amount")
    email_template_id = fields.Many2one('mail.template', string="Email Template",
                                        domain=lambda self: self.env['pos.config'].get_domain())
    users_ids = fields.Many2many('res.users', string="Users")
    allow_prefill_cash = fields.Boolean(string="Allow Cash Prefill")
    prefill_cash_ids = fields.Many2many('opening.cash.prefill', string="Cash Prefill")


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def get_html_report(self, id, report_name):
        report = self._get_report_from_name(report_name)
        document = report._render_qweb_html(id, data={})
        if document:
            return document
        return False


class OpeningCashPrefill(models.Model):
    _name = 'opening.cash.prefill'
    _description = 'Opening Cash Prefill'


    name = fields.Char('Name')
    value = fields.Float('Value', required=True)

    @api.model
    def create(self, vals):
        res = super(OpeningCashPrefill, self).create(vals)
        if res.value != 0:
            return res
        else:
            raise ValidationError(_('Value can not be 0.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
