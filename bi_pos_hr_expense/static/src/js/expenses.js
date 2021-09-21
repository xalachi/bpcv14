odoo.define('bi_pos_hr_expense.expenses', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class Expenses extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        get worngInput(){
            var self = this;
            var vals_list = {};
            var e = document.getElementById("note_select");
            var pro_id = e.options[e.selectedIndex].value || false;
            var pro_id1 = e.options[e.selectedIndex].text;
            var order = this.env.pos.get_order();
            
            
            if(!pro_id){
                this.showPopup('ErrorPopup', {
                title: _('Invalide order'),
                body: _('Please select Product')
                });
            }

            else if(! $(".field_value_name").val()){
                this.showPopup('ErrorPopup', {
                title: _('Invalide order'),
                body: _('Please enter Name')
                });
            }
            else{
                vals_list.product_id = parseInt(pro_id);
                vals_list.name = $(".field_value_name").val();
                vals_list.unit_amount = this.env.pos.db.get_product_by_id(pro_id).standard_price;
                vals_list.quantity = $(".field_value_qty").val();
                vals_list.employee_id = this.env.pos.get_cashier().id;
                vals_list.product_uom_id = this.env.pos.db.get_product_by_id(pro_id).uom_id[0];
            
                this.rpc({
                    model: 'hr.expense',
                    method: 'create',
                    args:[vals_list]
                });
                this.showPopup('ConfirmPopup', {
                title: _('Order Created'),
                body: _('Order Created')
                });
            }
        }
        async onClick() {
            
            const { confirmed } = await this.showPopup('Expensepopup', {
                title: this.env._t("Create Expense")
            });
            if(confirmed){
                return  this.worngInput;
            }

        }
    }

    Expenses.template = 'Expenses';

    ProductScreen.addControlButton({
        component: Expenses,
        condition: function() {
            return this.env.pos.config.module_pos_hr;
        },
    });

    Registries.Component.add(Expenses);

    return Expenses;
});
            
        
        


