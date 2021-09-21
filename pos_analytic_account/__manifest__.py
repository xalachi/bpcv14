{
    'name': "POS Analytic Account",
    'summary': """
       Use analytic account defined on POS configuration for POS orders and in Journal Entry""",

    'description': """
        Use analytic account defined on POS configuration for POS orders and in Journal Entry
    """,
    'price': 15.0,
    'currency': 'EUR',
    'author': 'Abdallah Mohamed',
    'license': 'OPL-1',
    'category': 'Sales/Point of Sale',
    'website': 'https://www.abdalla.work/r/Ohk',
    'support': 'https://www.abdalla.work/r/Ohk',
    'version': '14.0.1.1',
    'depends': [
        'point_of_sale',
        'account',
        'analytic'
    ],
    'data': [
        'views/pos_config.xml',
        'views/pos_order.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/module_screenshot.png',
    ],
    'installable': True,
}
