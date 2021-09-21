# -*- coding: utf-8 -*-pack
# Part of YoungWings Technologies.See the License file for full copyright and licensing details.

{
    # Product Info
    'name': 'Internal Stock Transfer',
    'category': 'stock',
    'version': '14.0.0.1',
    'license': 'OPL-1',
    'sequence': 1,
    'summary': 'Internal Stock Transfer Module is helps you to transfer you stock between to internal location for the different warehouse.',
    
    # Writer
    'author': 'YoungWings Technologies',
    'maintainer': 'YoungWings Technologies',
    'website':'https://www.youngwingstechnologies.in/',
    'support':'youngwingstechnologies@gmail.com',
    
    # Dependencies
    'depends': ['stock'],
    
    # Views
    'data': ['security/ir.model.access.csv',
            'data/ir_sequence_data.xml',
            'views/internal_stock_transfer_views.xml',
            'views/stock_location_route_views.xml',
            'views/res_company_views.xml'],
            
    # Banner
    'images': ['static/description/banner.png'],
       
     # Technical        
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 15.50,
    'currency': 'USD',
}
