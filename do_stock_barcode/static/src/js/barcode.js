odoo.define('do_stock_barcode.barcode', function(require) {
  "use strict";

  var BasicModel = require('web.BasicModel');
  var BarcodeFromView = require('barcodes.FormView');
  var FormController = require('web.FormController');

  BasicModel.include({
     async _performOnChange(record, fields, options = {}) {
        const firstOnChange = options.firstOnChange;
        let { hasOnchange, onchangeSpec } = this._buildOnchangeSpecs(record, options.viewType);
        if (!firstOnChange && !hasOnchange) {
            return;
        }
        var idList = record.data.id ? [record.data.id] : [];
        const ctxOptions = {
            full: true,
        };
        if (fields.length === 1) {
            fields = fields[0];
            // if only one field changed, add its context to the RPC context
            ctxOptions.fieldName = fields;
        }
        var context = this._getContext(record, ctxOptions);
        var currentData = this._generateOnChangeData(record, {
            changesOnly: false,
            firstOnChange,
        });

        const result = await this._rpc({
            model: record.model,
            method: 'onchange',
            args: [idList, currentData, fields, onchangeSpec],
            context: context,
        });
        if (!record._changes) {
            // if the _changes key does not exist anymore, it means that
            // it was removed by discarding the changes after the rpc
            // to onchange. So, in that case, the proper response is to
            // ignore the onchange.
            return;
        }
        if (result.warning) {
            if (fields === '_barcode_scanned' || fields === 'product_barcode_scan') {
              this.do_warn(result.warning.title, result.warning.message);
              $('.o_notification_manager').addClass('notification_center');
              if (result.warning.title === "Successfully Added") {
                $('.o_notification_manager').addClass('success');
              } else {
                $('.o_notification_manager').removeClass('success');
                $('body').append('<audio src="/do_stock_barcode/static/src/sounds/error.wav" autoplay="true"></audio>');
              }
            } else {
              $('.o_notification_manager').removeClass('success');
              $('.o_notification_manager').removeClass('notification_center');
              this.trigger_up('warning', {
                message: result.warning.message,
                title: result.warning.title,
                type: 'dialog',
              });
            }
            record._warning = true;
          }
        if (result.domain) {
            record._domains = Object.assign(record._domains, result.domain);
        }
        await this._applyOnChange(result.value, record, { firstOnChange });
        return result;
    },
  });
  FormController.include({
    _barcodeAddX2MQuantity: function(barcode, activeBarcode) {
      if (this.mode === 'readonly') {
        if (activeBarcode.name == '_barcode_scanned') {
          this._setMode('edit');
        } else {
          this.do_warn(_t('Error: Document not editable'),
            _t('To modify this document, please first start edition.'));
          return Promise.reject();
        }
      }

      var record = this.model.get(this.handle);
      var candidate = this._getBarCodeRecord(record, barcode, activeBarcode);
      if (candidate) {
        return this._barcodeSelectedCandidate(candidate, record, barcode, activeBarcode);
      } else {
        return this._barcodeWithoutCandidate(record, barcode, activeBarcode);
      }
    },
    _barcodeScanned: function(barcode, target) {
      var self = this;
      var resource = this._super.apply(this, arguments);
      if (self.modelName === "stock.picking") {
        self.saveRecord();

      }
      return resource;
    },
  });
});