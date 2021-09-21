// BiProductScreen js
odoo.define('bi_pos_barcode_lot_selection.ReceiptScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ReceiptScreen = require('point_of_sale.ReceiptScreen');

	const BiLotReceiptScreen = (ReceiptScreen) =>
		class extends ReceiptScreen {
			constructor() {
				super(...arguments);
				let self = this;
				const order = this.currentOrder;
				let orderlines = order.get_orderlines();
				let products = order.calculate_prod_qty();
				let config = this.env.pos.config;		
				let config_loc = config.stock_location_id[0];
				$.each(orderlines, function( i, line ){
					let prd = line.product;
					if (prd.type == 'product'){
						let loc = line.stock_location_id;
						if(!loc){
							loc = config_loc;
						}
						let loc_qty = self.env.pos.prod_with_quant[prd.id];
						if(loc_qty && self.env.pos.prod_with_quant[prd.id][loc]){
							self.env.pos.prod_with_quant[prd.id][loc] -= line.quantity;
						}
					}
				});
			}
		};

	Registries.Component.extend(ReceiptScreen, BiLotReceiptScreen);

	return ReceiptScreen;

});
