/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_cash_control.pos_cash_control', function (require) {
    "use strict";
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t  = core._t;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    class CashControlButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showPopup('CashControlPopupWidget', {
                title: this.env._t('Cash Control'),
            });
        }
    }
    CashControlButton.template = 'CashControlButton';
    ProductScreen.addControlButton({
        component: CashControlButton,
        condition: function() {
            return this.env.pos.config.cash_control && this.env.pos.config.enable_pos_cash_control;
        },
    });
    Registries.Component.add(CashControlButton);

    class CashControlPopupWidget extends AbstractAwaitablePopup {
        click_cash_in(event){
            this.showPopup('CashInPopupWidget', {
                'title': this.env._t('Cash IN'),
            });
        }
        click_cash_out(event){
            this.showPopup('CashOutPopupWidget', {
                'title': this.env._t('Cash OUT'),
            });
        }
        click_set_closing_cash(event){
            this.showPopup('SetClosingBalancePopupWidget', {
                'title': this.env._t('Set Closing Balance'),
            });
        }
        click_show_payments(event){
            var self = this;
            var session_details = {
                'pos_session_id' : self.env.pos.pos_session.id,
            }
            rpc.query({
                model: 'pos.session',
                method: 'get_payments',
                args: [session_details],
            }).then(function (result) {
                self.showPopup('PaymentsPopupWidget', {
                    'title': self.env._t('Payments'),
                    'payments': result
                });
            }).catch(function (error) {
                console.log("---fail---",error)
                self.showPopup('ErrorPopup', {
                    title: self.env._t('Unable to Show Payments'),
                    body: self.env._t('Unable to show Payments, due to some error. Please check internet connection.'),
                });
            });     
        }
    }
    CashControlPopupWidget.template = 'CashControlPopupWidget';
    Registries.Component.add(CashControlPopupWidget);

    class CashInPopupWidget extends AbstractAwaitablePopup {
        remove_class(){
            $('#reason').removeClass("text_shake");
            $('#amount').removeClass("text_shake");
        }
        click_confirm(event){
            var self = this;
            if (!$('#reason').val().replace(/^\s+|\s+$/g, "").length != 0) {
                $('#reason').addClass("text_shake");
                return
            }
            if (!$('#amount').val().replace(/^\s+|\s+$/g, "").length != 0) {
                $('#amount').addClass("text_shake");
                return
            }
            
            var reason = $('#reason').val()
            var amount = $('#amount').val()
            var user_id = false
            var user_name = false
            if (self.env.pos.config.module_pos_hr)
                user_name = self.env.pos.get_cashier().name
            else
                user_id = self.env.pos.user.id

            var cash_in_details = {
                'name' : reason,
                'amount' : amount,
                'user_id' : user_id,
                'user_name' : user_name,
                'pos_session_id' : self.env.pos.pos_session.id,
                'type': 'cash_in',
            }
            rpc.query({
                model: 'pos.session',
                method: 'create_check_in_out',
                args: [cash_in_details],
            }).then(function (result) {
                if (result && result.unable_to_create){
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Unable to Cash IN'),
                        body: self.env._t(result.message),
                    });
                } else {
                    self.showPopup('TransactionPopup', {
                        title: self.env._t('Success'),
                        body: self.env._t("Successfully Created Cash In")
                    });
                }
            }).catch(function (error) {
                console.log("---fail---",error)
                self.showPopup('ErrorPopup', {
                    title: self.env._t('Unable to Cash In'),
                    body: self.env._t('Unable to Cash In, due to some error. Please check internet connection.'),
                });
            });
        }
        click_back(event){
            this.showPopup('CashControlPopupWidget', {
                title: this.env._t('Cash Control'),
            });
        }
    }
    CashInPopupWidget.template = 'CashInPopupWidget';
    Registries.Component.add(CashInPopupWidget);

    class CashOutPopupWidget extends AbstractAwaitablePopup {
        remove_class(){
            $('#reason_cash_out').removeClass("text_shake");
            $('#amount_cash_out').removeClass("text_shake");
        }
        click_confirm(event){
            var self = this;
            if (!$('#reason_cash_out').val().replace(/^\s+|\s+$/g, "").length != 0) {
                $('#reason_cash_out').addClass("text_shake");
                return
            }
            if (!$('#amount_cash_out').val().replace(/^\s+|\s+$/g, "").length != 0) {
                $('#amount_cash_out').addClass("text_shake");
                return
            }
            
            var reason = $('#reason_cash_out').val()
            var amount = $('#amount_cash_out').val()
            var user_id = false
            var user_name = false
            if (self.env.pos.config.module_pos_hr)
                user_name = self.env.pos.get_cashier().name
            else
                user_id = self.env.pos.user.id

            var cash_in_details = {
                'name' : reason,
                'amount' : amount*-1,
                'user_id' : user_id,
                'user_name' : user_name,
                'pos_session_id' : self.env.pos.pos_session.id,
                'type': 'cash_out',
            }
            rpc.query({
                model: 'pos.session',
                method: 'create_check_in_out',
                args: [cash_in_details],
            }).then(function (result) {
                if (result && result.unable_to_create){
                        self.showPopup('ErrorPopup', {
                            title: self.env._t('Unable to Cash OUT'),
                            body: self.env._t(result.message),
                        });
                } else {
                    self.showPopup('TransactionPopup', {
                        title: self.env._t('Success'),
                        body: self.env._t("Successfully Created Cash Out")
                    });
                }
            }).catch(function (error) {
                console.log("---fail---",error)
                self.showPopup('ErrorPopup', {
                    title: self.env._t('Unable to Cash Out'),
                    body: self.env._t('Unable to Cash Out, due to some error. Please check internet connection.'),
                });
            });
        }
        click_back(event){
            this.showPopup('CashControlPopupWidget', {
                title: this.env._t('Cash Control'),
            });
        }
    }
    CashOutPopupWidget.template = 'CashOutPopupWidget';
    Registries.Component.add(CashOutPopupWidget);

    class SetClosingBalancePopupWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.line_count = 1
        }
        click_confirm(event){
            var self = this;
            var cash_box_data = self.get_cash_box_data()
            var cash_control_details = {
                'pos_session_id' : self.env.pos.pos_session.id,
                'cash_box_data': cash_box_data,
            }
            rpc.query({
                model: 'pos.session',
                method: 'create_closing_cash_control',
                args: [cash_control_details],
            }).then(function (result) {
                if (result){
                    self.showPopup('TransactionPopup', {
                        title: self.env._t('Success'),
                        body: self.env._t("Successfully Created Closing Balance")
                    });
                }
                else{
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Unable to Set Closing Balance'),
                        body: self.env._t("Unable to Set Closing Balace, due to some error. Please check internet connection.")
                    });
                }
            }).catch(function (error) {
                console.log("---fail---",error)
                self.showPopup('ErrorPopup', {
                    title: self.env._t('Unable to Set Closing Balance'),
                    body: self.env._t("Unable to Set Closing Balace, due to some error. Please check internet connection.")
                });
            });
        }
        get_cash_box_data(){
            var records = {}
            var keys = []
            var values = []
            $('.bill_count').each(function(i, obj) {
                keys.push(obj.value)
            });
            $('.bill_value').each(function(i, obj) {
                values.push(obj.value)
            });

            var i;
            for (i = 0; i < keys.length; i++) {
                records[parseInt(keys[i])] = parseInt(values[i])
            }
            return records
        }
        click_add_line(event){
            var line_count = this.line_count
            var newRow=document.getElementById('closing-balance').insertRow();
            newRow.innerHTML=`
             <tr class="bill-line" line_id="`+ line_count +`" style="border-bottom: 1px solid;">		
                 <td style="padding: 1%;">
                     <input class="bill_count" type="number" value="0" bill_count_line_id="`+ line_count +`" type='text'/>
                 </td>
                 <td>
                     <input class="bill_value" type="number" value="0" bill_value_line_id="`+ line_count +`" type='text'/>
                 </td>
                 <td>
                     <span class="bill_total" bill_total_line_id="`+ line_count +`">0.0</span>
                 </td>
                 <td>
                     <i class="fa fa-times" bill_line_id="`+ line_count +`" aria-hidden="true"></i>
                 </td>
             </tr>`;
            newRow.querySelector('.bill_count').addEventListener('change',this.change_line_bill_count);
            newRow.querySelector('.bill_value').addEventListener('change',this.change_line_bill_value);
            newRow.querySelector('.fa.fa-times').addEventListener('click',this.remove_line);
            this.line_count = this.line_count + 1
        }
        change_line_bill_count(event){
            var line_id = $(this).attr('bill_count_line_id')
            var bill_count = this.value
            var bill_value = $("[bill_value_line_id="+ line_id + "]").val()
            var amount = bill_count*bill_value
            $("[bill_total_line_id="+ line_id + "]").html(amount)
            
            var total_amount = 0
            $('.bill_total').each(function(i, obj) {
                total_amount = total_amount + parseFloat(obj.innerHTML)
            });
            $(".total-amount-bills").html(total_amount)
        }
        change_line_bill_value(event){
            var line_id = $(this).attr('bill_value_line_id')
            var bill_value = this.value
            var bill_count = $("[bill_count_line_id="+ line_id + "]").val()
            var amount = bill_count*bill_value
            $("[bill_total_line_id="+ line_id + "]").html(amount)

            var total_amount = 0
            $('.bill_total').each(function(i, obj) {
                total_amount = total_amount + parseFloat(obj.innerHTML)
            });
            $(".total-amount-bills").html(total_amount)
        }
        remove_line(event){
            event.target.parentElement.parentElement.remove()
            var total_amount = 0
            $('.bill_total').each(function(i, obj) {
                total_amount = total_amount + parseFloat(obj.innerHTML)
            });
            $(".total-amount-bills").html(total_amount)
        }
        click_back(event){
            this.showPopup('CashControlPopupWidget', {
                title: this.env._t('Cash Control'),
            });
        }
    }
    SetClosingBalancePopupWidget.template = 'SetClosingBalancePopupWidget';
    Registries.Component.add(SetClosingBalancePopupWidget);

    class PaymentsPopupWidget extends AbstractAwaitablePopup {
        click_back(event){
            this.showPopup('CashControlPopupWidget', {
                title: this.env._t('Cash Control'),
            });
        }
    }
    PaymentsPopupWidget.template = 'PaymentsPopupWidget';
    Registries.Component.add(PaymentsPopupWidget);
    
    class TransactionPopup extends AbstractAwaitablePopup {}
    TransactionPopup.template = 'TransactionPopup';
    Registries.Component.add(TransactionPopup);
});