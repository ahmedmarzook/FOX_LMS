/** @odoo-module */

import { ListController } from '@web/views/list/list_controller';
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { user } from "@web/core/user";

patch(ListController.prototype, {

	setup() {
		super.setup();
		this.show_action_approve_all = this.archInfo.xmlDoc.getAttribute("show_action_approve_all") || false;
		this._isSystemUser = false;
		user.hasGroup("base.group_system").then((isSystem) => {
			this._isSystemUser = isSystem;
		});
	},

	getStaticActionMenuItems() {
		const res = super.getStaticActionMenuItems();
		const actionOptions = {
			onClose : () => {
				this.model.root.load();
			}
		}
		Object.assign(res, {
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
							default_res_ids : await this.model.root.getResIds(true),
						}
					};
					this.env.services.action.doAction(action, actionOptions);
				}
			},
			approve: {
				isAvailable: () => this.show_action_approve_all,
				sequence: 110,
				icon: "fa fa-check-square-o",
				description: _t("Approve"),
				callback: async () => {
					const dialogProps = {
						body: _t("Are you sure you want to approve selected documents?"),
						confirm: async () => {
							const ids = await this.model.root.getResIds(true);
							const action = await this.model.orm.call(this.model.root.resModel, "action_approve_all", [ids]);
							this.actionService.doAction(action, actionOptions);
						},
						cancel: () => {},
					}
					await this.dialogService.add(ConfirmationDialog, dialogProps);
				}
			}
		});
		return res;
	},
});
