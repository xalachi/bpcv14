# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_pos_cash_control = fields.Boolean(string="Cash Control in POS", default=True)

class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def get_payments(self, kwargs):
        results = {}
        if kwargs.get('pos_session_id'):
            pos_session_id = self.search([('id', '=', kwargs.get('pos_session_id'))])
            if pos_session_id:
                results['cash_register_balance_start'] = pos_session_id.cash_register_balance_start
                results['cash_register_total_entry_encoding'] = pos_session_id.cash_register_total_entry_encoding 
                results['cash_register_balance_end'] = pos_session_id.cash_register_balance_end
                results['cash_register_balance_end_real'] = pos_session_id.cash_register_balance_end_real     
            payments = self.env['pos.payment'].search([('session_id', '=', kwargs.get('pos_session_id'))])
            if payments and len(payments):
                values = []
                for payment in payments:
                    result = {}
                    result['payment_name'] = payment.payment_method_id.name
                    result['pos_order_name'] = payment.pos_order_id.name
                    result['amount'] = payment.amount
                    result['payment_date'] = payment.payment_date.date()
                    values.append(result)
                results['values'] = values
        return results

    @api.model
    def create_check_in_out(self,kwargs):
        cash_in_details = {
            'name':kwargs.get('name'),
            'amount':kwargs.get('amount'),
        }
        cash_box_out = self.env['cash.box.out'].create(cash_in_details)
        session_id = self.search([('id', '=', kwargs.get('pos_session_id'))])
        bank_statements = [session_id.cash_register_id for session_id in self.browse(session_id.id) if session_id.cash_register_id]
        if not bank_statements:
            return {
                'unable_to_create': True,
                'message' : "There is no cash register for this PoS Session"
            }

        for box in cash_box_out:
            for record in bank_statements:
                if not record.journal_id:
                    return {
                            'unable_to_create': True,
                            'message' : "Please check that the field 'Journal' is set on the Bank Statement"
                        }

                if not record.journal_id.company_id.transfer_account_id:
                    return {
                            'unable_to_create': True,
                            'message' : "Please check that the field 'Transfer Account' is set on the company."
                        }
           
                if record.state == 'confirm':
                    return {
                        'unable_to_create': True,
                        'message' : "You cannot put/take money in/out for a bank statement which is closed."
                    }

                values = box._calculate_values_for_statement_line(record)
                record.write({'line_ids': [(0, False, values)]})

                if kwargs.get('type') == 'cash_in':
                    self.env['pos.cash.in.out'].create({
                        'transaction_type': kwargs.get('type'),
                        'amount': kwargs.get('amount'),
                        'reason': kwargs.get('name'),
                        'session_id': session_id.id,
                        'user_id':kwargs.get('user_id'),
                        'user_name':kwargs.get('user_name'),
                    })
                else:
                    self.env['pos.cash.in.out'].create({
                        'transaction_type': kwargs.get('type'),
                        'amount': -1*kwargs.get('amount'),
                        'reason': kwargs.get('name'),
                        'session_id': session_id.id,
                        'user_id':kwargs.get('user_id'),
                        'user_name':kwargs.get('user_name'),
                    })
        return {}

    @api.model
    def create_closing_cash_control(self, kwargs):
        session_id = self.search([('id', '=', kwargs.get('pos_session_id'))])
        if session_id:
            cash_box_id = session_id.cash_register_id.cashbox_end_id
            if cash_box_id:
                if len(cash_box_id.cashbox_lines_ids):
                    for cashbox_lines_id in cash_box_id.cashbox_lines_ids:
                        cashbox_lines_id.unlink()
                        
                cash_box_line_id = []
                for value in kwargs.get('cash_box_data'):
                    cash_box_line = {}
                    cash_box_line['coin_value'] = kwargs.get('cash_box_data')[value]
                    cash_box_line['number'] = int(value)
                    cash_box_line['cashbox_id'] = cash_box_id.id
                    cashbox_line_id = self.env['account.cashbox.line'].create(cash_box_line)
                    cash_box_line_id.append(cashbox_line_id.id)
                
                cash_box_id.cashbox_lines_ids = [cash_box_line_id] 
                return True
            else: 
                cash_box_obj = self.env['account.bank.statement.cashbox']
                vals = {}
                vals['cashbox_lines_ids'] = [[0, 0, {'coin_value': kwargs.get('cash_box_data')[value], 'number': int(value)}] for value in kwargs.get('cash_box_data')]
                result = cash_box_obj.create(vals)
                session_id.cash_register_id.cashbox_end_id = result.id
                if session_id.state == 'opened':
                    self.create_closing_entry(kwargs, session_id)
                return True
        else:
            return False  
    
    def create_closing_entry(self, kwargs, session_id):
        cash_box_id = session_id.cash_register_id.cashbox_end_id
        if cash_box_id:
            if len(cash_box_id.cashbox_lines_ids):
                for cashbox_lines_id in cash_box_id.cashbox_lines_ids:
                    cashbox_lines_id.unlink()
                    
            cash_box_line_id = []
            for value in kwargs.get('cash_box_data'):
                cash_box_line = {}
                cash_box_line['coin_value'] = kwargs.get('cash_box_data')[value]
                cash_box_line['number'] = int(value)
                cash_box_line['cashbox_id'] = cash_box_id.id
                cashbox_line_id = self.env['account.cashbox.line'].create(cash_box_line)
                cash_box_line_id.append(cashbox_line_id.id)
            
            cash_box_id.cashbox_lines_ids = [cash_box_line_id] 
            return True

class PosCashIn(models.Model):
    _name = 'pos.cash.in.out'
    _order = "id desc"
    _rec_name = 'session_id'

    transaction_type = fields.Selection([('cash_in', 'Cash In'), ('cash_out', 'Cash Out')])
    amount = fields.Float(string='Amount', digits=0)
    reason = fields.Char(string='Reason')
    session_id = fields.Many2one('pos.session', string="Pos Session")
    user_id = fields.Many2one('res.users', string="User")
    user_name = fields.Char(string="User")