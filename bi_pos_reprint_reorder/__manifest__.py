# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Orders Reprint and POS ReOrder in Odoo",
    "version" : "14.0.0.0",
    "category" : "Point of Sale",
    "depends" : ['base','sale','point_of_sale','pos_orders_list'],
    "author": "BrowseInfo",
    'summary': 'point of sale reprint and reorder reprint POS All Order list pos reorder pos repeat order pos order repeat point of sales reorders pos re-orders pos orders pos list orders pos reprint pos order reprint pos order reprint pos order receipt reprint pos receipt pos repeat orders',
    "description": """

    Purpose :-
    POS Reorder POS All Orders List POS reorder POS repeat order POS repeatorder pos
    point of sale reorder POS re-order point of sale re-order
    point of sale repeat-order point of sale repeat order point of sales re-order point of sales reorder
    point of sales repeat order point of sales repeat-order point of sales repeat order
    see the list of all the orders within a running POS Screen. It shows the Pos All Orders List on POS screen. View all POS order on screen. List all POS order on POS screen. Show order on POS, view all orders on POS, Display order on POS, View order on POS
    POS Orders Reprint POS reprint POS order reprint Reprint receipt from POS POS receipt reprint POS reprint receipt
    reprint pos orders Receipt print from POS POS order print POS order receipt print
    POS receipt print Receipt reprint from POS POS all order list POS show all order list

    POS Reorder POS All Orders List POS reorder POS repeat order POS repeatorder pos
    point of sale reorder POS re-order point of sale re-order point of sale repeat-order
    point of sale repeat order point of sales re-order point of sales reorder point of sales repeat order POS
    point of sales repeat-order point of sales repeat order

    point of sales reorder point of sales re-order point of sales re-order point of sales repeat-order point of sales
    point of sales repeat order point of sale re-order point of sale reorder point of sale repeat order point of sales
    point of sales repeat-order point of sale repeat order

    POS reorder POS re-order POS re-order POS repeat-order POS
    POS repeat order POS re-order POS reorder POS repeat order POS
    POS repeat-order POS repeat order point of sales
    Odoo point of sales doesn't allow to reprint order and re-order again once validate order, this Odoo apps allows to reprint all order again and re-order product from some specific order or re-order whole order again using POS touch screen. This Odoo modules help to see the list of all the orders in Point of sales screen, user can also see individual customers list of orders also from the same screen you can able to reorder/repeat order and reprint orders for same selected point of sales order easily.After installing this Odoo module POS user can also able to see all orders on screen in POS and reorder that same order and reprint it.

POS Orders Reprint POS reprint POS order reprint pos
    Reprint receipt from POS POS receipt reprint POS reprint receipt reprint pos orders
    Receipt print from POS POS order print POS order receipt print POS receipt print 
    Receipt reprint from POS POS all order list POS show all order list

    point of sale Reprint point of sale reprint point of sale order reprint point of sale
    Reprint receipt from point of sale point of sale receipt reprint point of sale reprint receipt reprint point of sale orders
    Receipt print from point of sale point of sale order print point of sale order receipt print point of sale receipt print 
    Receipt reprint from point of sale point of sale all order list point of sale show all order list


    point of sales Reprint point of sales reprint point of sales order reprint point of sales
    Reprint receipt from point of sales point of sale receipt reprint point of sales reprint receipt reprint point of sales orders
    Receipt print from point of sales point of sales order print point of sales receipt reprint point of sales receipt print print point of sales receipt print 
    Receipt reprint from point of sales point of sales all order list point of sales show all order list

point of sale orderlist pos orderlist odoo pos orders manage pos orders in odoo edit pos orders from pos screen 
    Purpose :- 
pos all list orders all orders pos all list orders pos pos all orders
all point of sales orders all orders list All pos orders list All pos order lists
pos All orders list pos all orders point of sales all orders point of sales order list 
pos orderlist pos all orderlist list of all order pos odoo manage all order list odoo manage pos all order list
see the list of all the orders within a running POS Screen. 

point of sale all list orders all orders point of sale all list orders point of sales point of sale all orders
all pos orders all orders list All point of sale orders list All point of sale order lists
point of sale All orders list point of sale all orders point of sales all orders point of sales order list 
point of sale orderlist point of sale all orderlist list of all order point of sale odoo manage all order list odoo manage point of sale all order list
see the list of all the orders within a running point of sale Screen. 

point of sales all list orders all orders point of sales all list orders point of sales point of sales all orders
all in one pos orders all orders list All point of sales orders list All point of sales order lists
point of sales All orders list point of sales all orders point of sales all orders point of sales order list 
point of sales orderlist point of sales all orderlist list of all order point of sales odoo manage all order list odoo manage point of sale all order list
see the list of all the orders within a running point of sales Screen. 
pos order list on pos point of sale order list on point of sales order list on point of sales

It shows the Pos All Orders List on POS screen View all POS order on screen. 
This apps helps to manage point of sale orders from the POS screen
List all POS order on POS screen Show order on POS view all orders on POS Display order on POS View order on POS
    
    """,
    "website" : "https://www.browseinfo.in",
    'price': '9',
    'currency': "EUR",
    "data": [
        'views/custom_pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/reprint_reorder.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url": "https://youtu.be/JDjZXnoBsm0",
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
