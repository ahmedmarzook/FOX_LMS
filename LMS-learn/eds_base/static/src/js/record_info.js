/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useAutofocus } from "@web/core/utils/hooks";
import { CopyButton } from "@web/core/copy_button/copy_button";
import { Component } from "@odoo/owl";
import { user } from "@web/core/user";

export class RecordInfoDialog extends Component {
    static template = "eds_base.record_info";
    static components = { Dialog, CopyButton };
    static defaultProps = {
        title: _t("Record Info"),
    };

    setup() {
        useAutofocus();
        this.copyText = _t("Copy");
        this.successText = _t("Copied");
        this.space = " ";
    }

    get isSystem() {
        return user.isSystem;
    }

    get reference() {
        return `${this.props.model},${this.props.id}`;
    }

    open_xml_record() {
        const action = {
            name: _t('XML ID'),
            res_model: 'ir.model.data',
            res_id: this.props.xmlid_id,
            views: [[false, 'form']],
            type: 'ir.actions.act_window',
            view_mode: 'form',
            context: {
                'default_name': this.props.suggest_xmlid,
                'default_model': this.props.model,
                'default_module': '_',
                'default_res_id': this.props.id
            }
        };
        this.env.services.action.doAction(action);
        this.props.close();
    }

    open_update_log() {
        const action = {
            name: _t('Audit Log Detail'),
            res_model: 'audit.log.detail',
            domain: [['reference', '=', this.reference]],
            views: [[false, 'list']],
            type: 'ir.actions.act_window',
            view_mode: 'list,form',
        };
        this.env.services.action.doAction(action);
        this.props.close();
    }

    open_chatter_log() {
        const action = {
            name: _t('Chatter Logs'),
            res_model: 'mail.tracking.value',
            domain: [['reference', '=', this.reference]],
            views: [[false, 'list']],
            type: 'ir.actions.act_window',
            view_mode: 'list,form',
            context: {
                list_view_ref: 'eds_user_audit.view_mail_tracking_value_tree'
            }
        };
        this.env.services.action.doAction(action);
        this.props.close();
    }

    open_all_log() {
        const action = {
            name: _t('Audit Log'),
            res_model: 'audit.log',
            domain: [['model_id.model', '=', this.props.model], ['record_id', '=', this.props.id]],
            views: [[false, 'list'], [false, 'form']],
            type: 'ir.actions.act_window',
            view_mode: 'list,form',
        };
        this.env.services.action.doAction(action);
        this.props.close();
    }
}
