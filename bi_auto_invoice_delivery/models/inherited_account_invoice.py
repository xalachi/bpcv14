# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.move"

    picking_id = fields.Many2one('stock.picking','Picking')
    sale_id  =  fields.Many2one('sale.order', 'Sale Origin')


    