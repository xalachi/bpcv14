# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
	'name': 'Automatic Invoice from Delivery Order',
	'version': '14.0.0.3',
	'category': 'Accounting',
	'summary': 'Automatic invoice from picking Auto invoice from delivery order Auto create invoice from delivery auto invoice on delivered products auto invoice on deliver goods invoice by delivery auto invoice validate by picking auto invoice from DO invoice on delivery',
	'description': """
	
		odoo Automatic invoice from delivery Automatic invoice from delivery order,
		Automatic invoice from picking in odoo,
		Invoice generation when picking get done in odoo,
		Auto delivery invoice in odoo,
		Auto create invoice from delivery order in odoo,
		Auto invoice created when delivery order done in odoo,
		Auto invoice validate and send from picking in odoo,

""",
	'author': 'BrowseInfo',
	'website': 'https://www.browseinfo.in',
	'price': 25,
	'currency': "EUR",
	'depends': ['sale_management','stock',],
	'data': [
				'views/inherited_account_invoice.xml',
				'views/inherited_stock_picking.xml',
				'views/res_config_inherit.xml',
			],
	'demo': [],
	'js': [],
	'qweb': [],
	'installable': True,
	'auto_install': False,
	"images":['static/description/Banner.png'],
	'live_test_url':'https://youtu.be/DTlzWeLA_JA',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
