odoo.define('sh_barcode_scanner_adv.global_doc_search', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var SystrayMenu = require('web.SystrayMenu');
    var rpc = require('web.rpc')

    var _t = core._t;
    var QWeb = core.qweb


    
    
    var ShBarcodeScannerAdvSearchDocument = Widget.extend({
        template:'sh_barcode_scanner_adv.global_doc_search',
        events: {
            'change input.js_cls_sh_barcode_scanner_adv_document_barcode': '_onChangeBarcode',   
            'change .js_cls_sh_barcode_scanner_adv_document_select': '_onChangeDocumentSelect',            
            'show.bs.dropdown': '_onShowDropdown',    
            'hide.bs.dropdown': '_onHideDropdown',            
        },

        start: function () {
            var self = this;
            var def = this._rpc({
                    model: 'sh_barcode_scanner_adv.search.document',
                    method: 'has_global_search_enabled',
                    args: [],
                })
                .then(function (result){
                	self.$el.find('.js_cls_sh_barcode_scanner_adv_document_select').html(result.options);
                	if (result.has_global_search_enabled){
                  		self.$el.removeClass('d-none');
                  	}else{
                  		self.$el.addClass('d-none');
                  	}
                });

            return Promise.all([def, this._super.apply(this, arguments)]);
        },
        
        
        _onHideDropdown: function (ev) {
            if (ev.clickEvent) {
                ev.preventDefault();
              }
        },
        
        
        _onShowDropdown: function (ev) {        	
        	var barcodeInput = $(ev.target).closest('.o_mail_systray_item').find(".js_cls_sh_barcode_scanner_adv_document_barcode");        	
        	barcodeInput.val('');
        	
        	setTimeout(function(){ 
        	//var barcodeInput = $(ev.target).closest('.o_mail_systray_item').find(".js_cls_sh_barcode_scanner_adv_document_barcode");        	
        	//barcodeInput.val('');
        	barcodeInput.focus();
        	}, 300);
        },
        
        
	    /**
         * OnChange Document Select
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onChangeDocumentSelect: function (ev) {
        	//ev.stopPropagation();
       	//var dropdown = $(ev.target).closest('.o_mail_systray_item').find(".js_cls_document_search_dropdown");  
       	//dropdown.dropdown("show");

       	//dropdown.dropdown('show');
       		//dropdown.addClass("show");
        	//dropdown.toggleClass('show');

        	//var searchbutton = $(ev.target).closest('.o_mail_systray_item').find('.js_cls_document_search_dropdown'); 
        	//searchbutton.dropdown('show');
        	//searchbutton.addClass("show");
        	
        },        
	    /**
         * Highlight selected color
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onChangeBarcode: function (ev) {
            var self = this;
        	var barcode = $(ev.target).val().trim();
        	var doc_type = $(ev.target).closest('.js_cls_form_group_wrapper').find(".js_cls_sh_barcode_scanner_adv_document_select option:selected").val();

        	if(barcode != ''){
                rpc.query({
                    model: 'sh_barcode_scanner_adv.search.document',
                    method: 'search_document',
                    args: [barcode,doc_type]
                    }).then(function(result){
                    	if (result.action){
                    		// to hide dropdown when found document
                    		$(ev.target).closest('.o_mail_systray_item').find(".js_cls_document_search_btn").click();
                    		self.do_action(result.action);	
                    	}
                    	else{
                    		alert("Document not found for the barcode: " + barcode);
                    		$(ev.target).val('');
                    		$(ev.target).focus();
                    		
                    	}
                    	 
                    });            	
            	
            	
            }
        },

    });

    SystrayMenu.Items.push(ShBarcodeScannerAdvSearchDocument);

    return {
    	ShBarcodeScannerAdvSearchDocument: ShBarcodeScannerAdvSearchDocument,
    };
});
