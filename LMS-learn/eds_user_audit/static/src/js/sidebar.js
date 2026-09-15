odoo.define('web.Sidebar.audit', function (require) {
"use strict";

var Sidebar = require('web.Sidebar');
var Dialog = require('web.Dialog');
var core = require('web.core');
var session = require('web.session');

var _t = core._t;
var qweb = core.qweb;

Sidebar.include({
	
	init: function (parent, options) {
		/*if (options.viewType == 'form' || odoo.debug) {
			options.actions.other.push({
				label: _t('Record Info'),
				callback: this._onRecordInfo.bind(this),
			});			
		}*/
		
		this._super.apply(this, arguments);
	},
	_onUpdateLogs : function () {
		var activeId = this.env.activeIds[0];
		var reference = _.str.sprintf('%s,%s', this.env.model, activeId);
		this.do_action({
			name: 'Audit Log Detail',
            res_model: 'audit.log.detail',
            domain : [['reference', '=', reference]],
            views: [[false, 'list']],
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'list,form',
		});
	},
	_onMailTrackingValues : function () {
		var activeId = this.env.activeIds[0];
		var reference = _.str.sprintf('%s,%s', this.env.model, activeId);
		var self = this;
		this.do_action({
			name: 'Chatter Logs',
            res_model: 'mail.tracking.value',
            domain : [['reference', '=', reference]],
            views: [[false, 'list']],
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'list,form',
            context : {
            	list_view_ref : 'eds_user_audit.view_mail_tracking_value_tree'
            }
		});				
	},	
	_onAllLogs : function () {
		var activeId = this.env.activeIds[0];
		this.do_action({
			name: 'Audit Log',
            res_model: 'audit.log',
            domain : [['model_id.model', '=', this.env.model], ['record_id','=', activeId]],
            views: [[false, 'list'], [false, 'form']],
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'list,form',
		});
	},	
	
	_onRecordInfo : function () {				
		var self = this;
        self.trigger_up('sidebar_data_asked', {
            callback: function (env) {
        		self.env = env;
            	var activeId = env.activeIds[0];
        		if (activeId) {
        			session.rpc('/eds_user_audit/record_info', {model : self.env.model, record_id : activeId, context : self.env.context}).then(function (data){
        		        var buttons = [
        		        	{
        		        		text: _t("Ok"), 
        		        		close: true,
        		        		classes: 'btn-primary',
        		        	}
        		        ];
        		        
        		        if (odoo.debug && !data.xmlid && session.is_system) {
        		        	buttons.push({
        		        		text : _t("Create XML ID"), 
        		        		close: true,
        		        		click : function () {
        		        			session.rpc('/eds_user_audit/create_xml_id', {model : self.env.model, record_id : activeId, context : self.env.context}).then(function (data){
        		        				self._onRecordInfo();
        		        			});        		        			
        		        		}
        		        	});
        		        }
        		        
        		        if (odoo.debug && data.xmlid && session.is_system) {
        		        	buttons.push({
        		        		text : _t("XML ID"), 
        		        		close: true,
        		        		click : function () {
        		        			self.do_action({
        		        				name: 'XML ID',
        		        	            res_model: 'ir.model.data',
        		        	            res_id : data.xmlid_id,        		        	            
        		        	            views: [[false, 'form']],
        		        	            type: 'ir.actions.act_window',
        		        	            view_type: 'form',
        		        	            view_mode: 'form',
        		        			});      		        			
        		        		}
        		        	});
        		        }        		        
        		        if (data.update_log_count > 0) {
        		        	buttons.push({
        		                text: _.str.sprintf('%s (%s)', _t("Update Logs"), data.update_log_count),
        		                close: true,
        		                click: self._onUpdateLogs.bind(self),
        		            });
        		        }
        		        if (data.tracking_value_count > 0) {
        		        	buttons.push({
        		                text: _.str.sprintf('%s (%s)', _t("Chatter Logs"), data.tracking_value_count),
        		                close: true,
        		                click: self._onMailTrackingValues.bind(self),
        		            });
        		        }
        		        		        
        		        if (data.log_count > 0) {
        		        	buttons.push({
        		                text: _.str.sprintf('%s (%s)', _t("All Logs"), data.log_count),
        		                close: true,
        		                click: self._onAllLogs.bind(self),
        		            });
        		        }
        		                		       
        		        var dialog = new Dialog(self, {
        	                title: _t("Record Info"),
        	                size: data.lines.length > 1 ? 'large' : 'medium',
        	                buttons : buttons,
        	                $content: qweb.render('eds_user_audit.record_info', {
        	                	data : data,
        	                	session : session
        	                })
        	            });
        		        
        		        dialog.open();
        		        
        		        $.when(dialog._opened).then(function (){
        		        	var $clipboardBtn = dialog.$('.btn-copy-xmlid');
        		            $clipboardBtn.tooltip({title: _t('Copied !'), trigger: 'manual', placement: 'right'});
        		            
        		        	var clipboard = new ClipboardJS('.btn-copy-xmlid', {
            					container : dialog.$modal[0]
            				});
            				
            				clipboard.on('success', function(e) {
            					_.defer(function () {
            		                $clipboardBtn.tooltip('show');
            		                _.delay(function () {
            		                    $clipboardBtn.tooltip('hide');
            		                }, 800);
            		            });
            				});
        		        });        				
        				
        				
        			});
        		}            	
            }
        });
		
	}	
	
});

});
