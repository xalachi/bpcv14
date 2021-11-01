# -*- coding: utf-8 -*-
from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_customer_invoice_template_id(self):
        self.ensure_one()
        if self.move_type != 'out_invoice':
            return False
        return self.env['reporting.custom.template'].sudo().get_template('report_customer_invoice')
