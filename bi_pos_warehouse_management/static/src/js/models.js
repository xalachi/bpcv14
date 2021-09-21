// bi_pos_warehouse_management js
odoo.define('bi_pos_warehouse_management.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var session = require('web.session');

	models.load_fields('product.product', ['type','quant_text']);

	models.load_models({
		model: 'stock.location',
		fields: ['name','complete_name'],
		domain: function(self) {
			return [['id', 'in', self.config.warehouse_available_ids]];
		},
		loaded: function(self, pos_custom_location) {
			self.pos_custom_location = pos_custom_location;
			self.loc_by_id = {};
			pos_custom_location.forEach(function(loc) {
				self.loc_by_id[loc.id] = loc;
			});
		},
	});

	models.load_models({
		model: 'product.product',
		fields: ['name','type','quant_text'],
		domain: null,
		loaded: function(self, prods) {
			self.prods = prods;
			self.prod_with_quant = {};
			prods.forEach(function(prd) {
				prd.all_qty = JSON.parse(prd.quant_text);
				self.prod_with_quant[prd.id] = prd.all_qty;
				
			});
		},
	});
	


	var OrderSuper = models.Order;
	models.Order = models.Order.extend({
		init: function(parent,options){
			this._super(parent,options);
			this.order_products = this.order_products || {};
			this.prd_qty = this.prd_qty || {};
		},

		export_as_JSON: function() {
			var self = this;
			var loaded = OrderSuper.prototype.export_as_JSON.call(this);
			loaded.order_products = self.order_products || {};
			loaded.prd_qty = self.calculate_prod_qty() || {};
			return loaded;
		},

		init_from_JSON: function(json){
			OrderSuper.prototype.init_from_JSON.apply(this,arguments);
			this.order_products = json.order_products || {};
			this.prd_qty = json.prd_qty || {};
		},

		calculate_prod_qty: function () {
			var self = this;
			var products = {};
			var order = this.pos.get_order();
			if(order){
				var orderlines = order.get_orderlines();
				var config_loc = self.pos.config.stock_location_id[0];
				if(order.prd_qty  == undefined){
					order.prd_qty = {};
				}
				if(order.order_products  == undefined){
					order.order_products = {};
				}
			
				if(orderlines.length > 0 && self.pos.config.display_stock_pos){
					orderlines.forEach(function (line) {
						var prod = line.product;

						order.order_products[prod.id] = self.pos.prod_with_quant[prod.id];
						var loc = line.stock_location_id;
						if(!loc){
							loc = config_loc;
						}
						if(prod.type == 'product'){
							if(products[prod.id] == undefined){
								products[prod.id] =  [{ 
									'loc' :loc,
									'line' : line.id,
									'name': prod.display_name,
									'qty' :parseFloat(line.quantity)
								}];
							}
							else{
								let found = $.grep(products[prod.id], function(v) {
									return v.loc === loc;
								});
								if(found){
									products[prod.id].forEach(function (val) {
										if(val['loc'] == loc){
											if(val['line'] == line.id){
												val['qty'] = parseFloat(line.quantity);
											}else{
												val['qty'] += parseFloat(line.quantity);
											}
										}
									});	
								}
								if(found.length == 0){
									products[prod.id].push({ 
										'loc' :loc,
										'line' : line.id,
										'name': prod.display_name,
										'qty' :parseFloat(line.quantity)
									}) 
								}
							}	
						}
					});	
				}		
				order.prd_qty = products;
			}
			
			return products;
		},
	});

	var _super_orderline = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
		initialize: function(attr,options){
			_super_orderline.initialize.call(this,attr,options);
			this.stock_location_id = this.stock_location_id || false;
		},

		export_as_JSON: function(){
			var json = _super_orderline.export_as_JSON.call(this);
			json.stock_location_id = this.stock_location_id;
			return json;
		},
		init_from_JSON: function(json){
			_super_orderline.init_from_JSON.apply(this,arguments);
			this.stock_location_id = json.stock_location_id;
		},
	});

});
