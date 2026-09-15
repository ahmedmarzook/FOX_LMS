/** @odoo-module */

import { ViewButton } from '@web/views/view_button/view_button';
import { patch } from "@web/core/utils/patch";

patch(ViewButton.prototype, {
	
	setup() {
		super.setup();
		if (this.props.className?.includes("oe_workflow_approve")) {
			const approve_button_name = this.props.record?.data?.approve_button_name;
			if (approve_button_name !== undefined) {
				if (approve_button_name)
					this.props.string = approve_button_name;
				else
					this.props.className += " o_hidden";
			}
		}
		else if (this.props.className?.includes("oe_workflow_reject")) {
			const reject_button_name = this.props.record?.data?.reject_button_name;
			if (reject_button_name !== undefined) {
				if (reject_button_name)
					this.props.string = reject_button_name;
				else
					this.props.className += " o_hidden";
			}
		}

	},

	get clickParams() {
		const res = super.clickParams;
		if (res.name == "action_approve" && res.confirm === undefined && this.props.className?.includes("oe_workflow_approve")) {
			const approve_confirm_msg =this.env.model.root.data.approve_confirm_msg;
			if (approve_confirm_msg)
				res.confirm = approve_confirm_msg;
		}
		if (res.name == "action_reject" && res.confirm === undefined && this.props.className?.includes("oe_workflow_reject")) {
			const reject_confirm_msg =this.env.model.root.data.reject_confirm_msg;
			if (reject_confirm_msg)
				res.confirm = reject_confirm_msg;
		}		
		return res;			
	}
});