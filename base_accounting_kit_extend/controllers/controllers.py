# -*- coding: utf-8 -*-
# from odoo import http


# class BaseAccountingKitExtend(http.Controller):
#     @http.route('/base_accounting_kit_extend/base_accounting_kit_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_accounting_kit_extend/base_accounting_kit_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_accounting_kit_extend.listing', {
#             'root': '/base_accounting_kit_extend/base_accounting_kit_extend',
#             'objects': http.request.env['base_accounting_kit_extend.base_accounting_kit_extend'].search([]),
#         })

#     @http.route('/base_accounting_kit_extend/base_accounting_kit_extend/objects/<model("base_accounting_kit_extend.base_accounting_kit_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_accounting_kit_extend.object', {
#             'object': obj
#         })
