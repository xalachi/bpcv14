# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
import werkzeug.urls


class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.onchange('partner_id')
    def _compute_total_customer_limit(self):
        sale_order_ids = self.env['sale.order'].search([('partner_id','=',self.partner_id.id),('state','=','sale'),('invoice_status','=','no')])
        sale_amount = 0
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            for total in sale_order_ids:
                sale_amount += total.currency_id._convert(total.amount_total, total.company_id.currency_id, self.company_id, total.date_order or fields.Date.today())
        else:
            for total in sale_order_ids:
                sale_amount += total.amount_total
            
        if self.partner_id:
            self.update({'sale_credit_limit_customer' : self.partner_id.credit_limit})
        else:
            self.update({'sale_credit_limit_customer':0.0})

    
    sale_credit_limit_customer = fields.Float(string="Credit Limit",compute="_compute_total_customer_limit")
    show_approve = fields.Boolean(string="Show Approve Sale",copy=False)
    company_currency_id = fields.Many2one('res.currency',string="Company Currency",related="company_id.currency_id")
    state = fields.Selection(selection_add=[
                            ('draft', 'Quotation'),
                            ('to_be_approved','Waiting For Approve'),
                            ('sent', 'Quotation Sent'),
                            ('sale', 'Sales Order'),
                            ('done', 'Locked'),
                            ('cancel', 'Cancelled')],
                            ondelete={
                            'draft': 'cascade',
                            'to_be_approved': 'cascade',
                            'sent': 'cascade',
                            'sale': 'cascade',
                            'done': 'cascade',
                            'cancel': 'cascade'})
    

    def action_approve_order(self):
        result = self.env['res.config.settings'].search([],order="id desc", limit=1)
        if result.sale_approve == 'after' :
            self.write({
                'state': 'sale',
                'date_order': fields.Datetime.now()
            })
            return True
        elif result.sale_approve == 'before' :
            res = super(sale_order, self).action_confirm()
            return res

        
    def action_confirm(self):
        result = self.env['res.config.settings'].search([],order="id desc", limit=1)
        date_today = fields.datetime.now().date()
        due_invoice = self.env['account.move'].search([('move_type','=','out_invoice'),('invoice_date_due','<',date_today),('state','=','posted'),('partner_id','=',self.partner_id.id)])

        if self.currency_id and self.currency_id != self.company_id.currency_id:
            amount = self.currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_order or fields.Date.today())
            total = self.partner_id.credit + amount
        else:
            total = self.partner_id.credit + self.amount_total

        flag = False
        res = True
        if result.sale_approve == 'after' :
            self.show_approve =True
            if self.sale_credit_limit_customer <= total:
                res = super(sale_order, self).action_confirm()
                self.state = 'to_be_approved'
                flag = True
            if result.due_date_check :
                if due_invoice and flag == False:
                    res = super(sale_order, self).action_confirm()
                    self.state = 'to_be_approved'
                    flag = True
            if flag == False :
                res = super(sale_order, self).action_confirm()
            return res
        elif result.sale_approve == 'before' :
            if self.sale_credit_limit_customer <= total:
                self.state = 'to_be_approved'
                flag = True
            if result.due_date_check :
                if due_invoice and flag == False:
                    self.state = 'to_be_approved'
                    flag = True
            if flag == False :
                res = super(sale_order, self).action_confirm()
        return res
