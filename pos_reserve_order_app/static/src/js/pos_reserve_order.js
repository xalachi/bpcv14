odoo.define('pos_reserve_order_app.pos_reserve_order', function(require) {
	"use strict";

	var field_utils = require('web.field_utils');
	var Pager = require('web.Pager');
	var utils = require('web.utils');
	var models = require('point_of_sale.models');
	var core = require('web.core');
	const PosComponent = require('point_of_sale.PosComponent');
	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const ClientListScreen = require('point_of_sale.ClientListScreen');
	const ClientLine = require('point_of_sale.ClientLine');
	const { useListener } = require('web.custom_hooks');
	var rpc = require('web.rpc');
	var QWeb = core.qweb;
	var _t = core._t;

	var reserve_amount;
	var pos_order_domain = [];

	var posorder_super = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attr, options) {
			this.delivery_date = this.delivery_date || false;
			this.amount_due = this.amount_due || 0;
			this.is_reserved = this.is_reserved || false;
			posorder_super.initialize.call(this,attr,options);
		},

		export_as_JSON: function(){
			var loaded = posorder_super.export_as_JSON.apply(this, arguments);
			loaded.is_reserved = this.is_reserved || false;
			loaded.amount_due = this.amount_due;
			loaded.delivery_date = this.delivery_date;
			return loaded;
		},

	});

	const PosReservePaymentScreen = PaymentScreen =>
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
				useListener('reserve-order', this.reserve_order);
				var order = this.env.pos.get_order()
			}

			order_reserve(){
				if(!this.currentOrder){
					return
				} else if(this.currentOrder.get_due() == 0 || this.currentOrder.get_due() == this.currentOrder.get_total_with_tax() || this.currentOrder.get_total_paid() >= this.currentOrder.get_total_with_tax()){
					$('.reserve').removeClass('highlight');
					return false
				} else {
					$('.reserve').addClass('highlight');
					return true
				}
			}
			reserve_order() {
				var self = this;
				var order = this.env.pos.get_order();
				var orderlines = order.get_orderlines();
				var paymentlines = order.get_paymentlines();
				var total_paid = order.get_total_paid();
				var total = order.get_total_with_tax();
				var reserve_charge_type = this.env.pos.config.reserve_charge_type;
				var reserve_charge = this.env.pos.config.min_reserve_charges;
				if($('.reserve').hasClass('highlight') ){
					if(reserve_charge_type == 'percentage')
					{
						reserve_amount = (total*reserve_charge)/100.0
					}
					else{
						reserve_amount = reserve_charge;
					}
					if(total_paid < reserve_amount){
						self.showPopup('ErrorPopup',{
							title: _t('Reserve Order Amount Error'),
							body: _t('Please Pay minimum amount to Reserve Order.'),
						});
						return;
					}
					var partner_id = false
					if (order.get_client() != null)
						partner_id = order.get_client();
					if (!partner_id){
						self.showPopup('ErrorPopup',{
							title: _t('Unknown customer'),
							body: _t('You cannot Reserve Order. Select customer first.'),
						});
						return;
					}
					else if(orderlines.length === 0){
						self.showPopup('ErrorPopup',{
							title: _t('Empty Order'),
							body: _t('There must be at least one product in your order before it can be validated.'),
						});
						return;
					}
					else{
						if(order.get_total_with_tax() !== order.get_total_paid() && order.get_total_paid() != 0){
							self.showPopup('SelectReserveDateWidget', {
								title: this.env._t('Select Date'),
								body: this.env._t(),
							});
						}
					}
				}
			}
		};

	Registries.Component.extend(PaymentScreen, PosReservePaymentScreen);

	// return PaymentScreen;

	class SelectReserveDateWidget extends PosComponent {
		constructor(){
			super(...arguments);
			var self = this;
			var order = this.env.pos.get_order();
			var selectedOrder = self.env.pos.get('selectedOrder');
			var partner_id = false
			if (order.get_client() != null){
				partner_id = order.get_client();
			}
		}
		get_current_day() {
			var today = new Date();
			var dd = today.getDate();
			var mm = today.getMonth()+1; //January is 0!
			var yyyy = today.getFullYear();
			if(dd<10){
				dd='0'+dd;
			} 
			if(mm<10){
				mm='0'+mm;
			} 
			today = yyyy+'-'+mm+'-'+dd;
			return today;
		}
		create_reserve_order() {
			var self = this;
			var order = this.env.pos.get_order();
			var orderlines = order.get_orderlines();
			var paymentlines = order.get_paymentlines();
			var total = order.get_total_with_tax();
			var entered_date = $("#entered_date").val();

			var orderLines, paymentLines;
			orderLines = [];
			order.orderlines.each(_.bind( function(item) {
				return orderLines.push([0, 0, item.export_as_JSON()]);
			}, order));
			paymentLines = [];
			order.paymentlines.each(_.bind( function(item) {
				return paymentLines.push([0, 0, item.export_as_JSON()]);
			}, order));
			if(!entered_date){
				alert('Please Select Delivery Date');				
			}
			else{
				var today_date = self.get_current_day();
				var d1 = Date.parse(today_date);
				var d2 =  Date.parse(entered_date);
				if(d1 > d2){
					alert("Please Select Valid Date");
				}
				else{
					order.is_reserved = true;
					order.amount_due = total - order.get_total_paid();
					order.delivery_date = entered_date;
					order.to_invoice = false;
					order.finalized = false;
					self.env.pos.push_orders(order);
					self.showScreen('ReceiptScreen');
				}		
			}
			this.trigger('close-popup');
		}
	};
	SelectReserveDateWidget.template = 'SelectReserveDateWidget';
	SelectReserveDateWidget.defaultProps = {
		confirmText: 'Ok',
		cancelText: 'Cancel',
		title: '',
		body: '',
	};

	Registries.Component.add(SelectReserveDateWidget);

	// Start SeeReservedOrdersButtonWidget

	class SeeReservedOrdersButtonWidget extends PosComponent {
		constructor() {
			super(...arguments);
			useListener('click', this.onClick);
		}
		async onClick() {
			let self = this;
			let params = self.env.pos.get_order().get_screen_data('params');
			if(params && params['selected_partner_id'])
			{
				params['selected_partner_id'] = undefined;
			}
			this.showScreen('SeeReservedOrdersScreenWidget');
		}
	}
	SeeReservedOrdersButtonWidget.template = 'SeeReservedOrdersButtonWidget';

	ProductScreen.addControlButton({
		component: SeeReservedOrdersButtonWidget,
		condition: function() {
			return this.env.pos.config.enable_reservation;
		},
	});

	Registries.Component.add(SeeReservedOrdersButtonWidget);


	// SeeReservedOrdersScreenWidget start

	class SeeReservedOrdersScreenWidget extends PosComponent {
		constructor(){
			super(...arguments);
			var self = this;
			this.details_visible = false;
			var a = self.get_pos_orders();
			var orders = self.env.pos.get('reserved_orders_list');
			var orders_lines = self.env.pos.get('reserved_orders_line_list');
			$('.search-order input').val('');
			self.render_list_orders(orders, undefined);
			self.orderline_click_events(orders,orders_lines);
			var current_date = null;
			$('.search-order input').keyup(function() {
				self.render_list_orders(orders, this.value);
			});
		}

		refresh(){
			$('.search-order input').val('');
				var params = this.env.pos.get_order().get_screen_data('params');
				if(params && params['selected_partner_id'])
				{
					params['selected_partner_id'] = undefined;
				}
			this.get_pos_orders();
		}
		back(){
			this.showScreen('ProductScreen');
			// this.trigger('close-temp-screen');
		}
		get_selected_partner() {
			var self = this;
			if (self.gui)
				return self.gui.get_current_screen_param('selected_partner_id');
			else
				return undefined;
		}
		
		render_list_orders(orders, search_input){
			var self = this;
			if(orders == undefined)
			{
				orders = self.env.pos.get('reserved_orders_list');
			}
			var selected_partner_id = this.props.selectedValue;
			var selected_client_orders = [];
			if (selected_partner_id != undefined) {
				if (orders)	{
					for (var i = 0; i < orders.length; i++) {
						if (orders[i].partner_id[0] == selected_partner_id)
							selected_client_orders = selected_client_orders.concat(orders[i]);
					}
					orders = selected_client_orders;
				}
			}
			
			if (search_input != undefined && search_input != '') {
				var selected_search_orders = [];
				var search_text = search_input.toLowerCase()
				for (var i = 0; i < orders.length; i++) {
					if (orders[i].partner_id == '') {
						orders[i].partner_id = [0, '-'];
					}
					if(orders[i].partner_id[1] == false)
					{
						if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].state.toLowerCase()).indexOf(search_text) != -1)  || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1)) {
							selected_search_orders = selected_search_orders.concat(orders[i]);
						}
					}
					else
					{
						if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].state.toLowerCase()).indexOf(search_text) != -1)  || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
							selected_search_orders = selected_search_orders.concat(orders[i]);
						}
					}
				}
				orders = selected_search_orders;
			}
			var content = $('.orders-list-contents');
			var orders = orders;
			this.orders = orders;
			var current_date = null;
			if(orders != undefined){
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
					var order = orders[i];
					current_date = field_utils.format.datetime(moment(order.date_order), {type: 'datetime'});
					var ordersline_html = QWeb.render('OrdersLine',{widget: this, order:orders[i], selected_partner_id: orders[i].partner_id[0],current_date:current_date});
					var ordersline = document.createElement('tbody');
					ordersline.innerHTML = ordersline_html;
					ordersline = ordersline.childNodes[1];
					content.html(ordersline);
					$('.orders-list-contents').delegate('.orders-line', 'click', function(event) {
						var o_id = $(this).data('id');
						self.display_details(o_id);
					});
					$('.orders-list-contents').delegate('.pay-order', 'click', function(event) {
						var orders =  self.env.pos.get('reserved_orders_list');
						var orders_lines = self.env.pos.get('reserved_orders_line_list');
						var order_id = parseInt(this.id);
						var selectedOrder = null;
						for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
							if (orders[i] && orders[i].id == order_id) {
								selectedOrder = orders[i];
							}
						}
						var orderlines = [];
						var order_line_data = orders_lines;
						selectedOrder.lines.forEach(function(line_id) {
							for(var y=0; y<order_line_data.length; y++){
								if(order_line_data[y]['id'] == line_id){
								   orderlines.push(order_line_data[y]); 
								}
							}	
						});
						var values = { 'orderlines': orderlines, 'order': selectedOrder,'amount_due':selectedOrder['amount_due']}
						self.showPopup('PayReserveOrderPopupWidget', {
							selectedValue : values
						});
					});
					$('.orders-list-contents').delegate('.cancel-order', 'click', function(event) {
						var orders =  self.env.pos.get('reserved_orders_list');
						var orders_lines = self.env.pos.get('reserved_orders_line_list');
						var order_id = parseInt(this.id);
						var selectedOrder = null;
						for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
							if (orders[i] && orders[i].id == order_id) {
								selectedOrder = orders[i];
							}
						}
						var orderlines = [];
						var order_line_data = orders_lines;
						var myNewArray = selectedOrder.lines.filter(function(elem, index, self) {
							return index === self.indexOf(elem);
						});
						selectedOrder.lines.forEach(function(line_id) {
							for(var y=0; y<order_line_data.length; y++){
								if(order_line_data[y]['id'] == line_id){
								   orderlines.push(order_line_data[y]); 
								}
							}	
						});
						var selected_value = { 'orderlines': orderlines, 'order': selectedOrder }
						self.showPopup('CancelOrderPopupWidget', 
							{
								selectedValue : selected_value, 
							});
					});

					$('.orders-list-contents').delegate('.change-date', 'click', function(event) {
						var orders =  self.env.pos.get('reserved_orders_list');
						var order_id = parseInt(this.id);
						var selectedOrder = null;
						for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
							if (orders[i] && orders[i].id == order_id) {
								selectedOrder = orders[i];
							}
						}
						self.showPopup('ChangeReserveDateWidget', {
								selectedValue : selectedOrder, 
							});
					});
				}
			}
		}

		get_orders_domain(){
			var self = this;
			var days = self.env.pos.config.last_days
			if(days > 0)
			{
				var today= new Date();
				today.setDate(today.getDate() - days);
				var dd = today.getDate();
				var mm = today.getMonth()+1; //January is 0!
				var yyyy = today.getFullYear();
				if(dd<10){
					dd='0'+dd;
				} 
				if(mm<10){
					mm='0'+mm;
				} 
				var today = yyyy+'-'+mm+'-'+dd+" "+ "00" + ":" + "00" + ":" + "00";
				pos_order_domain = [['date_order', '>=',today],['state', 'in', ['reserved']]]
				return pos_order_domain;
			}	
		}

		get_orders_fields () {
			var	fields = ['name', 'id', 'date_order','delivery_date', 'partner_id', 'pos_reference', 'lines', 'amount_total','amount_due','amount_paid','session_id', 'state', 'company_id'];
			return fields;
		}

		get_pos_orders() {
			var self = this;
			var fields = self.get_orders_fields();
			var pos_domain = self.get_orders_domain();
			var load_orders = [];
			var load_orders_line = [];
			var order_ids = [];
			rpc.query({
				model: 'pos.order',
				method: 'search_read',
				args: [pos_order_domain,fields],
			}, {async: false}).then(function(output) {
				load_orders = output;
				self.env.pos.db.get_orders_by_id = {};
				load_orders.forEach(function(order) {
					order_ids.push(order.id)
					self.env.pos.db.get_orders_by_id[order.id] = order;
				});
				
				var fields_domain = [['order_id','in',order_ids],['is_cancel_charge_line','=',false],['price_unit','>',0]];
				rpc.query({
					model: 'pos.order.line',
					method: 'search_read',
					args: [fields_domain],
				}, {async: false}).then(function(output1) {
					self.env.pos.db.reserved_orders_line_list = output1;
					load_orders_line = output1;
					self.env.pos.set({'reserved_orders_list' : load_orders});
					self.env.pos.set({'reserved_orders_line_list' : output1});
					
					self.render_list_orders(load_orders, undefined);
				});
			});
			self.props.orders = load_orders;
			return [load_orders,load_orders_line]
		}

		display_details(o_id) {
			var self = this;
			var orders =  self.env.pos.get('reserved_orders_list');
			var orders_lines =  self.env.pos.get('reserved_orders_line_list');
			var orders1 = [];
			for(var ord = 0; ord < orders.length; ord++){
				if (orders[ord]['id'] == o_id){
					 orders1 = orders[ord];
				}
			}
			var current_date =  field_utils.format.datetime(moment(orders1.date_order),{type: 'datetime'});
			var orderline = [];
			for(var n=0; n < orders_lines.length; n++){
				if (orders_lines[n]['order_id'][0] ==o_id){
					orderline.push(orders_lines[n])
				}
			}
			var current_order = {'order': [orders1], 'orderline':orderline,'current_date':current_date}
			this.showPopup('ReservedOrderDetailsPopupWidget', current_order);
		}

		orderline_click_events() {
			var self = this;
			
			$('.orders-list-contents').delegate('.orders-line-name', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});
			
			$('.orders-list-contents').delegate('.orders-line-ref', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});
						
			$('.orders-list-contents').delegate('.orders-line-partner', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});
			
			$('.orders-list-contents').delegate('.orders-line-date', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});
						
			$('.orders-list-contents').delegate('.orders-line-tot', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});

			$('.orders-list-contents').delegate('.orders-line-state', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});
			
			$('.orders-list-contents').delegate('.orders-line-amount_due', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});

			$('.orders-list-contents').delegate('.orders-line-amount_paid', 'click', function(event) {
				var o_id = $(this).data('id');
				self.display_details(o_id);
			});

			$('.orders-list-contents').delegate('.cancel-order', 'click', function(event) {
				var orders =  self.pos.get('reserved_orders_list');
				var orders_lines = self.pos.get('reserved_orders_line_list');
				var order_id = parseInt(this.id);
				var selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];
				var order_line_data = orders_lines;
				var myNewArray = selectedOrder.lines.filter(function(elem, index, self) {
					return index === self.indexOf(elem);
				});
				selectedOrder.lines.forEach(function(line_id) {
					for(var y=0; y<order_line_data.length; y++){
						if(order_line_data[y]['id'] == line_id){
						   orderlines.push(order_line_data[y]); 
						}
					}	
				});
				self.gui.show_popup('cancel_order_popup_widget', { 'orderlines': orderlines, 'order': selectedOrder });
			});

			$('.orders-list-contents').delegate('.change-date', 'click', function(event) {
				var orders =  self.pos.get('reserved_orders_list');
				var order_id = parseInt(this.id);
				var selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				self.gui.show_popup('change_reserve_date_widget', {'order': selectedOrder });
			});

			$('.orders-list-contents').delegate('.pay-order', 'click', function(event) {
				var orders =  self.pos.get('reserved_orders_list');
				var orders_lines =  self.pos.get('reserved_orders_line_list');
				var order_id = parseInt(this.id);
				var selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];
				var order_line_data = orders_lines;
				selectedOrder.lines.forEach(function(line_id) {
					for(var y=0; y<order_line_data.length; y++){
						if(order_line_data[y]['id'] == line_id){
						   orderlines.push(order_line_data[y]); 
						}
					}	
				});
				self.showPopup('pay_reserve_order_popup_widget', { 'orderlines': orderlines, 'order': selectedOrder,'amount_due':selectedOrder['amount_due']});
			});
		}
	}
	SeeReservedOrdersScreenWidget.template = 'SeeReservedOrdersScreenWidget';

	Registries.Component.add(SeeReservedOrdersScreenWidget);


	class ReservedOrderDetailsPopupWidget extends PosComponent {
		constructor() {
			super(...arguments);
		}
		cancel(){
			this.trigger('close-popup')
		}
	}
	ReservedOrderDetailsPopupWidget.template = 'ReservedOrderDetailsPopupWidget';
	ReservedOrderDetailsPopupWidget.defaultProps = {
		confirmText: 'Ok',
		cancelText: 'Cancel',
		startingValue: "",
		title: '',
		body: '',
	};

	Registries.Component.add(ReservedOrderDetailsPopupWidget);


	class PayReserveOrderPopupWidget extends PosComponent {
		constructor() {
			super(...arguments);
			var self = this;
			this.order = this.props.selectedValue.order || [];
			this.orderlines = this.props.selectedValue.orderlines || [];
			this.amount_due = this.props.selectedValue.amount_due || 0.0;
		}
		get_change(event){
			if(parseFloat(event.target.value) > parseFloat(this.props.selectedValue.amount_due))
			{
				var remain = parseFloat(event.target.value) - parseFloat(this.props.selectedValue.amount_due)
				$('.reamining-div').show();
				$('.reamining-change').text(remain)
			}
			else{
				$('.reamining-div').hide();
			}
		}
		cancel(){
			this.trigger('close-popup')
		}
		pay_order(){
			var self= this;
			var orderlines = this.props.selectedValue.orderlines;
			var order = this.props.selectedValue.order;
			var amount_due = this.props.selectedValue.amount_due || 0.0;
			var select_journal_id = $('.select_journal_id').val();
			var pay_amount =  $('#pay_amount').val();
			var cash_jrnl_id = false;
			var session_id = self.env.pos.get_order().pos_session_id;
			if(pay_amount)
			{
				for (var i = 0; i < self.env.pos.payment_methods[0].length; i++) {
					if(self.pos.payment_methods[i]['type'] == 'cash')
					{
						cash_jrnl_id = self.env.pos.payment_methods['id']
					}
				}
				rpc.query({
					model: 'pos.order',
					method: 'pay_reserved_amount',
					args: [order.id,parseInt(select_journal_id),parseFloat(pay_amount),parseInt(cash_jrnl_id),parseInt(session_id)],
					
					}).then(function(output) {
						alert("You have Paid: "+pay_amount +"Amount")
						self.showScreen('ProductScreen');
				});
			}

			else{
				alert("Please Enter Amount To Done Order")
			}
			this.trigger('close-popup')
		}
	}
	PayReserveOrderPopupWidget.template = 'PayReserveOrderPopupWidget';
	PayReserveOrderPopupWidget.defaultProps = {
		confirmText: 'Ok',
		cancelText: 'Cancel',
		startingValue: "",
		title: '',
		body: '',
	};

	Registries.Component.add(PayReserveOrderPopupWidget);


	class CancelOrderPopupWidget extends PosComponent {
		constructor() {
			super(...arguments);
			var selectedOrder = this.env.pos.get_order();
			var orderlines = this.props.selectedValue.orderlines;	
			var order = this.props.selectedValue.order;
			var removedline = [];

			$('#delete_whole').click(function() {
				if ($('#delete_whole').is(':checked')) {
					$('.div-container').hide();
				}
				else{
					$('.div-container').show();
				}
			});

			$('.entered_item_qty').change(function(ev) {
				var entered_item_qty = $('#entered_item_qty');
				var line_id = parseFloat(entered_item_qty.attr('line-id'));
				var qty_id = parseFloat(entered_item_qty.attr('qty-id'));
				var entered_qty = parseFloat(entered_item_qty.val());
				if (qty_id < entered_qty)
				{
					alert("You can not increase ordered quantity")
					entered_item_qty.val(qty_id);
				}	
			});
			$('#apply_order').click(function() {
				// self.cancel_order_or_product(order,orderlines,removedline)
			});
		}
		remove_line(event, line_id){
			var selectedOrder = this.env.pos.get_order();
			var orderlines = this.props.selectedValue.orderlines;	
			var order = this.props.selectedValue.order;
			var removedline = [];
			var remove_lines = $(this.el).find('.remove-line');
			for (var i = 0; i < orderlines.length; i++) {
				if(orderlines[i])
				{
					if(orderlines[i]['id'] == $(line_id.target).attr('line-id'))
					{
						removedline.push($(line_id.target).attr('line-id'))
						orderlines.splice(i, 1); 
					}
				}
			}
			this.props.selectedValue.removedlines = removedline
			$(line_id.target).closest('tr').remove();
			if(orderlines.length === 0)
			{
				$('#delete_whole').prop('checked', true);
				$('.div-container').hide();
			}
		}
		cancel_order_or_product() {
			var self = this;
			var entered_code = $("#entered_item_qty").val();
			var list_of_qty = $('.entered_item_qty');
			var cancelorder_products = {};
			var order = this.props.selectedValue.order;
			var orderlines = this.props.selectedValue.orderlines;
			var removedlines = this.props.selectedValue.removedlines
			var orders_lines = self.env.pos.get('reserved_orders_line_list');	
			var cancel_charges_product = this.env.pos.config.cancel_charges_product;
			var cancel_charge_type = this.env.pos.config.cancel_charge_type;
			var cancel_charges = this.env.pos.config.cancel_charges;
			var orders = self.env.pos.get('reserved_orders_list');
			var selectedOrder = this.env.pos.get_order();
			var cancellation_charge;
			var temp_charge;
			var partner_id = false;	
			var client = false;
			var is_del_all = false;
			if (order && order.partner_id != null)
				partner_id = order.partner_id[0];
				client = this.pos.db.get_partner_by_id(partner_id);

			if ($('#delete_whole').is(':checked')) {
				for (var i = 0; i<orders_lines.length; i++){
					for (var j = 0; j<orderlines.length; j++){
						if (orders_lines[i]['order_id'][1] == orderlines[j]['order_id'][1]){
							orders_lines.splice(i, 1);
						}
					}
				}
				is_del_all = true;

			}
			else{
				$.each(list_of_qty, function(index,value) {
					var entered_item_qty = $(value).find('input');
					var line_id = parseFloat(entered_item_qty.attr('line-id'));
					var qty_id = parseFloat(entered_item_qty.attr('qty-id'));
					var entered_qty = parseFloat(entered_item_qty.val());
					cancelorder_products[line_id] = entered_qty;
				});
			}
			removedline.sort()
			for (var i = 0; i < orders_lines.length; i++){
				for (var line in removedline){
					if (orders_lines[i]){
						if (orders_lines[i]['id'] == parseInt(removedline[line])){
							orders_lines.splice(i, 1);
						}
					}
				}
			}
			rpc.query({
				model: 'pos.order',
				method: 'change_or_remove_product',
				args: [order.id,cancelorder_products,removedline,self.pos.config.id,is_del_all],
			})
			this.showScreen('SeeReservedOrdersScreenWidget');
		}
		cancel(){
			this.trigger('close-popup')
		}
	}
	CancelOrderPopupWidget.template = 'CancelOrderPopupWidget';
	CancelOrderPopupWidget.defaultProps = {
		confirmText: 'Ok',
		cancelText: 'Cancel',
		startingValue: "",
		title: '',
		body: '',
	};

	Registries.Component.add(CancelOrderPopupWidget);



	class ChangeReserveDateWidget extends PosComponent {
		constructor() {
			super(...arguments);
		}
		get_today_date(){
			var today= new Date();
			var dd = today.getDate();
			var mm = today.getMonth()+1; //January is 0!
			var yyyy = today.getFullYear();
			if(dd<10){
				dd='0'+dd;
			} 
			if(mm<10){
				mm='0'+mm;
			} 
			var date =yyyy+"-"+mm+"-"+dd;
			return date
		}


		change_reserve_order_date() {
			var self = this;
			var order = self.props.selectedValue;
			var changed_date = $("#changed_date").val();
			var orders =  self.env.pos.get('reserved_orders_list');
			var orders_lines = self.env.pos.get('reserved_orders_line_list');
			if(!changed_date){
				alert('Please Select Delivery Date');				
			}
			else{
				var today_date = self.get_today_date();
				var d1 = Date.parse(today_date);
				var d2 =  Date.parse(changed_date);
				if(d1 > d2){
					alert("Please Select Valid Date");
				}
				else{
					return rpc.query({
						model: 'pos.order',
						method: 'change_reserve_date',
						args: [order.id,changed_date],
					})
				}
				
			}
			this.trigger('close-popup')
		}
		cancel(){
			this.trigger('close-popup')
		}
	}
	ChangeReserveDateWidget.template = 'ChangeReserveDateWidget';
	ChangeReserveDateWidget.defaultProps = {
		confirmText: 'Ok',
		cancelText: 'Cancel',
		startingValue: "",
		title: '',
		body: '',
	};
	Registries.Component.add(ChangeReserveDateWidget);


	class ReservedLinesButtonWidget extends PosComponent {
		constructor() {
			super(...arguments);
			useListener('click', this.onClick);
		}
		async onClick() {
			this.showScreen('ReservedLinesScreenWidget');
		}
	}
	ReservedLinesButtonWidget.template = 'ReservedLinesButtonWidget';

	ProductScreen.addControlButton({
		component: ReservedLinesButtonWidget,
		condition: function() {
			return this.env.pos.config.enable_reservation;
		},
	});
	Registries.Component.add(ReservedLinesButtonWidget);


	class ReservedLinesScreenWidget extends PosComponent {
		constructor(){
			super(...arguments);
			var self = this;
			this.details_visible = false;
			$('.search-order input').val('');
			self.get_reserved_lines();
			var orders_lines =  self.env.pos.get('reserved_line_list');
		}

		back(){
			this.showScreen('ProductScreen')
		}

		render_list_orders(event, search_input){
			let self = this;
			var orders = this.props.reserved_lines;
			var order_lines = self.env.pos.get('reserved_line_list');
			if(orders == undefined)
			{
				orders = self.env.pos.get('reserved_line_list');
			}
			if (event.target != undefined && event.target != '') {
				var selected_search_orders = [];
				var search_text = event.target.value.toLowerCase()
				for (var i = 0; i < orders.length; i++) {
					if (((orders[i].product.toLowerCase()).indexOf(search_text) != -1) ||  ((orders[i].order_id.toLowerCase()).indexOf(search_text) != -1)) {
						selected_search_orders = selected_search_orders.concat(orders[i]);
					}
				}
				orders = selected_search_orders;
			}
			let content = $('.lines-list-contents');
			content.innerHTML = "";
			let current_date = null;
			if(orders != undefined){
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
					var order = orders[i];
					current_date = field_utils.format.datetime(moment(order.date_order), {type: 'datetime'});
					var ordersline_html = QWeb.render('ReservedOrdersLine',{widget: this, line:orders[i]});
					var ordersline = document.createElement('tbody');
					ordersline.innerHTML = ordersline_html;
					ordersline = ordersline.childNodes[1];
					content.html(ordersline);
				}
			}
		}
		get_reserved_lines() {
			$('.search-order input').val('');
			var self = this;
			rpc.query({
				model: 'pos.order',
				method: 'get_reserved_lines',
				args: [1],
			}, {async: false}).then(function(output1) {
				self.env.pos.set({'reserved_line_list' : output1});
				self.props.reserved_lines = output1;
				self.render_list_orders(output1, undefined);
			});
		}

	};
	ReservedLinesScreenWidget.template = 'ReservedLinesScreenWidget';

	Registries.Component.add(ReservedLinesScreenWidget);


	const PosReserveClientListScreen = ClientListScreen =>
        class extends ClientListScreen {
			constructor(){
				super(...arguments);
				var self = this;
			}
		};
	Registries.Component.extend(ClientListScreen, PosReserveClientListScreen);
	

	const PosReserveClientLine = ClientLine =>
        class extends ClientLine {
			constructor(){
				super(...arguments);
				var self = this;
			}
			client_order(event){
				this.trigger('close-temp-screen');
				this.showScreen('SeeReservedOrdersScreenWidget',
				{
					selectedValue: $(event.target).attr('id'),
				});
			}
		};

	Registries.Component.extend(ClientLine, PosReserveClientLine);
	
	return {
		PaymentScreen,
		SelectReserveDateWidget,
		SeeReservedOrdersButtonWidget,
		SeeReservedOrdersScreenWidget,
		ReservedOrderDetailsPopupWidget,
		PayReserveOrderPopupWidget,
		CancelOrderPopupWidget,
		ChangeReserveDateWidget,
		ReservedLinesButtonWidget,
		ReservedLinesScreenWidget,
		ClientListScreen,
		ClientLine,
	};
});
