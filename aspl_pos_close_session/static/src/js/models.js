odoo.define('aspl_pos_close_session.models', function (require) {
"use strict";

    var models = require('point_of_sale.models');

    models.load_fields("res.users", ['display_amount_during_close_session']);

    models.PosModel.prototype.models.push({
        model:  'opening.cash.prefill',
        domain: function(self){ return [['id', 'in', self.config.prefill_cash_ids]]; },
        fields: ['name', 'value'],
        loaded: function(self,cash_prefill){
            self.cash_prefill = cash_prefill;
        },
    });
});
