# -*- coding: utf-8 -*-
{
    "name" : "Odoo POS Reservation Order",
    "author": "Edge Technologies",
    "version" : "14.0.1.0",
    "category" : "Point of Sale",
    'summary': 'pos order reservation pos reserve order reservation in pos reservation on point of sale pos order booking on pos booking order reserving in pos order reserve in pos reserve pos items pos item reserve pos order booking pos order booking order on pos',
    "description": """
        This app used to Reserve Order in POS. You can pay initial amount and reserve the order, cancel any item from the reserve order, update delivery date, pay the remaining amount later and confirm the whole order.
        Odoo POS Order Reservation management with Odoo. POS order Reserve with Odoo. Order Reservation on POS with Odoo. POS reserve Order in Odoo. Odoo point of sale Order Reservation management with Odoo. point of sale order Reserve with Odoo. Order Reservation on point of sale with Odoo. point of sale reserve Order in Odoo.Order Reservation on POS Order reservation POS order reservation on Odoo.Order Reservation on point of sale Order reservation point of sale order reservation on Odoo.
pos order reserve
pos reserve order
order resvervation in pos
point of sales order reserve
pos order booking 
pos order in draft
pos draft order
pos save order
pos booking order
pos book order
order reserving in pos
order reserve in pos
reserve pos order
draft pos order
save draft pos order
reserve pos items
pos item reserve
pos order booking
book pos order
booking order on pos

    """,
    "license" : "OPL-1",
    "depends" : ['base','point_of_sale','account'],
    "data": [
        'views/pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/reserve_order_xml.xml',
    ],
    "auto_install": False,
    "price": 20,
    "currency": 'EUR',
    "installable": True,
    "live_test_url":'https://youtu.be/FkuzfnM-Doc',
    "images":["static/description/main_screenshot.png"],
    "category" : "Point of Sale",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
