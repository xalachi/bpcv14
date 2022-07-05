# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, format_date, get_lang

class Picking(models.Model):
    _inherit = "stock.picking"

    @api.depends('state')
    def _get_invoiced(self):
        for order in self:
            invoice_ids = self.env['account.move'].search([('picking_id','=',order.id)])
            order.invoice_count = len(invoice_ids)
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced')
    
    def button_view_invoice(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        work_order_id = self.env['account.move'].search([('picking_id', '=', self.id)])
        inv_ids = []
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        context = {
            'default_move_type': work_order_id[0].move_type,
        }
        action['domain'] = [('id', 'in', work_order_id.ids)]
        action['context'] = context
        return action

    
    def _action_done(self):
        action = super(Picking, self)._action_done()
        res_config = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        if self.state == 'done':            

            if self.picking_type_id.code == 'outgoing':
                inv_obj = self.env['account.move']
                invoice_lines =[]
                invoice_vals = []
                sale_order_line_obj = self.env['account.move.line']
                sale_order  =  self.env['sale.order'].search([('name', '=',self.origin )])
                journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
                if not journal:
                    raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

                if sale_order:
                    
                    inv_vals = {
                            'invoice_origin': self.origin,
                            'picking_id':self.id,
                            'move_type': 'out_invoice',
                            'ref': False,
                            'sale_id':sale_order.id,
                            'journal_id': journal.id,  
                            'partner_id': sale_order.partner_invoice_id.id,
                            'currency_id': sale_order.pricelist_id.currency_id.id,
                            'invoice_payment_term_id': sale_order.payment_term_id.id,
                            'fiscal_position_id': sale_order.fiscal_position_id.id or sale_order.partner_id.property_account_position_id.id,
                            'team_id': sale_order.team_id.id,
                            'invoice_date' : fields.Datetime.now().date(),
                        }
                    
                    if 'l10n_in_gst_treatment' in sale_order._model_fields and sale_order.l10n_in_company_country_code == 'IN':
                        inv_vals['l10n_in_reseller_partner_id'] = sale_order.l10n_in_reseller_partner_id.id
                        if sale_order.l10n_in_journal_id:
                            inv_vals['journal_id'] = sale_order.l10n_in_journal_id.id
                            inv_vals['l10n_in_gst_treatment'] = sale_order.l10n_in_gst_treatment
                        
                        
                    invoice = inv_obj.create(inv_vals)
                    
                    for so_line in  sale_order.order_line :
                        if not self.backorder_id:
                            if so_line.product_id.type == "service":
                                if so_line.product_uom_qty != so_line.qty_invoiced:
                                    if so_line.product_id.property_account_income_id:
                                        account_id = so_line.product_id.property_account_income_id
                                    elif so_line.product_id.categ_id.property_account_income_categ_id:
                                        account_id = so_line.product_id.categ_id.property_account_income_categ_id                    
                                    inv_line = {
                                            'name': so_line.name,
                                            'product_id': so_line.product_id.id,
                                            'product_uom_id': so_line.product_id.uom_id.id,
                                            'account_id': account_id.id,
                                            'display_type': so_line.display_type,
                                            'tax_ids': [(6, 0, so_line.tax_id.ids)],
                                            'move_id':invoice.id,
                                            'price_unit': so_line.price_unit,
                                            'sale_line_ids': [(4, so_line.id)],
                                            }
                                    if so_line.product_id.invoice_policy == 'delivery':
                                        inv_line['quantity']=so_line.qty_delivered
                                    else:
                                        inv_line['quantity']=so_line.product_uom_qty

                                    if inv_line['quantity']:
                                        invoice_vals.append((0,0,inv_line))
                              
                    for line in  self.move_ids_without_package :
                        if line.product_id.property_account_income_id:
                            account = line.product_id.property_account_income_id
                        elif line.product_id.categ_id.property_account_income_categ_id:
                            account = line.product_id.categ_id.property_account_income_categ_id
                        else:
                            account_search = self.env['ir.property'].search([('name', '=', 'property_account_income_categ_id')])
                            account = account_search.value_ref
                            account = account.split(",")[1]
                            account = self.env['account.account'].browse(account)
                        inv_line = {
                                'name': line.name,
                                'product_id': line.product_id.id,
                                'product_uom_id': line.product_id.uom_id.id,
                                'account_id': account.id,
                                'display_type': line.sale_line_id.display_type,
                                'tax_ids': [(6, 0, line.sale_line_id.tax_id.ids)],
                                'move_id':invoice.id,
                                'price_unit': line.sale_line_id.price_unit,
                                'sale_line_ids': [(4, line.sale_line_id.id)],
                                }
                        if line.product_id.invoice_policy == 'delivery':
                            inv_line['quantity']=line.quantity_done
                        else:
                            inv_line['quantity']=line.product_uom_qty

                        if inv_line['quantity']:
                            invoice_vals.append((0,0,inv_line))
                      
                    invoice.write({
                        'invoice_line_ids' : invoice_vals
                    })
                    if res_config.auto_validate_invoice == True :
                        invoice.action_post()
                    if res_config.auto_validate_invoice == True and res_config.auto_send_mail_invoice == True:
                        template = self.env.ref('account.email_template_edi_invoice', False)            
                        send = invoice.with_context(force_send=True,model_description='Invoice').message_post_with_template(int(template),email_layout_xmlid="mail.mail_notification_paynow")
        return action
    
    
    