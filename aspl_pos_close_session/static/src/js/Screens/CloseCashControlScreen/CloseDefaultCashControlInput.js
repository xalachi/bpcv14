odoo.define('aspl_pos_close_session.CloseDefaultCashControlInput', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { debounce } = owl.utils;
    const { useState } = owl.hooks;

    class CloseDefaultCashControlInput extends PosComponent {
        constructor() {
            super(...arguments);
        }

        onKeyDown(e) {
            if(e.which == 9 || e.which == 13) {
                this.props.line.line_total = this.props.line.coin_value * this.props.line.number_of_coins;
                this.trigger('closing-main_total');
            }else if(e.which == 190){
               e.preventDefault();
            }
        }

        focusOut() {
            this.props.line.line_total = this.props.line.coin_value * this.props.line.number_of_coins;
            this.trigger('closing-main_total');
        }

    }

    CloseDefaultCashControlInput.template = 'CloseDefaultCashControlInput';

    Registries.Component.add(CloseDefaultCashControlInput);

    return CloseDefaultCashControlInput;
});

