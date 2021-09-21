# -*- coding: utf-8 -*-

from odoo import fields,models,api, _
from ast import literal_eval
from odoo import SUPERUSER_ID
from odoo.http import request


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    due_date_check = fields.Boolean(string="Due Date",related="company_id.due_date_check",readonly=False)
    sale_approve = fields.Selection(related="company_id.sale_approve",readonly=False,string="Sale Approve")

class Company_Inherit(models.Model):
	_inherit = 'res.company'

	due_date_check = fields.Boolean(string="Due Date")
	sale_approve = fields.Selection([('before','Approve Before Delivery Order'),('after','Approve After Delivery Order')],default='after',string="Sale Approve")