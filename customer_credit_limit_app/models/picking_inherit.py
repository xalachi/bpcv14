from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class Picking_inherit(models.Model):
    _inherit = "stock.picking"

    sale_state = fields.Selection(related="sale_id.state", string='Sale Order Status')
    show_approve = fields.Boolean(string="Show Approve",related='sale_id.show_approve')

    def action_see_approve(self):
    	return