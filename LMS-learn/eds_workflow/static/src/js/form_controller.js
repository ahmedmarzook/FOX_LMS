/** @odoo-module */

import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ApprovalInfoDialog } from '@eds_workflow/js/approval_info';
import { user } from "@web/core/user";

patch(FormController.prototype, {
	setup() {
		super.setup();
		this._isSystemUser = false;
		user.hasGroup("base.group_system").then((isSystem) => {
			this._isSystemUser = isSystem;
		});
	},

	getStaticActionMenuItems() {
		const res = super.getStaticActionMenuItems();
		Object.assign(res, {
			approval_info: {
				isAvailable: () => "button_approve_enabled" in this.model.root.activeFields,
				sequence: 100,
				icon: "fa fa-check",
				description: _t("Approval Info"),
				callback: async () => {
					const dialogProps = await this.model.orm.call(this.model.root.resModel, "get_approval_info", [this.model.root.resId]);
					await this.dialogService.add(ApprovalInfoDialog, dialogProps);
				}
			},
			update_status : {
				isAvailable: () => "state" in this.model.root.activeFields && this._isSystemUser,
				sequence: 100,
				icon: "fa fa-code",
				description: _t("Update Status"),
				callback: async () => {
					const action = {
					    name: _t('Change Document Status'),
					    res_model: 'approval.state.update',
					    type: 'ir.actions.act_window',
					    views: [[false, 'form']],
					    view_mode: 'form',
					    target : 'new',
						context: {
							default_res_model : this.model.root.resModel,
							default_res_ids : [this.model.root.resId],
						}
					};
					const options = {
						onClose : () => {
							this.model.root.load();
						}
					}
					await this.env.services.action.doAction(action, options);

				}
			}
		});
		return res;
	},
});
