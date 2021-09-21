odoo.define('bi_pos_warehouse_management.OrderWidget', function(require) {
	"use strict";

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { useListener } = require('web.custom_hooks');
	const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
	const { useState } = owl.hooks;
	const rpc = require('web.rpc');
	const OrderWidget = require('point_of_sale.OrderWidget');

	const BiOrderWidget = (OrderWidget) =>
	class extends OrderWidget {
		constructor() {
			super(...arguments);
		}
		
		mounted() {
			// this._super();
			this.order.orderlines.on('change', () => {
				let self = this;
				this.order.orderlines.each(function(line){
					let order = self.order;
					let orderlines = order.get_orderlines();
					let prod = line.product;
					if(order.order_products  == undefined){
						order.order_products = {};
					}
					if(prod.type == 'product'  && self.env.pos.config.display_stock_pos){
						order.order_products[prod.id] = self.env.pos.prod_with_quant[prod.id];
					}
					order.calculate_prod_qty();
					
				});
			});
		}
	};

	Registries.Component.extend(OrderWidget, BiOrderWidget);

	return OrderWidget;

});