from odoo import fields, models, api


class Company(models.Model):
    _inherit = 'res.company'
    
    bridge_transfer_location_id = fields.Many2one('stock.location', string="Bridge Location", domain=[('usage', 'in', ['internal', 'inventory', 'production', 'transit'])])
