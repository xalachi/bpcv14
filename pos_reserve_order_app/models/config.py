# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
from functools import partial
import psycopg2
import pytz
import odoo.addons.decimal_precision as dp



class POSConfigInherit(models.Model):
	_inherit = 'pos.config'
	
	enable_reservation = fields.Boolean('Allow Reserve Order')
	reservation_location = fields.Many2one('stock.location','Location to store reserve products',domain=[('usage', '!=', 'view')])
	cancel_charge_type = fields.Selection([('percentage', "Percentage"), ('fixed', "Fixed")], string='Cancellation Charge Type', default='fixed')
	cancel_charges = fields.Float('Cancellation Charges')
	cancel_charges_product = fields.Many2one('product.product','Cancellation Charges Product',domain=[('type', '=', 'service'),('available_in_pos','=',True)])
	reserve_charge_type = fields.Selection([('percentage', "Percentage"), ('fixed', "Fixed")], string='Reservation Charge Type', default='fixed')
	min_reserve_charges = fields.Float('Minimum amount to reserve order')
	last_days = fields.Integer('Load Reserve Orders for Last')