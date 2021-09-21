odoo.define('bi_pos_hr_expense.model', function (require) {
    "use strict";

var models = require('point_of_sale.models');

    models.load_models([{
    model:  'product.product',
    fields: ['name','id','standard_price'],
    domain: function(self){ return [['can_be_expensed','=','True'],['available_in_pos','=','True']]; },
    loaded: function(self, products){
        self.products =[];
        for(var i=0;i<products.length;i++){
            self.products[i] = products[i];
        }
    },
    }]);

    models.load_models([{
    model:  'hr.expense',
    fields: ['name',],
    domain: function(self){ return [['state','=','draft']]; },
    loaded: function(self){
        
        }
    }]);

});