/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted, useRef } from "@odoo/owl";

// ─────────────────────────────────────────────
// Donut Chart Component
// ─────────────────────────────────────────────
class PtDonutChart extends Component {
    static template = "eds_smart_theme.DonutChart";
    static props = {
        segments: { type: Array, optional: true },
        size: { type: Number, optional: true },
    };

    setup() {
        this.canvasRef = useRef("canvas");
        onMounted(() => this._draw());
    }

    _draw() {
        const el = this.canvasRef.el;
        if (!el) return;
        const ctx = el.getContext("2d");
        const s = Number(this.props.size) || 160;
        const cx = s / 2, cy = s / 2;
        const R = s * 0.42, r = s * 0.27;
        const segs = this.props.segments || [];
        const total = segs.reduce((a, b) => a + (b.value || 0), 0) || 1;

        ctx.clearRect(0, 0, s, s);
        let angle = -Math.PI / 2;

        if (!segs.length) {
            ctx.beginPath();
            ctx.arc(cx, cy, R, 0, Math.PI * 2);
            ctx.arc(cx, cy, r, Math.PI * 2, 0, true);
            ctx.closePath();
            ctx.fillStyle = "#E9ECF6";
            ctx.fill();
        }

        segs.forEach(seg => {
            const arc = (seg.value / total) * Math.PI * 2;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, R, angle, angle + arc);
            ctx.arc(cx, cy, r, angle + arc, angle, true);
            ctx.closePath();
            ctx.fillStyle = seg.color;
            ctx.fill();
            ctx.strokeStyle = "#fff";
            ctx.lineWidth = 2.5;
            ctx.stroke();
            angle += arc;
        });

        const pct = segs[0] ? Math.round((segs[0].value / total) * 100) : 0;
        ctx.font = `bold ${s * 0.16}px 'Alexandria', sans-serif`;
        ctx.fillStyle = "#1A1D3B";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(`${pct}%`, cx, cy - 6);
        ctx.font = `${s * 0.09}px 'Alexandria', sans-serif`;
        ctx.fillStyle = "#8890B5";
        ctx.fillText("إشغال", cx, cy + s * 0.12);
    }
}

// ─────────────────────────────────────────────
// Main Dashboard
// ─────────────────────────────────────────────
export class PropertyThemeDashboard extends Component {
    static template = "eds_smart_theme.Dashboard";
    static components = { PtDonutChart };
    static props = ["*"];

