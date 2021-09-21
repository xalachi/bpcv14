# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Merge Sales And Purchase Order Odoo/OpenERP',
    'version': '14.0.0.3',
    'category': 'Sales',
    'summary': 'This module helps to merge sales and purchase orders with different options',
    'description': """
    
    odoo Merge sales order merge purchase orders merge order merge data mix order make together 
    Odoo Sales Order Merge Purchase Order Merge Merge Sale Order Merge purchases Order
    odoo merge orders merge so po merge po so merge orders merge
    odoo merging orders odoo orders merging
    Odoo Combine Invoices combine sales order combine purchase orders combine sales combine purchase combine orders
    Odoo Combine orders mix orders Combine po combine so

odoo Merge Picking list Merge Delivery Orders Merge Incoming shipments Merge Receipts Merge orders Merge 
    odoo merge Delivery Orders/Incoming Shipments in odoo merge shipment merge pickings merge combine orders
    odoo combine picking order combine delivery order combine combine incoming shipment combine
    odoo merge transfer merge shipment delivery merger shipment merger picking merger
    odoo merge operations merge internal transfer in odoo
    odoo merge DO receipt merger merge multiple picking merge multiple delivery merge multiple shipment
    odoo merge warhouse picking merge stock picking merge stock movement
    odoo merge stock picking merge stock picking merger stock picking combine stock picking combine
    odoo merge stock operation merge stock operation merger stock operation combine stock operation combine
    odoo merge operations merge operations merger operations combine operations combine merge DO merge
    odoo merge delivery order merge delivery order merger delivery order combine delivery order combine
    odoo merge receipt merge receipt merger receipt combine receipt combine
    odoo merge picking merge picking merger picking combine picking combine
Fusionner la liste de prélèvement, fusionner les commandes de livraison, fusionner les envois entrants, fusionner les reçus. Fusionner les commandesfusionner le transfert, fusionner l'expédition, fusionner les livraisons, fusionner les expéditions, choisir la fusion, fusionner les opérations, fusionner le transfert internefusionner DO, réception fusion, fusionner plusieurs picking, fusionner plusieurs livraisons, fusionner plusieurs envois, fusionner picking warhouse, fusionner picking stock, fusionner stock mouvement

Combinar lista de picking, fusionar pedidos de entrega, combinar envíos entrantes, combinar recibos. Fusionar pedidos
fusión de transferencia, combinación de envío, fusión de entrega, fusión de envío, fusión de picking, fusión de operaciones, combinación de transferencia interna
fusionar DO, fusionar recibos, fusionar selección múltiple, fusionar entregas múltiples, fusionar envíos múltiples, fusionar picking de warhouse, combinar stock picking, fusionar stock de movimientos


odoo Merge purchase list Merge sale Orders Merge sales order Merge purchase Merge purchase orders Merge 
    odoo merge sale order in odoo merge purchase merge purchases merge combine orders
    odoo combine purchases order combine sale order combine PO combine purchase order combine
    odoo merges sale order merger purchase order merger sale merger purchase merger
    odoo merge purchase picking merge sale transfer in odoo
    odoo merge SO receipt merger merge multiple Sales merge multiple purchase merge multiple orders
    odoo merge Sales process merge purchase process merge Sale purchase merge
    odoo merge Sales order merge purchase order merger sale purchase combine order sale combine

""",
    'author': 'BrowseInfo',
    "price": 35,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'images': [],
    'depends': ['sale_management', 'purchase','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_merge_view.xml',
        'views/sale_order.xml',
        'views/purchase_order_line_merge.xml',
        'views/sale_order_line_merge.xml',
        'views/res_config_settings.xml',
        'wizard/merge_same_vendor_po_views.xml',
        'wizard/merge_same_customer_so_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "live_test_url":'https://youtu.be/POTbKCOSrms',
    "images":["static/description/Banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
