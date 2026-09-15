/** @odoo-module **/

import { loadCSS, loadJS } from "@web/core/assets";
import GlobalFunction from "../formatting_function";
import { format } from "../formatting_function";

export async function loadChartAssets() {
    await loadJS("/openeducat_dashboard_kpi/static/lib/js/Chart.bundle.min.js");
    await loadJS("/openeducat_dashboard_kpi/static/lib/js/chartjs-plugin-datalabels.js");
    await loadCSS("/openeducat_dashboard_kpi/static/lib/css/Chart.min.css");
}

function chartFamilyOf(chartType) {
    switch (chartType) {
        case "pie":
        case "doughnut":
        case "polarArea":
            return "circle";
        case "bar":
        case "horizontalBar":
        case "line":
        case "area":
            return "square";
        default:
            return "none";
    }
}

function buildScales(chartData, chartType) {
    let scales = {};
    if (chartData?.show_second_y_scale && chartType === "bar") {
        scales.yAxes = [
            {
                type: "linear",
                display: true,
                position: "left",
                id: "y-axis-0",
                gridLines: { display: true },
                labels: { show: true },
            },
            {
                type: "linear",
                display: true,
                position: "right",
                id: "y-axis-1",
                labels: { show: true },
                ticks: {
                    beginAtZero: true,
                    callback(value) {
                        return formatTick(value, chartData);
                    },
                },
            },
        ];
    }
    return scales;
}

function formatTick(value, chartData) {
    const selection = chartData?.selection;
    if (selection === "monetary") {
        const data = GlobalFunction.number_shorthand_function(value, 1);
        return GlobalFunction.currency_monetary_function(data, chartData.currency);
    } else if (selection === "custom") {
        return `${GlobalFunction.number_shorthand_function(value, 1)} ${chartData.field || ""}`;
    }
    return GlobalFunction.number_shorthand_function(value, 1);
}

function formatAmount(kAmount, chartData) {
    const selection = chartData?.selection;
    if (selection === "monetary") {
        return GlobalFunction.currency_monetary_function(kAmount, chartData.currency);
    } else if (selection === "custom") {
        return `${format.float(kAmount)} ${chartData.field || ""}`;
    }
    return format.float(kAmount);
}

function paletteGradient(palette) {
    switch (palette) {
        case "warm":
            return {
                0: [255, 255, 255, 1],
                20: [254, 235, 101, 1],
                45: [228, 82, 27, 1],
                65: [77, 52, 47, 1],
                100: [0, 0, 0, 1],
            };
        case "neon":
            return {
                0: [255, 255, 255, 1],
                20: [255, 236, 179, 1],
                45: [232, 82, 133, 1],
                65: [106, 27, 154, 1],
                100: [0, 0, 0, 1],
            };
        case "cool":
        default:
            return {
                0: [255, 255, 255, 1],
                20: [220, 237, 200, 1],
                45: [66, 179, 213, 1],
                65: [26, 39, 62, 1],
                100: [0, 0, 0, 1],
            };
    }
}

const DEFAULT_COLOR_SET = [
    "#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600",
    "#8a79fd", "#b1b5be", "#1c425c", "#8c2620", "#71ecef",
    "#0b4295", "#f2e6ce", "#1379e7",
];

function buildColors(palette, count) {
    if (palette === "default") {
        const colors = [];
        for (let i = 0, counter = 0; i < count; i++, counter++) {
            if (counter >= DEFAULT_COLOR_SET.length) {
                counter = 0;
            }
            colors.push(DEFAULT_COLOR_SET[counter]);
        }
        return colors;
    }
    const gradient = paletteGradient(palette);
    const gradientKeys = Object.keys(gradient)
        .map(Number)
        .sort((a, b) => a - b);
    const colors = [];
    for (let i = 0; i < count; i++) {
        const gradientIndex = (i + 1) * (100 / (count + 1));
        for (let j = 0; j < gradientKeys.length; j++) {
            const gradientKey = gradientKeys[j];
            if (gradientIndex === gradientKey) {
                colors[i] = `rgba(${gradient[gradientKey].toString()})`;
                break;
            } else if (gradientIndex < gradientKey) {
                const prevKey = gradientKeys[j - 1];
                const part = (gradientIndex - prevKey) / (gradientKey - prevKey);
                const color = [];
                for (let k = 0; k < 4; k++) {
                    color[k] =
                        gradient[prevKey][k] -
                        (gradient[prevKey][k] - gradient[gradientKey][k]) * part;
                    if (k < 3) {
                        color[k] = Math.round(color[k]);
                    }
                }
                colors[i] = `rgba(${color.toString()})`;
                break;
            }
        }
    }
    return colors;
}

