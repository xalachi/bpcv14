odoo.define('bi_pos_warehouse_management.ProductScreen', function(require) {
	"use strict";

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	let rpc = require('web.rpc');
	const { useListener } = require('web.custom_hooks');
	const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
	const { useState } = owl.hooks;
	const ProductScreen = require('point_of_sale.ProductScreen'); 

	const BiProductScreen = (ProductScreen) =>
	class extends ProductScreen {
		constructor() {
			super(...arguments);
		}

		async _clickProduct(event) { 
			let self = this;
			const product = event.detail;
			let order = self.env.pos.get_order();
			let orderlines = order.get_orderlines();
			let partner_id = self.env.pos.get_client();
			let location = self.env.pos.config.stock_location_id;
			let other_locations = self.env.pos.pos_custom_location;

			let config_loc = self.env.pos.config.stock_location_id[0];
			let loc_qty = self.env.pos.prod_with_quant[product.id];
			let config_loc_qty = loc_qty[config_loc] || 0;
			let product_id = product['id'];
			let result = 0;
			// Deny POS Order When Product is Out of Stock
			if (product.type == 'product'  && self.env.pos.config.display_stock_pos)
			{
				let products = order.calculate_prod_qty();
				let is_used = products[product.id] || false;
				let used_qty = 0;
				if(is_used){
					let found = $.grep(products[product.id], function(v) {
						return v.loc === config_loc;
					});
					if(found.length >0){
						used_qty = found[0].qty;
					}
				}
				if(config_loc_qty <= 0 || config_loc_qty <= used_qty){
					await this.rpc({
						model: 'stock.quant',
						method: 'get_product_stock',
						args: [partner_id, location, other_locations, product.id],
					}).then(function(output) {
						result = output[1];
					});

					const { confirmed } = await this.showPopup('ConfirmPopup', {
						title: this.env._t('Out of Stock !!'),
						body: this.env._t('The product you have selected is out of stock'),
						cancelText: this.env._t('Cancel'),
						confirmText: this.env._t('CheckAvailability'),
						'product': product, 
						'result':result,
					});
					if (confirmed) {
						self.showPopup('PosStockWarehouse', {
							'product': product,
							'result': result,
						});
					}
					
				}
				else {
					super._clickProduct(event);
				}
				
			}else {
				super._clickProduct(event);
			}
		}

		_onClickPay() {
			let self = this;
			let order = self.env.pos.get_order();
			let orderlines = order.get_orderlines();
			let products = order.calculate_prod_qty();
			let pos_config = self.env.pos.config;
			let prods = [];
			let call_super = true;

			if(pos_config.display_stock_pos){
				$.each(order.order_products, function( key, value ) {
					$.each(products, function( key1, value1 ) {
						if(key === key1) {
							$.each(value1, function( key3, value3 ) {
								let loc = value3['loc'];
								let qty = value3['qty'];
								let prd = value3['name'];
								let ol = value3['line'];
								if(self.env.pos.loc_by_id && self.env.pos.loc_by_id[loc] && self.env.pos.loc_by_id[loc]['complete_name'])
								{
									let loc_name = self.env.pos.loc_by_id[loc]['complete_name'];
									let loc_list = [];
									$.each(value, function( k, v ) {
										if(self.env.pos.loc_by_id[k] && self.env.pos.loc_by_id[k]['complete_name']){
											let l_nm = self.env.pos.loc_by_id[k]['complete_name'];
											loc_list.push([l_nm,v]);
										}
									});
									if(qty > value[loc]){
										let wrning = prd + ': has only '+value[loc]+' Qty for location:"'+loc_name+'", So Please Update Quantity or select from other location.';
										let odrln = order.get_orderline(ol);
										odrln.set_quantity(value[loc]);
										call_super = false;
										self.showPopup('PosOutOfStock', {
											'title': self.env._t('Out of Stock'),
											'warning':  self.env._t(wrning),
											'loc_list' : loc_list,
										});
										return;
									}

								}

								
							});
						} 
					});
				});

				$.each(orderlines, function( key, value ) {
						let prod_qty = self.env.pos.prod_with_quant[value.product.id];
						let config_loc = self.env.pos.config.stock_location_id[0];
						let config_loc_qty = prod_qty[config_loc] || 0;
						let loc_name = self.env.pos.loc_by_id[config_loc]['complete_name'];
						let loc_list = [];
						$.each(prod_qty, function( k, v ) {
							if(self.env.pos.loc_by_id[k] && self.env.pos.loc_by_id[k]['complete_name']){
								let l_nm = self.env.pos.loc_by_id[k]['complete_name'];	
								loc_list.push([l_nm,v]);
							}
							
						});	

						if(value.stock_location_id == false && config_loc_qty < value.quantity){
							let wrning = value.product.display_name + ': has only '+ config_loc_qty +' Qty for location:"'+loc_name+'", So Please Update Quantity or select from other location.';
							let odrln = order.get_orderline(value.id);
							odrln.set_quantity(config_loc_qty);
							call_super = false;
							self.showPopup('PosOutOfStock', {
								'title': self.env._t('Out of Stock'),
								'warning':  self.env._t(wrning),
								'loc_list' : loc_list,
							});
							return;
						}
					});
			}
			
			if(call_super){
				super._onClickPay();
			}	
		}

	};

	Registries.Component.extend(ProductScreen, BiProductScreen);

	return ProductScreen;
});