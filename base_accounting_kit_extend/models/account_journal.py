# -*- coding: utf-8 -*-


from odoo import models, api, fields
import json

class AccountJournal(models.Model):
    _inherit = "account.journal"

    number_to_reconcile_journal = fields.Integer(compute='_compute_number_to_reconcile_journal', copy=False)

    @api.depends('kanban_dashboard')
    def _compute_number_to_reconcile_journal(self):
        for record in self:
            number_to_reconcile_journal = 0
            if record.kanban_dashboard:
                load = json.loads(record.kanban_dashboard)
                if 'number_to_reconcile' in load:
                    number_to_reconcile_journal = load['number_to_reconcile']
            record.number_to_reconcile_journal = number_to_reconcile_journal

