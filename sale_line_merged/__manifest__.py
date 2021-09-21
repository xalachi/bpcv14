# -*- coding: utf-8 -*-
{
    'name': 'Duplicate Sale Line Merged',
    'version': '13.0.1',
    'price': 15,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Sales',
    'summary': 'Sale order line merged if duplication,Duplicate product line merge,Same product line merger,Merger Order line ',
    'description': """ This module help to check/merged/combine lines if same product exist in sale order line.""",
    'author': 'Caliber Softwares',
    'website': 'http://calibersoftware.odoo.com/',
    'depends': ['sale'],
    'data': [
            'security/ir.model.access.csv',
            'views/sale_view.xml',
            'wizard/existing_sale_check.xml',
             ],
    'installable': True,
    'application': False,
    'images': ['static/description/img11.jpeg'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
