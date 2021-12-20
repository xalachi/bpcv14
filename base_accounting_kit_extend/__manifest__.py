# -*- coding: utf-8 -*-
{
    'name': "base_accounting_kit_extend",
    'summary': """
        Extensión del módulo base_accounting_kit""",
    'description': """
        1. Referencia en lista de pagos a conciliar
    """,
    'author': "Odoomatic",
    'website': "https://www.odoomatic.com/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.0.2',
    # any module necessary for this one to work correctly
    'depends': ['base','account','base_accounting_kit','l10n_cr_electronic_invoice'],

    # always loaded
    'data': [
        'views/account_bank_statement_views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
