/** @odoo-module **/

import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import GlobalFunction from "./formatting_function";
import { DashboardChartCanvas } from "./components/dashboard_chart";

export class DashboardPro extends Component {
    static template = "openeducat_dashboard_kpi.Dashboard";
    static props = ["*"];
    static components = { DashboardChartCanvas };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.rootRef = useRef("root");
        this.state = useState({
            loading: true,
            error: "",
            dashboardId: Number(
                this.props.action?.params?.dashboard_id ||
                this.props.action?.context?.dashboard_id ||
                0
            ),
            dashboard: null,
            selectedDashboardId: 0,
            query: "",
            fullscreen: false,
        });
        this.refreshTimer = null;
        onWillStart(() => this.load());
        onMounted(() => this.scheduleRefresh());
        onWillUnmount(() => this.clearRefresh());
    }

    get elements() {
        const raw = this.state.dashboard?.element_data || {};
        const values = Array.isArray(raw) ? raw : Object.values(raw);
        const query = this.state.query.trim().toLowerCase();
        return values
            .filter((item) => !query || String(item.name || "").toLowerCase().includes(query))
            .sort((left, right) => Number(left.sequence || 0) - Number(right.sequence || 0));
    }

    get dashboards() {
        return this.state.dashboard?.dashboard_list || [];
    }

    get themeStyle() {
        let theme = this.state.dashboard?.theme_data;
        if (typeof theme === "string") {
            try {
                theme = JSON.parse(theme);
            } catch {
                theme = null;
            }
        }
        if (!theme) {
            return "";
        }
        return [
            `--dashboard-primary:${theme.dashboard_theme_primary_color || "#ffffff"}`,
            `--dashboard-secondary:${theme.dashboard_theme_secondary_color || "#f5f6f8"}`,
            `--dashboard-font:${theme.dashboard_theme_font_color || "#212529"}`,
        ].join(";");
    }

    async load(dashboardId = this.state.dashboardId) {
        this.clearRefresh();
        this.state.loading = true;
        this.state.error = "";
        try {
            if (!dashboardId) {
                const records = await this.orm.searchRead(
                    "dashboard_pro.main_dashboard",
                    [["dashboard_active", "=", true]],
                    ["id"],
                    { limit: 1 }
                );
                dashboardId = records[0]?.id || 0;
            }
            if (!dashboardId) {
                this.state.dashboard = {
                    name: "Dashboard",
                    dashboard_list: [],
                    element_data: {},
                };
                return;
            }
            const data = await this.orm.call(
                "dashboard_pro.main_dashboard",
                "get_dashboard_values_to",
                [dashboardId, false]
            );
            this.state.dashboardId = dashboardId;
            this.state.selectedDashboardId = dashboardId;
            this.state.dashboard = data;
        } catch (error) {
            console.error("OpenEduCat dashboard load failed", error);
            this.state.error = error.message || "Unable to load dashboard.";
        } finally {
            this.state.loading = false;
            this.scheduleRefresh();
        }
    }

    async changeDashboard(event) {
        const dashboardId = Number(event.target.value || 0);
        if (dashboardId) {
            await this.load(dashboardId);
        }
    }

    async refresh() {
        await this.load(this.state.dashboardId);
    }

    scheduleRefresh() {
        this.clearRefresh();
        const seconds = Number(this.state.dashboard?.interval_time || 0);
        if (seconds > 0) {
            this.refreshTimer = window.setTimeout(
                () => this.refresh(),
                seconds * 1000
            );
        }
    }

    clearRefresh() {
        if (this.refreshTimer) {
            window.clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    toggleFullscreen() {
        this.state.fullscreen = !this.state.fullscreen;
        this.rootRef.el?.classList.toggle(
            "o_dashboard_fullscreen",
            this.state.fullscreen
        );
    }

    formatValue(value) {
        return GlobalFunction.number_shorthand_function(Number(value || 0), 1);
    }

    color(value, fallback) {
        try {
            return GlobalFunction.convert_to_rgba_function(value);
        } catch {
            return fallback;
        }
    }

    parseJSON(value, fallback) {
        if (!value) {
            return fallback;
        }
        if (typeof value === "object") {
            return value;
        }
        try {
            return JSON.parse(value);
        } catch {
            return fallback;
        }
    }

    getListRows(item) {
        return this.parseJSON(item.json_list_data, {}).data_rows || [];
    }

    getListLabels(item) {
        return this.parseJSON(item.json_list_data, {}).label || [];
    }

    getTodoRows(item) {
        return this.parseJSON(item.json_todo_list_data, {}).data_rows || [];
    }

    getChartLabels(item) {
        const data = this.parseJSON(item.chart_data, {});
        return data.labels || data.label || [];
    }

    getChartValues(item) {
        const data = this.parseJSON(item.chart_data, {});
        const datasets = data.datasets || [];
        return datasets[0]?.data || data.data || [];
    }

    async openElement(item) {
        if (item.action) {
            await this.action.doAction(item.action);
            return;
        }
        if (item.model_name) {
            await this.action.doAction({
                type: "ir.actions.act_window",
                name: item.name,
                res_model: item.model_name,
                views: [[false, "list"], [false, "form"]],
                target: "current",
                domain: item.domain || [],
            });
        }
    }

    async openDashboardConfiguration() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Dashboard",
            res_model: "dashboard_pro.main_dashboard",
            res_id: this.state.dashboardId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async createElement() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Dashboard Element",
            res_model: "dashboard_pro.element",
            views: [[false, "form"]],
            target: "current",
            context: {
                default_dashboard_pro_dashboard_id: this.state.dashboardId,
            },
        });
    }
}

registry.category("actions").add("openeducat_dashboard_kpi", DashboardPro);
