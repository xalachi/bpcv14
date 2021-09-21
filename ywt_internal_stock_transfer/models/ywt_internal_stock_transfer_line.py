from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class YWTInternalStockTransferLine(models.Model):
    _name = 'ywt.internal.stock.transfer.line'
    
    product_id = fields.Many2one('product.product', string='Product', required=True, copy=False, ondelete='cascade')
    qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), copy=False, required=True, ondelete='cascade', default=1.0)
    quantity_on_hand = fields.Float(related='product_id.qty_available', string="Qty On Hand")
    internal_stock_transfer_id = fields.Many2one('ywt.internal.stock.transfer', ondelete='cascade', string='Internal Stock Transfer', required=True, copy=False)
