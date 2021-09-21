# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "HR Expense from POS - POS HR Expense",
    "version" : "14.0.0.0",
    "category" : "Point of Sales",
    'summary': 'Point of Sales HR Expense point of sales expense with pos expense from pos expense with point of sale expense point of sale hr expense using pos with expense add expense from pos add use hr expense from pos',
    "description": """
    
   This odoo app helps user to create hr expenses from point of sale, user can select product and enter description and product quantity and create hr expenses from point of sale.
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 25,
    "currency": 'EUR',
    "depends" : ['base','hr_expense','point_of_sale'],
    "data": [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/expenses.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/5OnurFzBpEk',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
