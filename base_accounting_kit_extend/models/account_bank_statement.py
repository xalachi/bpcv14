# -*- coding: utf-8 -*-

import copy
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import formatLang, format_date, parse_date
import json

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"


    kanban_dashboard_journal = fields.Text(related='journal_id.kanban_dashboard')
    number_to_reconcile_journal = fields.Integer(related='journal_id.number_to_reconcile_journal')


    def action_open_reconcile(self):

        for record in self:
            if record.journal_id:
                return record.journal_id.action_open_reconcile()