/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useAutofocus } from "@web/core/utils/hooks";

import { Component } from "@odoo/owl";

export class ApprovalInfoDialog extends Component {
    static template = "eds_workflow.approval_info";
    static components = { Dialog };
    static props = {
        name : {type: String},
        lines : {type: Array},
        approval_users: {type: Array},
        waiting_approval: {type:Boolean},
        show_login_as: {type:Boolean},
        close: {type : Function},
		workflow: {type: String},
		workflow_node: {type: String},
		workflow_activity: {type: Array},
    };
    static defaultProps = {
        title: _t("Approval Info"),
    };
        
    setup() {
        useAutofocus();
    }
}
