import { Component } from '@odoo/owl';

export class RecipientsListPopover extends Component {
    static template = 'eds_web_chatter.RecipientsListPopover';
    static props = {
        recipients: { type: Array },
        close: { type: Function, required: true },
    };
}