    setup() {
        this.orm    = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            activeTab: "active",

            user: {
                name: "مدير النظام",
                role: "مشرف العقارات",
            },

            kpis: {
                totalProperties:    0,
                totalUnits:         0,
                rentedUnits:        0,
                availableUnits:     0,
                occupancyRate:      0,
                monthlyRevenue:     0,
                activeContracts:    0,
                pendingCheques:     0,
                expiringContracts:  0,
                overdueAmount:      0,
                bouncedCheques:     0,
                maintenanceUnits:   0,
            },

            contracts:     [],
            cheques:       [],
            donutSegments: [],

            quickLinks: [
                { label: "لوحة التحكم", icon: "fa-home",      color: "#6C5CE7", action: "eds_property_management.action_property_dashboard" },
                { label: "الإيجارات",   icon: "fa-money",     color: "#00CEC9", action: "eds_property_management.action_property_invoices"  },
                { label: "الحضور",      icon: "fa-clock-o",   color: "#4A90D9", action: null },
                { label: "الراتب",      icon: "fa-bank",      color: "#00B894", action: "eds_property_management.action_property_cheque"    },
                { label: "المهام",      icon: "fa-tasks",     color: "#F9A825", action: "eds_property_management.action_property_contract"  },
                { label: "التقارير",    icon: "fa-bar-chart", color: "#FF7675", action: null },
            ],
        });

        onMounted(() => this._loadData());
    }

    // ─── Data ───
    async _loadData() {
        this.state.loading = true;
        try {
            await Promise.all([
                this._loadKpis(),
                this._loadContracts(),
                this._loadCheques(),
                this._loadUser(),
            ]);
        } finally {
            this.state.loading = false;
        }
    }

    async _loadUser() {
        try {
            const [user] = await this.orm.searchRead(
                "res.users",
                [["id", "=", this.env.uid || 2]],
                ["name", "job_title", "department_id"],
                { limit: 1 }
            );
            if (user) {
                this.state.user.name = user.name || "مدير النظام";
                this.state.user.role = user.job_title || "مشرف العقارات";
            }
        } catch (_) { /* keep defaults */ }
    }

    async _loadKpis() {
        const props = await this.orm.searchRead(
            "property.property",
            [["state", "=", "active"]],
            ["unit_count", "rented_units", "available_units",
             "actual_monthly_revenue", "occupancy_rate"]
        );

        const totalProperties  = props.length;
        const totalUnits       = props.reduce((s, p) => s + p.unit_count, 0);
        const rentedUnits      = props.reduce((s, p) => s + p.rented_units, 0);
        const availableUnits   = props.reduce((s, p) => s + p.available_units, 0);
        const monthlyRevenue   = props.reduce((s, p) => s + p.actual_monthly_revenue, 0);
        const occupancyRate    = totalUnits ? Math.round((rentedUnits / totalUnits) * 100) : 0;
        const maintenanceUnits = Math.max(0, totalUnits - rentedUnits - availableUnits);

        const activeContracts = await this.orm.searchCount(
            "property.contract", [["state", "in", ["active", "expiring_soon"]]]
        );

        const today = new Date();
        const in90  = new Date(today.getTime() + 90 * 86400000);
        const expiringContracts = await this.orm.searchCount(
            "property.contract",
            [
                ["state", "in", ["active", "expiring_soon"]],
                ["end_date", "<=", in90.toISOString().split("T")[0]],
                ["end_date", ">=", today.toISOString().split("T")[0]],
            ]
        );

        const pendingCheques = await this.orm.searchCount(
            "property.cheque", [["state", "=", "pending"]]
        );
        const bouncedCheques = await this.orm.searchCount(
            "property.cheque", [["state", "=", "bounced"]]
        );

        const overdueInvs = await this.orm.searchRead(
            "account.move",
            [
                ["move_type", "=", "out_invoice"],
                ["property_contract_id", "!=", false],
                ["payment_state", "!=", "paid"],
                ["invoice_date_due", "<", today.toISOString().split("T")[0]],
                ["state", "=", "posted"],
            ],
            ["amount_residual"]
        );
        const overdueAmount = overdueInvs.reduce((s, i) => s + i.amount_residual, 0);

        Object.assign(this.state.kpis, {
            totalProperties, totalUnits, rentedUnits, availableUnits,
            monthlyRevenue, occupancyRate, maintenanceUnits,
            activeContracts, expiringContracts,
            pendingCheques, bouncedCheques, overdueAmount,
        });

        this.state.donutSegments = [
            { label: "مؤجرة",  value: rentedUnits,      color: "#6C5CE7" },
            { label: "متاحة",  value: availableUnits,   color: "#00CEC9" },
            { label: "صيانة",  value: maintenanceUnits, color: "#F9A825" },
        ];
    }

    async _loadContracts() {
        this.state.contracts = await this.orm.searchRead(
            "property.contract",
            [["state", "in", ["active", "confirmed", "expiring_soon"]]],
            ["name", "tenant_id", "unit_id", "annual_rent", "end_date", "state", "days_remaining"],
            { limit: 8, order: "write_date desc" }
        );
    }

    async _loadCheques() {
        this.state.cheques = await this.orm.searchRead(
            "property.cheque",
            [["state", "in", ["pending", "bounced"]]],
            ["name", "tenant_id", "amount", "due_date", "state", "bank_id"],
            { limit: 8, order: "due_date asc" }
        );
    }

    // ─── Formatters ───
    fmt(n) {
        if (!n && n !== 0) return "0";
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + " م";
        if (n >= 1_000)     return (n / 1_000).toFixed(0) + " ألف";
        return n.toLocaleString("ar-SA");
    }

    fmtDate(s) {
        if (!s) return "-";
        return new Date(s).toLocaleDateString("ar-SA", { month: "short", day: "numeric" });
    }

    initials(name) {
        if (!name) return "؟";
        const parts = name.trim().split(/\s+/);
        return parts.length > 1 ? parts[0][0] + parts[1][0] : name.substring(0, 2);
    }

    stateLabel(s) {
        return {
            active: "نشط", confirmed: "مؤكد", expiring_soon: "ينتهي قريباً",
            draft: "مسودة", expired: "منتهي", terminated: "مفسوخ"
        }[s] || s;
    }

    stateBadge(s) {
        return {
            active: "pt-badge-active", confirmed: "pt-badge-pending",
            expiring_soon: "pt-badge-expiring", expired: "pt-badge-expired"
        }[s] || "";
    }

    chequeBadge(s) {
        return { pending: "pt-badge-pending", cleared: "pt-badge-cleared", bounced: "pt-badge-bounced" }[s] || "";
    }

    chequeLabel(s) {
        return { pending: "معلق", deposited: "مودع", cleared: "محصّل", bounced: "مرتجع", cancelled: "ملغي" }[s] || s;
    }

    // ─── Navigation ───
    go(xmlid) { if (xmlid) this.action.doAction(xmlid); }

    goContracts()  { this.go("eds_property_management.action_property_contract");   }
    goProperties() { this.go("eds_property_management.action_property_property");   }
    goUnits()      { this.go("eds_property_management.action_property_unit_list");  }
    goCheques()    { this.go("eds_property_management.action_property_cheque");     }
    goInvoices()   { this.go("eds_property_management.action_property_invoices");   }

    openContract(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "property.contract",
            res_id: id,
            view_mode: "form",
            views: [[false, "form"]],
        });
    }

    openCheque(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "property.cheque",
            res_id: id,
            view_mode: "form",
            views: [[false, "form"]],
        });
    }

    setTab(tab) { this.state.activeTab = tab; }

    get filteredContracts() {
        if (this.state.activeTab === "pending") {
            return this.state.contracts.filter(c => c.state === "expiring_soon").slice(0, 8);
        }
        return this.state.contracts.slice(0, 8);
    }

    get filteredCheques() { return this.state.cheques.slice(0, 8); }
}

registry.category("actions").add("eds_property_theme_dashboard", PropertyThemeDashboard);
