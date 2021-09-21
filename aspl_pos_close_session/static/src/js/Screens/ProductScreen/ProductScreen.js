odoo.define('aspl_pos_close_session.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState, useRef } = owl.hooks;
    var rpc = require('web.rpc');

    const ProductScreenInherit = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
            }

            showCashBoxOpening() {
                if(this.env.pos.config.enable_close_session && this.env.pos.config.cash_control){
                    return false;
                }else if(!this.env.pos.config.enable_close_session && this.env.pos.pos_session.state == 'opening_control'){
                    return true;
                }else{
                    return false;
                }
            }

        };

    Registries.Component.extend(ProductScreen, ProductScreenInherit);

    return ProductScreen;
});
