odoo.define('aspl_pos_close_session.chrome', function (require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    var session = require('web.session');
    const { useListener } = require('web.custom_hooks');
    var rpc = require('web.rpc');
    var framework = require('web.framework');

    const ChromeInherit = (Chrome) =>
        class extends Chrome {
            constructor() {
                super(...arguments);
            }

            get startScreen() {
                if (this.env.pos.config.enable_close_session && this.env.pos.config.cash_control && this.env.pos.pos_session.state == 'opening_control') {
                    return { name: 'CashControlScreen'};
                } else {
                    return super.startScreen;
                }
            }

            async generateZReport(){
                return this.env.pos.do_action('aspl_pos_close_session.pos_z_report',{additional_context:{
                           active_ids:[this.env.pos.pos_session.id],
                }});
            }

            async closePosSession(){
                var params = {
                    model: 'pos.session',
                    method: 'custom_close_pos_session',
                    args:[this.env.pos.pos_session.id]
                }
                return this.rpc(params, {async: false}).then(function(res){});
            }

            async generateReceipt(){
                var self = this;
                if(self.env.pos.config.other_devices){
                    var report_name = "aspl_pos_close_session.pos_z_thermal_report_template";
                    var params = {
                        model: 'ir.actions.report',
                        method: 'get_html_report',
                        args: [[self.env.pos.pos_session.id], report_name],
                    }
                    rpc.query(params, {async: false})
                    .then(function(report_html){
                        if(report_html && report_html[0]){
                            self.env.pos.proxy.printer.print_receipt(report_html[0]);
                        }
                    });
                }
            }

            async _closePos() {
                if(this.env.pos.config.enable_close_session){
                    var self = this;
                    if(self.mainScreen.name != 'CloseCashControlScreen'){
                        const { confirmed } = await self.showPopup('CloseSessionPopup');
                        if(confirmed){
                            if(self.env.pos.config.cash_control){
                                self.get_session_data().then(function(session_data){
                                    self.showScreen('CloseCashControlScreen',{'sessionData': session_data});
                                });
                                return;
                            }else{
                                framework.blockUI();
                                await self.closePosSession();
                                if(self.env.pos.config.z_report_pdf){
                                    await self.generateZReport();
                                }
                                if(self.env.pos.config.iface_print_via_proxy){
                                    await self.generateReceipt();
                                }
                                framework.unblockUI();
                                super._closePos();
                            }
                        }else{
                            return;
                        }
                    }else{
                        await super._closePos();
                    }
                }
                else{
                    await super._closePos();
                }
            }

            get_session_data(){
                var self = this;
                var session_details = false;
                return new Promise(function (resolve, reject) {
                    var params = {
                        model: 'pos.session',
                        method: 'search_read',
                        domain: [['id', '=', self.env.pos.pos_session.id]],
                    }
                    rpc.query(params, {}).then(function (data) {
                        if(data){
                            session_details = data;
                            resolve(session_details);
                        } else {
                            reject();
                        }
                   }, function (type, err) { reject(); });
                });
            }
    }
    Registries.Component.extend(Chrome, ChromeInherit);

    return Chrome;
});
