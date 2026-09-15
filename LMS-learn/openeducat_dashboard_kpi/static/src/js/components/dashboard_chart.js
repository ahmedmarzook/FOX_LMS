/** @odoo-module **/

import { Component, onWillStart, onWillUnmount, useEffect, useRef } from "@odoo/owl";
import { buildDashboardChart, loadChartAssets } from "./chart_renderer";

export class DashboardChartCanvas extends Component {
    static template = "openeducat_dashboard_kpi.DashboardChartCanvas";
    static props = ["item"];

    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;

        onWillStart(() => loadChartAssets());

        useEffect(
            () => {
                this.renderChart();
                return () => this.destroyChart();
            },
            () => [this.canvasRef.el, this.props.item.chart_data, this.props.item.type_of_element]
        );

        onWillUnmount(() => this.destroyChart());
    }

    get chartData() {
        if (!this.props.item.chart_data) {
            return null;
        }
        if (typeof this.props.item.chart_data === "object") {
            return this.props.item.chart_data;
        }
        try {
            return JSON.parse(this.props.item.chart_data);
        } catch {
            return null;
        }
    }

    renderChart() {
        this.destroyChart();
        const canvasEl = this.canvasRef.el;
        const chartData = this.chartData;
        if (!canvasEl || !chartData || !(chartData.datasets || []).length) {
            return;
        }
        // eslint-disable-next-line no-undef
        if (typeof Chart === "undefined") {
            return;
        }
        this.chart = buildDashboardChart(canvasEl, {
            typeOfElement: this.props.item.type_of_element,
            chartData,
            chartTheme: this.props.item.chart_theme_selection,
            showDataValue: this.props.item.show_data_value,
            barChartStacked: this.props.item.bar_chart_stacked,
            semiCircleChart: this.props.item.semi_circle_chart,
        });
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}
