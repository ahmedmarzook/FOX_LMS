odoo.define('eds_mail.systray.ActivityMenu', function (require) {
"use strict";

var ActivityMenu = require("mail.systray.ActivityMenu");
var session = require('web.session');
var core = require('web.core');
//var Menu = require("web.Menu");
var data_manager = require('web.data_manager');
var Domain = require('web.Domain');

ActivityMenu.include({
    
	/**
     * Redirect to particular model view
     * @private
     * @param {MouseEvent} event
     */
    _onActivityFilterClick: function (event) {
        // fetch the data from the button otherwise fetch the ones from the parent (.o_mail_preview).
        var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
        var context = {};
        if (data.filter === 'my') {
            context['search_default_activities_overdue'] = 1;
            context['search_default_activities_today'] = 1;
        } else {
            context['search_default_activities_' + data.filter] = 1;
        }
        var main_menu_id = 0;	
		var action_id = 0;
		
        _.each(this._activities, function(activity_data){
        	if (activity_data.model ==data.res_model && activity_data.name ==data.model_name) {
			main_menu_id = activity_data.main_menu_id;
			action_id = activity_data.action_id;
		}
        		
        });
	
	// Use correct domain based on the target model
	var action_domain = data.res_model === 'mail.activity' 
	    ? [['user_id', '=', session.uid]]
	    : [['activity_ids.user_id', '=', session.uid]];
	var self = this;
		
		if (action_id) {
			data_manager.load_action(action_id).then(function(action){
				var domain = new Domain(action.domain || []);
        		action.domain = Domain.prototype.normalizeArray(domain.toArray().concat(action_domain));
				
				core.bus.trigger('change_menu_section', main_menu_id);
				self.do_action(action, {clear_breadcrumbs : true});
			});
			return;	
		}
        
		core.bus.trigger('change_menu_section', main_menu_id);
        this.do_action({
            type: 'ir.actions.act_window',
            name: data.model_name,
            res_model:  data.res_model,
            views: [[false, 'list'], [false, 'kanban'], [false, 'form']],
            search_view_id: [false],
            domain: action_domain,
            context:context,
            target : 'main'
        }, {
        	clear_breadcrumbs : true
    	});
    },
	
});

});