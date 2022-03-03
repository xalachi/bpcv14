odoo.define('l10n_fr_pos_cert.BiPaymentScreen', function(require) {

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');

	const session = require('web.session');
	const PosComponent = require('point_of_sale.PosComponent');

	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;

	const BiPaymentScreen = PaymentScreen => class extends PaymentScreen {
		constructor() {
			super(...arguments);
			useListener('click-update_amount', this._UpdateAmountt);
			useListener('click-cur-switch', this._UpdateDetails);
		}

		mounted() {
			$('#details').hide()
		}

		_UpdateDetails() {
			if($("#cur-switch").prop('checked') == true){
				$('#details').hide()
			}
			else{
				$('#details').show()
			}
		}

		_UpdateAmountt() {
			let self = this;
			let order = this.env.pos.get_order();
			let paymentlines = this.env.pos.get_order().get_paymentlines();
			let open_paymentline = false;
			let tot = order.get_curamount();
			let tot_amount = 0;
			let currency = this.env.pos.poscurrency;
			let user_amt = $('.edit-amount').val();
			let cur = $('.drop-currency').val();
			let payment_methods_from_config = this.env.pos.payment_methods.filter(method => this.env.pos.config.payment_method_ids.includes(method.id));
			order.add_paymentline(payment_methods_from_config[0]);
			let selected_paymentline = order.selected_paymentline;

			for(var i=0;i<currency.length;i++){
				if(cur==currency[i].id){
					
					let c_rate = self.env.pos.company_currency.rate/currency[i].rate;
					tot_amount = parseFloat(user_amt)*c_rate;
					selected_paymentline.amount =parseFloat(tot_amount.toFixed(2));
					selected_paymentline.amount_currency =parseFloat(parseFloat(user_amt).toFixed(2)) ;
					$('.show-payment').text(this.env.pos.format_currency_no_symbol(selected_paymentline.amount));
					selected_paymentline.set_curname(currency[i].name);
					selected_paymentline.set_curamount(selected_paymentline.amount_currency);
				}
			}
			order.get_paymentlines();
			if (!order) {
				return;
			} else if (order.is_paid()) {
				$('.next').addClass('highlight');
			}else{
				$('.next').removeClass('highlight');
			}
			$('.edit-amount').val('');
			self._ChangeCurrency();
			window.document.body.removeEventListener('keypress', self.keyboard_handler);
			window.document.body.removeEventListener('keydown', self.keyboard_keydown_handler);
		}

		_ChangeConfig() {
			let config = false;
			let order= this.env.pos.get_order();
			if($('#Receipt').prop('checked') == true){
				order.set_inrecipt(true);
			}
			else{
				order.set_inrecipt(false);
			}   
		}

		_ChangeCurrency() {
			let self = this;
			let currencies = this.env.pos.poscurrency;
			let cur = $('.drop-currency').val();
			let curr_sym;
			let order= this.env.pos.get_order();
			let pos_currency = this.env.pos.currency;
			for(var i=0;i<currencies.length;i++)
			{
				if(cur != pos_currency.id && cur==currencies[i].id)
				{
					let currency_in_pos = (currencies[i].rate/self.env.pos.currency.rate).toFixed(6);
					$('.currency_symbol').text(currencies[i].symbol);
					$('.currency_rate').text(currency_in_pos);
					$('.currency_name').text(currencies[i].name);
					curr_sym = currencies[i].symbol;

					let curr_tot =order.get_due()*currency_in_pos;
					$('.currency_cal').text(parseFloat(curr_tot.toFixed(6)));
					order.set_curamount(parseFloat(curr_tot.toFixed(6)));
					order.set_symbol(curr_sym);
					order.set_curname(currencies[i].name);

					return curr_tot;
				}
				if(cur == pos_currency.id && cur==currencies[i].id){
					$('.currency_symbol').text(pos_currency.symbol);
					$('.currency_rate').text(1);
					$('.currency_name').text(pos_currency.name);
					curr_sym = pos_currency.symbol;

					let curr_tot =order.get_due();
					$('.currency_cal').text(parseFloat(curr_tot.toFixed(2)));
					order.set_curamount(parseFloat(curr_tot.toFixed(2)));
					order.set_symbol(curr_sym);
					order.set_curname(pos_currency.name);

					return curr_tot;
				}
			}
		}
	}

	Registries.Component.extend(PaymentScreen, BiPaymentScreen);

	return PaymentScreen;
});