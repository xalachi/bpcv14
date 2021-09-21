# -*- coding: utf-8 -*-
{
    "name": "Merge Sale and Purchase Order Lines",
    "author": "Edge Technologies",
    "version": '14.0.1.0',
    "live_test_url": "https://youtu.be/OZtSgs4qS8A",
    "images":['static/description/main_screenshot.png'],
    "summary": "Auto Merge Sale order line merge Purchase order line merger sale merge so merge po merge so lines merge po lines merge Sales Order merge lines for sales merge purchase line merge sale line combine order line duplicate product merge on line duplicate sale",
    "description": """ User have to merge sale order lines of similar product and quantity with auto merge and manual merge options. 

Merge Sale and Purchase
merge so  
merge so po 
Auto Merge Sale Order Lines
merge so lines merge po lines 
po lines merge 
sale order lines merge
so merge sale merge sale order merge purchase order merge purchase order line merge Odoo Sales Order Merge Sales Order Merge App
sales order line merge Sale Order Merge Merge Sale Orders Sale, Purchase and Invoice Merge  Merge Sale, Purchase and Invoice
merge sale purchase lines 
sale order lines merge purchase order lines merge 



merge sale order lines
merge lines




    """,
    "license" : "OPL-1",
    "depends": ['base','sale_management','account','purchase'],
    "data": [
            'security/ir.model.access.csv',
            'views/res_config_setting_view.xml',
            'views/sale_order_merge_wizard_view.xml',
            ],
    "installable": True,
    "auto_install": False,
    "price": 8,
    "currency": "EUR",
    "category": 'Sales',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
