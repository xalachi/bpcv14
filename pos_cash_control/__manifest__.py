# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Pos Cash Control",
  "summary"              :  """POS Cash Control allows you to manage the cash controls in the running POS session""",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """Pos Cash Control
  Pos Cash Alert
  Manage Cash
  Cash Management
  Cash Control Management
  Cash Box Closing Balance
  Payments Pos Session
  Closing Cash
  Track Cash In Cash Out
  """,
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_cash_control&custom_url=/pos/auto",
  "depends"              :  ['point_of_sale'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/template.xml',
                             'views/pos_config.xml',
                             'views/pos_cash_in_out.xml',
                            ],
  "qweb"                 :  [
                              'static/src/xml/pos.xml',
                            ],
  "images"               :  ['static/description/banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  49,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