function applyColors(chart, chartType, chartFamily, chartColors, chartData, extras) {
    const options = chart.config.options;
    const datasets = chart.config.data.datasets;

    options.legend = options.legend || { labels: {} };
    options.legend.labels = options.legend.labels || {};
    options.legend.labels.usePointStyle = true;

    if (chartFamily === "circle") {
        options.legend.position = extras.showDataValue ? "top" : "bottom";
        options.layout.padding.top = extras.showDataValue ? 10 : options.layout.padding.top;
        options.layout.padding.bottom = extras.showDataValue ? 20 : options.layout.padding.bottom;

        options.plugins.datalabels.align = "center";
        options.plugins.datalabels.anchor = "end";
        options.plugins.datalabels.borderColor = "white";
        options.plugins.datalabels.borderRadius = 25;
        options.plugins.datalabels.borderWidth = 2;
        options.plugins.datalabels.clamp = true;
        options.plugins.datalabels.clip = false;

        options.tooltips = options.tooltips || {};
        options.tooltips.callbacks = {
            title(tooltipItem, data) {
                const kAmount =
                    data.datasets[tooltipItem[0].datasetIndex].data[tooltipItem[0].index];
                return `${data.datasets[tooltipItem[0].datasetIndex].label} : ${formatAmount(kAmount, chartData)}`;
            },
            label(tooltipItem, data) {
                return data.labels[tooltipItem.index];
            },
        };
        for (let i = 0; i < datasets.length; i++) {
            datasets[i].backgroundColor = chartColors;
            datasets[i].borderColor = "rgba(255,255,255,1)";
        }
        if (extras.semiCircleChart && (chartType === "pie" || chartType === "doughnut")) {
            options.rotation = 1 * Math.PI;
            options.circumference = 1 * Math.PI;
        }
    } else if (chartFamily === "square") {
        options.scales = options.scales || {};
        options.scales.xAxes = options.scales.xAxes || [{ gridLines: {}, ticks: {} }];
        options.scales.yAxes = options.scales.yAxes || [{ ticks: {} }];
        options.scales.xAxes[0].gridLines = options.scales.xAxes[0].gridLines || {};
        options.scales.xAxes[0].gridLines.display = false;
        options.scales.yAxes[0].ticks = options.scales.yAxes[0].ticks || {};
        options.scales.yAxes[0].ticks.beginAtZero = true;
        options.plugins.datalabels.align = "end";
        options.plugins.datalabels.formatter = (value) => formatTick(value, chartData);

        if (chartType === "line") {
            options.plugins.datalabels.backgroundColor = (context) => context.dataset.borderColor;
        }

        if (chartType === "horizontalBar") {
            options.scales.xAxes[0].ticks.callback = (value) => formatTick(value, chartData);
            options.scales.xAxes[0].ticks.beginAtZero = true;
        } else {
            options.scales.yAxes[0].ticks.callback = (value) => formatTick(value, chartData);
        }

        options.tooltips = options.tooltips || {};
        options.tooltips.callbacks = {
            label(tooltipItem, data) {
                const kAmount =
                    data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                return `${data.datasets[tooltipItem.datasetIndex].label} : ${formatAmount(kAmount, chartData)}`;
            },
        };

        for (let i = 0; i < datasets.length; i++) {
            switch (extras.rawChartType) {
                case "bar":
                case "horizontalBar":
                    if (datasets[i].type === "line") {
                        datasets[i].borderColor = chartColors[i];
                        datasets[i].backgroundColor = "rgba(255,255,255,0)";
                        datasets[i].datalabels = { backgroundColor: chartColors[i] };
                    } else {
                        datasets[i].backgroundColor = chartColors[i];
                        datasets[i].borderColor = "rgba(255,255,255,0)";
                        options.scales.xAxes[0].stacked = extras.barChartStacked;
                        options.scales.yAxes[0].stacked = extras.barChartStacked;
                    }
                    break;
                case "line":
                    datasets[i].borderColor = chartColors[i];
                    datasets[i].backgroundColor = "rgba(255,255,255,0)";
                    break;
                case "area":
                    datasets[i].borderColor = chartColors[i];
                    break;
            }
        }
    }
    chart.update();
}

/**
 * Build (or rebuild) a Chart.js instance on the given canvas element from
 * the same "chart_data" JSON contract used across dashboard_pro.element records.
 *
 * @param {HTMLCanvasElement} canvasEl
 * @param {Object} params
 * @param {string} params.typeOfElement e.g. "bar_chart", "polarArea_chart"
 * @param {Object} params.chartData parsed chart_data (labels/datasets/selection/currency/field)
 * @param {string} [params.chartTheme]
 * @param {boolean} [params.showDataValue]
 * @param {boolean} [params.barChartStacked]
 * @param {boolean} [params.semiCircleChart]
 * @returns {Chart} the created Chart.js instance (caller owns destroy())
 */
export function buildDashboardChart(canvasEl, params) {
    const rawChartType = String(params.typeOfElement || "").split("_")[0];
    const chartType = rawChartType === "area" ? "line" : rawChartType;
    const chartFamily = chartFamilyOf(rawChartType);
    const chartData = params.chartData || { labels: [], datasets: [] };

    const scales = buildScales(chartData, rawChartType);

    // eslint-disable-next-line no-undef
    const chart = new Chart(canvasEl, {
        type: chartType,
        // eslint-disable-next-line no-undef
        plugins: [ChartDataLabels],
        data: {
            labels: chartData.labels || [],
            datasets: chartData.datasets || [],
        },
        options: {
            maintainAspectRatio: false,
            animation: { easing: "easeInQuad" },
            layout: { padding: { bottom: 0 } },
            scales,
            plugins: {
                datalabels: {
                    backgroundColor: (context) => context.dataset.backgroundColor,
                    borderRadius: 4,
                    color: "white",
                    font: { weight: "bold" },
                    anchor: "center",
                    display: "auto",
                    clamp: true,
                    formatter(value, ctx) {
                        const sum = (ctx.dataset.data || []).reduce(
                            (acc, item) => acc + Number(item || 0),
                            0
                        );
                        return sum === 0 ? "0%" : `${((value * 100) / sum).toFixed(2)}%`;
                    },
                },
            },
        },
    });

    if (chartData.datasets && chartData.datasets.length > 0) {
        const count =
            chartFamily === "circle"
                ? (chartData.datasets[0]?.data || []).length
                : chartData.datasets.length;
        const chartColors = buildColors(params.chartTheme || "cool", count);
        applyColors(chart, chartType, chartFamily, chartColors, chartData, {
            rawChartType,
            showDataValue: params.showDataValue,
            barChartStacked: params.barChartStacked,
            semiCircleChart: params.semiCircleChart,
        });
    }

    return chart;
}
