# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "All In One Barcode Scanner-Advance| Sale Order Barcode Scanner | Purchase Order Barcode Scanner | Invoice Barcode Scanner | Inventory Barcode Scanner | Bill Of Material Barcode Scanner | Scrap Barcode Scanner | Warehouse Barcode Scanner",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "14.0.2",

    "category": "Extra Tools",

    "summary": "Barcode Scanner Package,Sales Barcode Scanner,Purchase Barcode Scanner Module,Account Barcode Scanner,Stock Barcode Scanner,BOM Barcode Scanner,Request For Quotation Barcode Scanner,Bill Barcode Scanner,PO Barcode Scanner,RFQ Barcode Scanner Odoo",

    'description': """Do your time-wasting in sales, purchases, invoices, inventory, bill of material, scrap operations by manual product selection? So here are the solutions these modules useful do quick operations of sales, purchases, invoicing and inventory, bill of material, scrap using barcode scanner. You no need to select the product and do one by one. scan it and you do! So be very quick in all operations of odoo and cheers!

 All In One Barcode Scanner - Sales, Purchase, Invoice, Inventory, BOM, Scrap Odoo.
Operations Of Sales, Purchase Using Barcode, Invoice Using Barcode, Inventory Using Barcode, Bill Of Material Using Barcode, Scrap Using Barcode Module, Sales Barcode Scanner,Purchase Barcode Scanner, Invoice Barcode Scanner, Inventory Barcode Scanner,Bom Barcode Scanner, Single Product Multi Barcode Odoo.
 
 Barcode Scanner App,Package All in one barcode scanner,  Operations Of Sales, Purchase In Barcode Module, Invoice In Barcode, Inventory In Barcode, Bom In Barcode, Scrap Using Barcode, Single Product Multi Barcode, Sales Barcode Scanner,Purchase Barcode Scanner, Invoice Barcode Scanner, Inventory Barcode Scanner,Bom Barcode Scanner, Single Product Multi Barcode Odoo.


Add products by barcode    
Add products using barcode    

sales mobile barcode scanner
so barcode scanner
so mobile barcode scanner
sale mobile barcode scanner

po mobile barcode scanner
purchase order mobile barcode scanner
purchase order barcode scanner
po barcode scanner
    
inventory mobile barcode scanner    
stock mobile barcode scanner
inventory barcode scanner
stock barcode scanner

inventory adjustment mobile barcode scanner
stock adjustment mobile barcode scanner
inventory adjustment barcode scanner
stock adjustment barcode scanner

invoice barcode scanner
bill barcode scanner
credit note barcode scanner
debit note barcode scanner
invoice barcode mobile scanner
bill barcode mobile scanner
credit note barcode mobile scanner
debit note barcode mobile scanner""",

    "depends": [

                'purchase',
                'sale_management',
                'barcodes',
                'account',
                'stock',
                'mrp',
                'sale',
                'sh_product_qrcode_generator',
                "sh_product_multi_barcode",
    ],

    "data": [
        "security/ir.model.access.csv",
        "security/multi_barcode.xml",
        # Sale
        "views/sale/sale.xml",
        "views/sale/res_config_settings.xml",

        # Purchase
        "views/purchase/purchase.xml",
        "views/purchase/res_config_settings.xml",

        # Stock Picking
        "views/stock_picking/stock_picking.xml",
        "views/stock_picking/res_config_settings.xml",

        # Stock Move
        "views/stock_move/stock_move.xml",

        # Stock Inventory
        "views/stock_inventory/stock_inventory.xml",
        "views/stock_inventory/res_config_settings.xml",

        # Stock Scrap
        "views/stock_scrap/stock_scrap.xml",
        "views/stock_scrap/res_config_settings.xml",

        # Invoice
        "views/account/account.xml",
        "views/account/res_config_settings.xml",

        # MRP BOM
        "views/mrp_bom/mrp_bom.xml",
        "views/mrp_bom/res_config_settings.xml",
       
        # Global Search Document
        "views/global_doc_search/res_config_settings.xml",
        
        # Product
        "views/product/product.xml",
        # Assets
        "views/assets_backend.xml",                

    ],
    'qweb': ['static/src/xml/global_doc_search/global_doc_search.xml'],    
    'images': ['static/description/background.png', ],
    "installable": True,
    "application": True,
    "autoinstall": False,
    "price": 50,
    "currency": "EUR",
    "license": "OPL-1"
}
