odoo.define('bi_pos_hr_expense.Expensepopup', function(require) {
    'use strict';

    const confirmPopup = require('point_of_sale.ConfirmPopup');
    
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    class Expensepopup extends confirmPopup {
        constructor() {
            super(...arguments);
        }
        
    };
    Expensepopup.template = 'Expensepopup';
    Expensepopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Confirm ?',
        body: '',
    };

    Registries.Component.add(Expensepopup);

    return Expensepopup;
});
