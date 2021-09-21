odoo.define('bi_pos_warehouse_management.PosStockWarehouse', function(require) {
	'use strict';

	const { useListener } = require('web.custom_hooks');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
	let pos_model=require('point_of_sale.models');      
	let location_id = null;

	class PosStockWarehouse extends AbstractAwaitablePopup {
		constructor() {
			super(...arguments);
			this.product = this.props.product;
			this.result = this.props.result;
			this.locations = this.result || [];
			this.location_id = null;
		}

		mounted(){
			let self = this;
			$('.warehouse-locations').each(function(){
				$('.raghav').removeClass('raghav');
				$(this).on('click',function (event) {
					if ( $(this).hasClass('raghav') )
					{
						$(this).removeClass('raghav');
						$(this).css("border", "1px solid #e2e2e2");
						self.location_id =  null;
					}
					else{
						$('.warehouse-locations').removeClass('raghav');
						$('.warehouse-locations').css("border", "1px solid #e2e2e2");
						$(this).addClass('raghav');	
						$(".raghav").css("border", "2px solid #6ec89b");
						self.location_id = $(this).find('div').data("id");
						$('.warehouse-qty').css('display', 'block');
						$('#stock_qty').focus();
					}
				});
			});

		}

		cancel() {
			this.props.resolve({ confirmed: false, payload: null });
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}

		apply() {
			let self = this;
			let product = this.product;
			let result = this.result;
			
			let entered_qty = $("#stock_qty").val() || 0;
			let order = this.env.pos.get_order();
			let selected_location_id = event.target.id;
			let location_id = self.location_id;
			if(location_id){
				let loc = $.grep(result, function(value, index){
					return  value['location']['id'] == location_id;
				});
				if(loc && parseFloat(entered_qty) > 0 && parseFloat(loc[0].quantity) >= parseFloat(entered_qty))
				{
					let orderline = new pos_model.Orderline({},{pos:self.env.pos,order:order,product:product,stock_location_id:location_id});
					orderline.product=product;
					orderline.stock_location_id=location_id;
					orderline.set_quantity(entered_qty);
					order.add_orderline(orderline);
					location_id = null;
					this.showScreen('ProductScreen');
					this.trigger('close-popup');
				}
				else{
					let str1 = loc[0].location.complete_name + ' : has : '+loc[0].quantity+' QTY. ';
					let str2 = 'You have entered : '+entered_qty 
					let msg = str1+str2
					self.showPopup('ErrorPopup', {
						title: self.env._t('Please enter valid amount of quantity.'),
						body: self.env._t(msg),
					});
				}
			}else{
				self.showPopup('ErrorPopup', {
					title: self.env._t('Unknown Location'),
					body: self.env._t('Please select Location.'),
				});
			}
		}
	}

	PosStockWarehouse.template = 'PosStockWarehouse';
	PosStockWarehouse.defaultProps = {
		confirmText: 'Apply',
		cancelText: 'Cancel',
		title: 'Confirm ?',
		body: '',
	};

	Registries.Component.add(PosStockWarehouse);

	return PosStockWarehouse;
});
