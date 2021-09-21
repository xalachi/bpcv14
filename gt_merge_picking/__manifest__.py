# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    Globalteckz                                                              #
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)        #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU Affero General Public License for more details.                      #
#                                                                             #
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################
{
    'name': "Merge multiple Picking",
    'summary': """This module will help you to handle large picking and merge in single picking merge picking merge delivery order merge receipts merge merge stock picking Merge Picking list merge shipments Merge orders combine picking merge transfer merge internal transfer picking merger merge operations merge multiple delivery merge DO merger merge picking merge delivery merge receipts merge stock picking merge invoice merge sales order merge purchase merge order line merge order merger picking merger vendor bill merge DO merge SO merge PO merge customer invoice merge transfer""",
    'description': """
merge picking
picking merge
merging
pick list merge
picklist merge
    """,
    'author': "Globalteckz",
    'website': "http://www.globalteckz.com",
    'category': 'Uncategorized',
    'version': '14.0.1',
    "license" : "Other proprietary",
    'images': ['static/description/banner.png'],
    "price": "39.00",
    "currency": "EUR",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/merge_picking.xml'

    ],

}
