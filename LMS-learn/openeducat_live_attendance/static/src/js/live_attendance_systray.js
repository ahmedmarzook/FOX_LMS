/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LiveAttendanceSystray extends Component {
    static template = "openeducat_live_attendance.LiveAttendanceSystray";
    static props = ["*"];

    setup() {
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.state = useState({
            open: false,
            loading: false,
            registers: [],
            sheets: [],
            registerId: false,
            sheetId: false,
        });
    }

    get isDiscussPage() {
        const url = decodeURIComponent(window.location.href);
        return (
            /\/discuss(?:\/|$)/.test(url) ||
            /active_id=discuss\.channel_\d+/.test(url) ||
            /model=discuss\.channel/.test(url)
        );
    }

    get channelId() {
        const url = decodeURIComponent(window.location.href);
        const patterns = [
            /active_id=discuss\.channel_(\d+)/,
            /\/discuss\/channel\/(\d+)/,
            /\/discuss\/(\d+)/,
            /model=discuss\.channel[^#&]*[&#]id=(\d+)/,
        ];
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) {
                return Number(match[1]);
            }
        }
        return false;
    }

    async toggleMenu() {
        this.state.open = !this.state.open;
        if (!this.state.open || this.state.registers.length) {
            return;
        }
        this.state.loading = true;
        try {
            this.state.registers = await rpc(
                "/openeducat_live_attendance/registers",
                {}
            );
            const channelId = this.channelId;
            if (channelId) {
                const context = await rpc(
                    "/openeducat_live_attendance/context",
                    { channel_id: channelId }
                );
                if (!context?.error) {
                    this.state.registerId = context.register || false;
                    this.state.sheetId = context.sheet || false;
                    if (this.state.registerId) {
                        await this.loadSheets();
                    }
                }
            }
        } finally {
            this.state.loading = false;
        }
    }

    async onRegisterChange(event) {
        this.state.registerId = Number(event.target.value) || false;
        this.state.sheetId = false;
        await this.loadSheets();
    }

    async loadSheets() {
        if (!this.state.registerId) {
            this.state.sheets = [];
            return;
        }
        this.state.sheets = await rpc(
            "/openeducat_live_attendance/sheets",
            { register_id: this.state.registerId }
        );
    }

    onSheetChange(event) {
        this.state.sheetId = Number(event.target.value) || false;
    }

    async createSheet() {
        if (!this.state.registerId) {
            this.notification.add(
                "Select an attendance register first.",
                { type: "warning" }
            );
            return;
        }
        const result = await rpc(
            "/openeducat_live_attendance/create-sheet",
            { register_id: this.state.registerId }
        );
        if (result?.error) {
            this.notification.add(
                "The attendance sheet could not be created.",
                { type: "danger" }
            );
            return;
        }
        await this.loadSheets();
        this.state.sheetId = result.id;
    }

    async save() {
        const channelId = this.channelId;
        if (!channelId) {
            this.notification.add(
                "Open a live meeting channel in Discuss first.",
                { type: "warning" }
            );
            return;
        }
        if (!this.state.sheetId) {
            this.notification.add(
                "Select an attendance sheet.",
                { type: "warning" }
            );
            return;
        }
        const result = await rpc(
            "/openeducat_live_attendance/set-sheet",
            {
                channel_id: channelId,
                sheet_id: this.state.sheetId,
            }
        );
        if (result?.error) {
            this.notification.add(
                "The attendance sheet could not be linked to this meeting.",
                { type: "danger" }
            );
            return;
        }
        this.notification.add(
            "Attendance sheet linked to the live meeting.",
            { type: "success" }
        );
        this.state.open = false;
    }
}

registry.category("systray").add(
    "openeducat_live_attendance.LiveAttendanceSystray",
    { Component: LiveAttendanceSystray },
    { sequence: 31 }
);
