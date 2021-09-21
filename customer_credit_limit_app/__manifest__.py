# -*- coding: utf-8 -*-

{
    "name" : "Customer Credit Limit",
    "author": "Edge Technologies",
    "version" : "14.0.1.0",
    "live_test_url":'https://youtu.be/6Gk6vhIBF2s',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Credit Limit for Customer Credit Limit credit limit for customer Credit Limit with Due Amount Warning Customers Credit Limit check Customer Credit Limit Exceeded customer Credit Limit on Hold customer account limit credit account limit partner credit limit',
    "description": """
    
  This app used to set credit limit for each customer, based on that approval is required on sales order. configuration is available to create delivery order before or after credit limit approval. Customer Due invoice approval on sales order also possible with this odoo module. 
Credit Limit for Customer Credit Limit credit limit for individual customers cc hold cc payment cc Customer Credit Limit with Due Amount Warning credit limit feature customer credit limit with warning Delivery Customers Credit Limit check customer credit limit credit limit amount 
Customer Credit Limit Exceeded Credit Limit Customer on Credit Limit Hold Credit Limit on Hold customer account limit credit account limit 
credit account hold hold credit account 

    
    """,
    "license" : "OPL-1",
    "depends" : ['base','sale_management','account','stock','sale_stock'],
    "data": [
        'security/groups.xml',
        'views/config_views.xml',
        'views/sale_view_inherit.xml',
        'views/res_partner_inherit.xml',
        'views/picking_inherit_view.xml',
        
    ],
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": 'EUR',
    "category" : "Sales",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
