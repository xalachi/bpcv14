odoo.define('bi_pos_warehouse_management.PosOutOfStock', function(require) {
	'use strict';

	const { useListener } = require('web.custom_hooks');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');


	class PosOutOfStock extends AbstractAwaitablePopup {
		constructor() {
			super(...arguments);
			// this.product = this.props.product;
		}

		cancel() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}

		Ok() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}

	}

	PosOutOfStock.template = 'PosOutOfStock';
	PosOutOfStock.defaultProps = {
		confirmText: 'Okay',
		cancelText: 'Cancel',
		title: 'Out of Stock',
		body: '',
	};

	Registries.Component.add(PosOutOfStock);

	return PosOutOfStock;
});
