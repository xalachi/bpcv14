# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class Picking(models.TransientModel):
    _inherit = "res.config.settings"

    auto_send_mail_invoice = fields.Boolean("Auto Send Mail Invoice",related='company_id.auto_send_mail_invoice',readonly=False)
    auto_validate_invoice = fields.Boolean("Auto Validate Invoice",related='company_id.auto_validate_invoice',readonly=False)


class Company(models.Model):
    _inherit = 'res.company'

    auto_validate_invoice = fields.Boolean("Auto Validate Invoice And Send Mail")
    auto_send_mail_invoice = fields.Boolean("Auto Send Mail Invoice")
