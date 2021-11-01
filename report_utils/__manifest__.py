# -*- coding: utf-8 -*-

{
    'name': 'Report Utils',
    'version': '1.0.0.5',
    'summary': """""",
    'description': """""",
    'category': 'Base',
    'author': 'iKreative',
    'website': "",
    'license': 'AGPL-3',

    'price': 5.0,
    'currency': 'USD',

    'depends': ['base'],

    'data': [
        'data/reports.xml',
        'security/ir.model.access.csv',
        'views/reporting_template.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}
