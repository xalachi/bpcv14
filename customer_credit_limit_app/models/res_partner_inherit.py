# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
import werkzeug.urls

class res_pertner(models.Model):
    _inherit = "res.partner"
    
    credit_limit = fields.Integer(string="Customer Credit Limit")
        
    _sql_constraints = [
        ('customer_internal_ref', 'unique (ref)', 'Customer Internal Reference must be unique !')
    ]
