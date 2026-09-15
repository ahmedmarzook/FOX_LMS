odoo.define('validation.web.ajax', function (require) {
"use strict";

var ajax = require('web.ajax');
var Dialog = require('web.Dialog');
var core = require('web.core');

var jsonRpc = ajax.jsonRpc;
var _t = core._t;
var qweb = core.qweb;

var confirm = function (owner, message, options) {
    var buttons = [
        {
            text: _t("Confirm"),
            classes: 'btn-primary',
            close: true,
            click: options && options.confirm_callback,
        },
        {
            text: _t("Cancel"),
            close: true,
            click: options && options.cancel_callback
        }
    ];

    return new Dialog(owner, _.extend({
        size: 'medium',
        buttons: buttons,
        $content: qweb.render("validation.confirm.warning", {message : message}),
        title: _t("Confirmation"),
    }, options)).open();
};

var jsonRpc2 = function (url, fct_name, params, settings)  {
	var self = this;
	
	var p = jsonRpc (url, fct_name, params, settings);
	
	var resolve_func = null;
	var reject_func = null;
	
	var promise = new Promise(function (resolve, reject) {
		resolve_func = resolve;
		reject_func = reject;
	});
	
	promise.abort = function () {
		if (p.abort) {
            p.abort();
        }
	}
	
	p.then(function(result){
		resolve_func(result);
	});
	
	p.catch(function(error){
		var context = null;
		
		if (params.kwargs && params.kwargs.context )
			context = params.kwargs.context;
		else if (params.args && Number.isInteger(params.context_id))
			context = params.args[params.context_id];
		else
			context = _.last(params);
		
		context = context || null;
		
		var old_arguments = arguments;	
				
		if (context != null && error.message && error.message.data && error.message.data.name == 'odoo.addons.eds_validation.models.exceptions.ConfirmWarning') {   
			error.message.data.ConfirmWarning = true;
			var message = error.message.data.message.slice(0, -1);
			confirm(self, message, {
        		confirm_callback: function () {        			        			
        			
        			var validation_confirm = context.validation_confirm || [];
        			validation_confirm.push(message);       
        			context.validation_confirm = validation_confirm;
        			
        			var p2 = jsonRpc2 (url, fct_name, params, settings);
        			p2.then(function (){
        				resolve_func.apply(promise, arguments);
        			});
        			p2.catch(function (){
        				reject_func.apply(promise, arguments);
        			});
        		},
        		cancel_callback : function () {
        			reject_func.apply(promise, old_arguments);
        		}
        	}); 
		}
		else {
			reject_func(error);
		}
		
		
	});
	
	return promise;
}

ajax.jsonRpc = jsonRpc2;

});