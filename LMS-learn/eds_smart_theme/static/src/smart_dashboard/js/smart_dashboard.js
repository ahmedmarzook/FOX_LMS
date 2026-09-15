/** @odoo-module **/

import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc as jsonrpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { getUiDirection, getUiLocale, isUiArabic, notifyUiDirection } from "./ui_direction";

const ARROW_SM = '<i class="fa-solid fa-arrow-left arrow-sm" aria-hidden="true"></i>';

const UI_LABELS_AR = {
    "Leave balance": "رصيد الإجازات",
    "Emergency leave balance": "رصيد اضطراري",
    "Remote work": "العمل عن بعد",
    "Monthly permission": "استئذان شهري",
    "Annual permission": "استئذان سنوي",
    "Annual performance review appointment": "موعد تقييم الأداء السنوي",
    "Leadership skills development workshop": "ورشة تطوير مهارات القيادة",
    "Administrative review • HR department": "تقييم إداري - قسم الموارد البشرية",
    "Training • Main meeting hall": "تدريب • القاعة الرئيسية",
    "December": "ديسمبر",
    "Upcoming": "قادم",
    "Ongoing": "قائم",
    "Past": "فائت",
    "View all": "عرض الكل",
};

function formatPageLabel(page, total) {
    const key = "Page %s of %s";
    const translated = String(_t(key, page, total));
    if (translated !== key) {
        return translated;
    }
    if (isUiArabic()) {
        return `الصفحة ${page} من ${total}`;
    }
    return `Page ${page} of ${total}`;
}

/** _t() + ar.po; Arabic fallback when translations are not loaded yet. */
function localizedLabel(text) {
    if (text == null || text === "") {
        return "";
    }
    const key = String(text);
    const translated = String(_t(key));
    if (translated !== key) {
        return translated;
    }
    if (isUiArabic()) {
        return UI_LABELS_AR[key] || key;
    }
    return key;
}

function kpiLabel(enKey) {
    return localizedLabel(enKey);
}

const EVENT_STATUS_LABELS = {
    upcoming: "Upcoming",
    ongoing: "Ongoing",
    past: "Past",
};

function resolveEventStatus(event) {
    const status = event?.status;
    if (status === "upcoming" || status === "ongoing" || status === "past") {
        return status;
    }
    const now = Date.now();
    const begin = event?.date_begin ? Date.parse(event.date_begin) : Number.NaN;
    const end = event?.date_end ? Date.parse(event.date_end) : Number.NaN;
    if (!Number.isNaN(end) && end < now) {
        return "past";
    }
    if (!Number.isNaN(begin) && begin <= now && (Number.isNaN(end) || end >= now)) {
        return "ongoing";
    }
    return "upcoming";
}

function eventStatusLabel(status) {
    return localizedLabel(EVENT_STATUS_LABELS[status] || EVENT_STATUS_LABELS.upcoming);
}

/** Inline SVGs for KPI glyphs (Odoo backend ships Font Awesome 4 only). */
const KPI_ICON_CALENDAR_CHECK =
    '<svg class="kpi-fa-svg" viewBox="0 0 448 512" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><path fill="currentColor" d="M128 0c17.7 0 32 14.3 32 32V64H288V32c0-17.7 14.3-32 32-32s32 14.3 32 32V64h48c26.5 0 48 21.5 48 48v48H0V112C0 85.5 21.5 64 48 64H96V32c0-17.7 14.3-32 32-32zM0 192H448V464c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V192zm305-51.3l31 31c9.4 9.4 9.4 24.6 0 33.9L273 353c-9.4 9.4-24.6 9.4-33.9 0l-96-96c-9.4-9.4-9.4-24.6 0-33.9l31-31c9.4-9.4 24.6-9.4 33.9 0l47 47L351 112c9.4-9.4 24.6-9.4 33.9 0z"/></svg>';
const KPI_ICON_CLOCK =
    '<svg class="kpi-fa-svg" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><path fill="currentColor" d="M256 0a256 256 0 1 1 0 512A256 256 0 1 1 256 0zM232 120V256c0 8 4 15.5 10.7 20l96 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2V120c0-13.3-10.7-24-24-24s-24 10.7-24 24z"/></svg>';

/** Fixed 5-column layout matching the portal mockup; API rows fill slots by sequence. */
function getKpiSlots() {
    return [
        {
            label: kpiLabel("Leave balance"),
            unit: "days",
            style: { bg: "var(--lilac)" },
            icon: KPI_ICON_CALENDAR_CHECK,
        },
        {
            label: kpiLabel("Emergency leave balance"),
            unit: "days",
            style: { bg: "var(--yellow)" },
            icon: '<i class="fa fa-exclamation-triangle" aria-hidden="true"></i>',
        },
        {
            label: kpiLabel("Remote work"),
            unit: "days",
            style: { bg: "var(--mint)" },
            icon: '<i class="fa fa-laptop" aria-hidden="true"></i>',
        },
        {
            label: kpiLabel("Monthly permission"),
            unit: "hours",
            style: { bg: "var(--blue)" },
            icon: '<i class="fa fa-calendar-o" aria-hidden="true"></i>',
        },
        {
            label: kpiLabel("Annual permission"),
            unit: "hours",
            style: { bg: "#5d4b8f" },
            icon: KPI_ICON_CLOCK,
        },
    ];
}

function defaultKpiValue(unit) {
    return unit === "hours" ? "0:00" : "0";
}

function buildKpiDisplayRows(leaveKpis) {
    const apiRows = Array.isArray(leaveKpis) ? leaveKpis : [];
    return getKpiSlots().map((slot, index) => {
        const api = apiRows[index];
        const unit = api?.unit || slot.unit;
        return {
            label: slot.label,
            value: api?.value ?? defaultKpiValue(unit),
            unit,
            style: slot.style,
            icon: slot.icon,
        };
    });
}

function formatKpiDisplayValue(kpi) {
    const raw = kpi.value ?? defaultKpiValue(kpi.unit);
    if (isUiArabic()) {
        return kpi.unit === "hours" ? `${raw} ساعة` : `${raw} يوم`;
    }
    return kpi.unit === "hours" ? _t("%s hours", raw) : _t("%s days", raw);
}

function getMockNews() {
    return {
        general: [
            {
                id: "g1",
                title: _t(
                    "Administrative decision: cancel institution-level employee issues request"
                ),
                date: _t("October 30, 2025"),
                dot: "#ef5364",
                image_url:
                    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=900&q=80",
            },
            {
                id: "g2",
                title: _t("Leave balance update for year 2026"),
                date: _t("October 14, 2025"),
                dot: "#f2b741",
                image_url:
                    "https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=900&q=80",
            },
        ],
        press: [
            {
                id: "p1",
                title: _t("Mawhiba launches quality initiative to support national talents"),
                date: _t("September 22, 2025"),
                dot: "#67a0ea",
                image_url:
                    "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=80",
            },
        ],
        employees: [
            {
                id: "e1",
                title: _t("New employee welfare package for year 2026"),
                date: _t("November 11, 2025"),
                dot: "#24d4bc",
                image_url:
                    "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=900&q=80",
            },
        ],
    };
}

function getMockDecisions() {
    return [
        {
            id: 1,
            title: _t("Administrative procedure: cancel guide for event staff rewards at Mawhiba"),
        },
        { id: 2, title: _t("Leave balance update for year 2035") },
        { id: 3, title: _t("Emergency leave policy in the organization") },
    ];
}

function getMockEvents() {
    const now = Date.now();
    const day = 24 * 60 * 60 * 1000;
    return [
        {
            title: "Annual performance review appointment",
            meta: "Administrative review • HR department",
            day: "07",
            month: "December",
            color: "#286fd4",
            status: "upcoming",
            date_begin: new Date(now + 5 * day).toISOString(),
            date_end: new Date(now + 5 * day + 2 * 60 * 60 * 1000).toISOString(),
        },
        {
            title: "Leadership skills development workshop",
            meta: "Training • Main meeting hall",
            day: "12",
            month: "December",
            color: "#f3bb22",
            status: "ongoing",
            date_begin: new Date(now - day).toISOString(),
            date_end: new Date(now + day).toISOString(),
        },
    ];
}

function getMockPendingActivityRows() {
    return [
        {
            id: 1,
            can_approve: true,
            code: "HR-2026-0001",
            title: _t("New employee contract"),
            status: _t("Pending"),
            statusKey: "pending",
            owner: _t("Human resources"),
        },
        {
            id: 2,
            can_approve: true,
            code: "HR-2026-0003",
            title: _t("Semi-annual performance appraisal"),
            status: _t("Pending"),
            statusKey: "pending",
            owner: _t("Department manager"),
        },
    ];
}

function getMockClosedTaskRows() {
    return [
        {
            code: "HR-2025-0099",
            title: _t("Leave balance update"),
            status: _t("Done"),
            statusKey: "closed",
            owner: _t("Human resources"),
        },
    ];
}

function getMockPendingRequestRows() {
    return [
        {
            code: "REQ-2026-0007",
            title: _t("Annual leave request"),
            status: _t("Pending"),
            statusKey: "pending",
            owner: _t("Human resources"),
        },
    ];
}

function getMockApprovedRequestRows() {
    return [
        {
            code: "REQ-2025-0042",
            title: _t("Permission request"),
            status: _t("Approved"),
            statusKey: "closed",
            owner: _t("Human resources"),
        },
    ];
}

const QUICK_LINK_COLORS = [
    { color: "#ffe7b7", text: "#ce8c0d" },
    { color: "#ecd2ff", text: "#9160cc" },
    { color: "#d9ebff", text: "#5590dc" },
    { color: "#ddeefb", text: "#6b94cc" },
    { color: "#ddffcf", text: "#6eae4a" },
    { color: "#ffd4cf", text: "#d06a55" },
    { color: "#dcd6ef", text: "#564d78" },
    { color: "#ffe4bf", text: "#e19a1a" },
];

function normalize(value) {
    return (value || "").toLowerCase().trim();
}

function rowKey(row) {
    return String(row.id ?? row.code ?? "");
}

function escapeHtml(value) {
    return (value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function truncateText(value, maxLength) {
    const text = String(value || "");
    return text.length > maxLength ? text.slice(0, maxLength) : text;
}

function formatOwnerName(owner) {
    return String(owner || "").trim();
}

function mapPortalServiceItem(item) {
    const href = (item.href || item.link_url || "").trim();
    const external = href.startsWith("http://") || href.startsWith("https://");
    return {
        id: item.id,
        label: item.label || item.name || "",
        href: href || "#",
        action: item.action || null,
        target: external ? "_blank" : "",
        rel: external ? "noopener noreferrer" : "",
    };
}

function mapPortalLinkItem(item, index, palette) {
    const icon = (item.icon || "").trim();
    const isFaIcon = icon.startsWith("fa");
    const href = (item.href || item.link_url || "").trim();
    const external = href.startsWith("http://") || href.startsWith("https://");
    const colors = palette || QUICK_LINK_COLORS[index % QUICK_LINK_COLORS.length];
    return {
        id: item.id,
        label: item.label || item.name || "",
        iconClass: isFaIcon ? icon : "",
        iconText: isFaIcon ? "" : icon || "📋",
        href: href || "#",
        target: external ? "_blank" : "",
        rel: external ? "noopener noreferrer" : "",
        color: colors.color,
        text: colors.text,
    };
}

function openNewsUrl(url) {
    if (!url || url === "#") {
        return false;
    }
    window.open(url, "_blank", "noopener,noreferrer");
    return true;
}

function formatTodayLocale() {
    return new Date().toLocaleDateString(getUiLocale(), {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

const PLACEHOLDER_AVATAR = "/web/static/img/placeholder.png";
const PLACEHOLDER_FEATURED_NEWS =
    "/web/static/img/placeholder.png";

const VIEW_ALL_URLS = {
    news: {
        general: "/news",
        press: "/press_news",
        employees: "/employee_news",
    },
    decisions: "/decisions_list",
    events: "/event",
};

function setImageWithFallback(img, url) {
    if (!img) {
        return;
    }
    img.onerror = () => {
        img.onerror = null;
        img.src = PLACEHOLDER_AVATAR;
    };
    img.src = url || PLACEHOLDER_AVATAR;
}

export class SmartPortalDashboard extends Component {
    static template = "eds_smart_theme.SmartPortalDashboard";
    static props = ["*"];

    setup() {
        this.rootRef = useRef("dashboardRoot");
        this.actionService = useService("action");
        this.employeeProfileAction = null;
        this.labelProfilePicture = _t("Profile picture");
        this.labelMyProfile = _t("My profile");
        this.labelWelcome = `${_t("Welcome!")} 👋`;
        this.labelRecentlyJoined = _t("Recently joined");
        this.labelPreviousProfile = _t("Previous profile");
        this.labelNextProfile = _t("Next profile");
        this.labelEmployeePhoto = _t("Employee photo");
        this.labelMyTasks = _t("My tasks");
        this.labelMyRequests = _t("My requests");
        this.labelPendingTasks = _t("Pending tasks");
        this.labelClosedTasks = _t("Closed tasks");
        this.labelRequestsInProgress = _t("Requests in progress");
        this.labelFinishedRequests = _t("Finished requests");
        this.labelLocked = _t("Locked");
        this.labelTaskNo = _t("Task no.");
        this.labelServiceSystem = _t("Service / system");
        this.labelTaskStatus = _t("Task status");
        this.labelTaskOwner = _t("Task owner");
        this.labelRequestLink = _t("Request link");
        this.labelApprove = _t("Approve");
        this.labelNextPage = _t("Next page");
        this.labelPreviousPage = _t("Previous page");
        this.labelPageOf = formatPageLabel(1, 1);
        this.labelSelfServices = _t("Self services");
        this.labelNews = _t("News");
        this.labelPressNews = _t("Press news");
        this.labelEmployeeNews = _t("Employee news");
        this.labelCircularsDecisions = _t("Circulars and decisions");
        this.labelUpcomingEvents = _t("Upcoming events");
        this.labelViewAll = localizedLabel("View all");
        this.labelQuickLinks = _t("Quick links");
        this.labelPrivacyPolicy = _t("Privacy Policy");
        this.labelCopyright = _t(
            ".كل الحقوق محفوظة لمؤسسة إدراك للانظمة %s",
            new Date().getFullYear()
        );
        onMounted(() => {
            this.initDashboard();
            notifyUiDirection(getUiDirection());
        });
    }

    get direction() {
        return getUiDirection();
    }

    /** Open the current user's `hr.employee.public` form. */
    async onOpenMyProfile() {
        let action = this.employeeProfileAction;
        if (!action?.type) {
            action = await jsonrpc(
                "/eds_smart_theme/smart_dashboard/employee_profile_action",
                {}
            );
        }
        if (action?.type) {
            await this.actionService.doAction(action);
        }
    }

    async initDashboard() {
        const root = this.rootRef.el;
        if (!root) {
            return;
        }

        const toast = root.querySelector("#toast");
        const serviceGrid = root.querySelector("#serviceGrid");
        const taskBody = root.querySelector("#taskTableBody");
        const pageLabel = root.querySelector("#pageLabel");
        // News/Circulars/Upcoming events panels were removed from the template;
        // these detached stand-ins keep the rendering code below a harmless no-op.
        const newsList = root.querySelector("#newsList") || document.createElement("div");
        const featuredNews = root.querySelector("#featuredNews") || document.createElement("div");
        const decisionsList = root.querySelector("#decisionsList") || document.createElement("div");
        const timelineList = root.querySelector("#timelineList") || document.createElement("div");
        const quickLinksRoot = root.querySelector("#quickLinks");
        const searchInput = root.querySelector("#globalSearch");
        let toastTimer = 0;

        const showToast = (message) => {
            toast.textContent = message;
            toast.classList.add("show");
            window.clearTimeout(toastTimer);
            toastTimer = window.setTimeout(() => toast.classList.remove("show"), 1800);
        };

        let newsContent = { general: [], press: [], employees: [] };
        let newsLoadedFromApi = false;
        let decisions = [...getMockDecisions()];
        let events = [...getMockEvents()];
        /** Dashboard preview lists; restored when the global search is cleared. */
        let defaultNewsContent = {
            general: [],
            press: [],
            employees: [],
        };
        let defaultDecisions = [...decisions];
        let defaultEvents = [...events];
        let pendingActivityRows = [];
        let closedTaskRows = [];
        let pendingRequestRows = [];
        let approvedRequestRows = [];
        let tableLoadedFromApi = false;
        let quickLinks = [];
        let serviceCategories = [];
        let newJoiners = [];
        let joinerIndex = 0;
        let portalSearchTimer = 0;
        let portalSearchSeq = 0;
        const attendanceCardActions = new Map();
        const rowActions = new Map();
        const serviceItemActions = new Map();
        let approvingActivityId = null;

        const state = {
            search: "",
            serviceGroup: "",
            tableTab: "tasks",
            tableFilter: "pending",
            page: 1,
            pageSize: 4,
            newsTab: "general",
            featuredNewsId: null,
            quickLink: "",
        };

        const setActiveButton = (container, selector, value, attr) => {
            if (!container) {
                return;
            }
            container.querySelectorAll(selector).forEach((button) => {
                button.classList.toggle("active", button.getAttribute(attr) === value);
            });
        };

        const renderKpis = (leaveKpis, options = {}) => {
            const kpiRow = root.querySelector("#kpiRow");
            if (!kpiRow) {
                return;
            }
            const loading = options.loading === true;
            kpiRow.classList.toggle("kpi-row--loading", loading);
            kpiRow.setAttribute("aria-busy", loading ? "true" : "false");

            if (loading) {
                kpiRow.innerHTML = getKpiSlots().map((slot) => {
                    return `<article class="kpi-card kpi-card--skeleton"><div class="kpi-icon" style="background: ${slot.style.bg}">${slot.icon}</div><div class="kpi-title">${escapeHtml(slot.label)}</div><div class="kpi-value">${escapeHtml(formatKpiDisplayValue(slot))}</div></article>`;
                }).join("");
                return;
            }

            kpiRow.innerHTML = buildKpiDisplayRows(leaveKpis)
                .map((kpi) => {
                    const label = escapeHtml(kpi.label || "");
                    const value = escapeHtml(formatKpiDisplayValue(kpi));
                    return `<article class="kpi-card"><div class="kpi-icon" style="background: ${kpi.style.bg}">${kpi.icon}</div><div class="kpi-title">${label}</div><div class="kpi-value">${value}</div></article>`;
                })
                .join("");
        };

        const renderWelcome = (profile, leaveKpis, pendingCount) => {
            const welcomeTitle = root.querySelector("#welcomeTitle");
            const welcomeSubtitle = root.querySelector("#welcomeSubtitle");
            const welcomeMeta = root.querySelector("#welcomeMeta");
            const welcomePending = root.querySelector("#welcomePending");
            const welcomeAvatar = root.querySelector("#welcomeAvatar");
            if (!profile) {
                return;
            }
            if (welcomeTitle) {
                welcomeTitle.textContent = profile.name
                    ? _t("Welcome, %s", profile.name) + " 👋"
                    : _t("Welcome!") + " 👋";
            }
            if (welcomeSubtitle) {
                const parts = [profile.department, profile.job_title].filter(Boolean);
                welcomeSubtitle.textContent = parts.join(_t(", "));
            }
            if (welcomeMeta) {
                const metaLines = [];
                if (profile.grade) {
                    metaLines.push(_t("Grade: %s", profile.grade));
                }
                if (profile.employee_no) {
                    metaLines.push(_t("Employee no.: %s", profile.employee_no));
                }
                metaLines.push(formatTodayLocale());
                welcomeMeta.innerHTML = metaLines.map((line) => escapeHtml(line)).join("<br>");
            }
            if (welcomePending) {
                welcomePending.textContent =
                    pendingCount > 0 ? _t("You have %s pending requests", pendingCount) : "";
            }
            setImageWithFallback(welcomeAvatar, profile.avatar_url);
            renderKpis(Array.isArray(leaveKpis) ? leaveKpis : []);
        };

        const renderEmployeeCarousel = () => {
            const joinerPhoto = root.querySelector("#joinerPhoto");
            const joinerName = root.querySelector("#joinerName");
            const joinerDepartment = root.querySelector("#joinerDepartment");
            const joinerJob = root.querySelector("#joinerJob");
            const joinerDots = root.querySelector("#joinerDots");
            const carousel = root.querySelector("#employeeCarousel");
            if (!newJoiners.length) {
                if (carousel) {
                    carousel.style.display = "none";
                }
                return;
            }
            if (carousel) {
                carousel.style.display = "";
            }
            const item = newJoiners[joinerIndex];
            setImageWithFallback(joinerPhoto, item.image_url);
            if (joinerName) {
                joinerName.textContent = item.employee_name || item.title || "";
            }
            if (joinerDepartment) {
                joinerDepartment.textContent = item.department || "";
            }
            if (joinerJob) {
                joinerJob.textContent = item.job_title || item.subtitle || "";
            }
            if (joinerDots) {
                joinerDots.innerHTML = newJoiners
                    .map((_, idx) => `<span class="${idx === joinerIndex ? "active" : ""}"></span>`)
                    .join("");
            }
        };

        const renderAttendance = (attendance) => {
            const grid = root.querySelector("#attendanceGrid");
            if (!grid) {
                return;
            }
            attendanceCardActions.clear();
            const cards = attendance?.cards?.length
                ? attendance.cards
                : attendance && Object.keys(attendance).length
                  ? [
                        {
                            key: "schedule",
                            full: true,
                            title: attendance.schedule_title || _t("Attendance and departure"),
                            subtitle:
                                attendance.schedule_label ??
                                _t("%s days", attendance.schedule_count ?? 0),
                        },
                        {
                            key: "absence",
                            full: false,
                            title: _t("Absence"),
                            subtitle: _t("%s days", attendance.absence_days ?? 0),
                        },
                        {
                            key: "delay",
                            full: false,
                            title: _t("Late"),
                            subtitle: _t("%s hours", attendance.delay_hours ?? 0),
                        },
                        {
                            key: "no_task",
                            full: true,
                            title: _t("No fingerprint"),
                            subtitle: String(attendance.no_task_count ?? 0),
                        },
                    ]
                  : [];
            if (!cards.length) {
                grid.innerHTML = `<div class="empty-state">${escapeHtml(_t("لا توجد بيانات حضور وانصراف"))}</div>`;
                return;
            }
            grid.innerHTML = cards
                .map((card) => {
                    if (card.action) {
                        attendanceCardActions.set(card.key, card.action);
                    }
                    const fullClass = card.full ? " full" : "";
                    const title = escapeHtml(card.title || "");
                    const subtitle = escapeHtml(card.subtitle || "");
                    return `<button class="attendance-card${fullClass}" type="button" data-attendance-key="${escapeHtml(card.key)}"><div><strong>${title}</strong><span>${subtitle}</span></div>${ARROW_SM}</button>`;
                })
                .join("");
        };

        const renderServiceTabs = () => {
            const tabs = root.querySelector("#serviceTabs");
            if (!tabs) {
                return;
            }
            if (!serviceCategories.length) {
                tabs.innerHTML = "";
                serviceGrid.innerHTML =
                    `<div class="empty-state">${escapeHtml(
                        _t("لا توجد خدمات ذاتية.")
                    )}</div>`;
                return;
            }
            if (!serviceCategories.some((cat) => cat.key === state.serviceGroup)) {
                state.serviceGroup = serviceCategories[0].key;
            }
            tabs.innerHTML = serviceCategories
                .map(
                    (cat) =>
                        `<button type="button" data-group="${escapeHtml(cat.key)}" class="${
                            cat.key === state.serviceGroup ? "active" : ""
                        }">${escapeHtml(cat.label)}</button>`
                )
                .join("");
        };

        const renderServices = () => {
            if (!serviceCategories.length) {
                return;
            }
            const category = serviceCategories.find((cat) => cat.key === state.serviceGroup);
            const items = (category?.items || []).filter((item) =>
                normalize(item.label).includes(normalize(state.search))
            );
            serviceItemActions.clear();
            serviceGrid.innerHTML = items.length
                ? items
                      .map((item) => {
                          const label = escapeHtml(item.label);
                          if (item.action?.type) {
                              serviceItemActions.set(String(item.id), item.action);
                              return `<button class="service-card" type="button" data-service-id="${item.id}"><strong>${label}</strong>${ARROW_SM}</button>`;
                          }
                          const href = escapeHtml(item.href);
                          return `<a class="service-card" href="${href}" data-service-id="${item.id}" target="${item.target || ""}" rel="${item.rel || ""}"><strong>${label}</strong>${ARROW_SM}</a>`;
                      })
                      .join("")
                : `<div class="empty-state">${escapeHtml(_t("No services match your search."))}</div>`;
        };

        const rowsByView = () => ({
            "tasks:pending": pendingActivityRows,
            "tasks:closed": closedTaskRows,
            "requests:pending": pendingRequestRows,
            "requests:closed": approvedRequestRows,
        });

        const sortRowsNewestFirst = (rows) =>
            [...(rows || [])].sort((a, b) => Number(b?.id || 0) - Number(a?.id || 0));

        const getTableRows = () => {
            const rows = rowsByView()[`${state.tableTab}:${state.tableFilter}`] || [];
            return rows.filter((row) =>
                [row.code, row.title, row.owner, row.status]
                    .join(" ")
                    .toLowerCase()
                    .includes(normalize(state.search))
            );
        };

        const updateFilterTabLabels = () => {
            const pendingBtn = root.querySelector('#taskFilterTabs button[data-filter="pending"]');
            const closedBtn = root.querySelector('#taskFilterTabs button[data-filter="closed"]');
            const isRequests = state.tableTab === "requests";
            const pendingLabel = isRequests
                ? _t("Requests in progress")
                : _t("Pending tasks");
            const closedLabel = isRequests ? _t("Finished requests") : _t("Closed tasks");
            const pendingLabelEl = pendingBtn?.querySelector(".subtab-btn__label");
            const closedLabelEl = closedBtn?.querySelector(".subtab-btn__label");
            if (pendingLabelEl) {
                pendingLabelEl.textContent = pendingLabel;
            }
            if (closedLabelEl) {
                closedLabelEl.textContent = closedLabel;
            }
        };

        const updateTaskBadges = () => {
            const tasksTabBadge = root.querySelector('#taskTabs button[data-tab="tasks"] .custom-badge-count');
            const requestsTabBadge = root.querySelector('#taskTabs button[data-tab="requests"] .custom-badge-count');
            const pendingBadge = root.querySelector('#taskFilterTabs button[data-filter="pending"] .subtab-badge-count');
            const closedBadge = root.querySelector('#taskFilterTabs button[data-filter="closed"] .subtab-badge-count');
            const isRequests = state.tableTab === "requests";
            if (tasksTabBadge) {
                tasksTabBadge.textContent = String(pendingActivityRows.length);
            }
            if (requestsTabBadge) {
                requestsTabBadge.textContent = String(pendingRequestRows.length);
            }
            if (pendingBadge) {
                pendingBadge.textContent = String(
                    isRequests ? pendingRequestRows.length : pendingActivityRows.length
                );
            }
            if (closedBadge) {
                closedBadge.textContent = String(
                    isRequests ? approvedRequestRows.length : closedTaskRows.length
                );
            }
        };

        const renderTable = () => {
            const hideTaskStatus =
                state.tableTab === "tasks" && state.tableFilter === "closed";
            const tasksTable = root.querySelector(".tasks-table");
            if (tasksTable) {
                tasksTable.classList.toggle("tasks-table--hide-status", hideTaskStatus);
            }
            const colSpan = hideTaskStatus ? 4 : 5;
            if (!tableLoadedFromApi) {
                pageLabel.textContent = "";
                rowActions.clear();
                taskBody.innerHTML = `<tr><td colspan="${colSpan}"><div class="empty-state">${escapeHtml(
                    _t("Loading...")
                )}</div></td></tr>`;
                return;
            }
            const rows = getTableRows();
            const totalPages = Math.max(1, Math.ceil(rows.length / state.pageSize));
            if (state.page > totalPages) {
                state.page = totalPages;
            }
            const currentRows = rows.slice((state.page - 1) * state.pageSize, state.page * state.pageSize);
            pageLabel.textContent = formatPageLabel(state.page, totalPages);
            rowActions.clear();
            taskBody.innerHTML = currentRows.length
                ? currentRows
                      .map((row) => {
                          const key = rowKey(row);
                          if (row.action) {
                              rowActions.set(key, row.action);
                          }
                          const requestLinkLabel = _t("Request link %s", row.code);
                          const showApprove =
                              state.tableTab === "tasks" &&
                              state.tableFilter === "pending" &&
                              row.can_approve &&
                              row.id;
                          const approveDisabled =
                              approvingActivityId !== null &&
                              String(approvingActivityId) === String(row.id);
                          const approveBtn = ''
                          // const approveBtn = showApprove
                          //     ? `<button class="row-approve" type="button" data-approve-activity="${escapeHtml(
                          //           String(row.id)
                          //       )}"${approveDisabled ? " disabled" : ""}>${escapeHtml(
                          //           _t("Approve")
                          //       )}</button>`
                          //     : state.tableTab === "tasks" && state.tableFilter === "pending"
                          //     ? `<span class="row-approve-spacer" aria-hidden="true"></span>`
                          //     : "";
                          const statusCell = hideTaskStatus
                              ? ""
                              : `<td class="tasks-table__col-status"><span class="status-pill ${
                                    row.statusKey
                                }">${escapeHtml(row.status)}</span></td>`;
                          return `<tr><td class="table-code">${escapeHtml(truncateText(row.code, 24))}</td><td>${escapeHtml(truncateText(row.title, 48))}</td>${statusCell}<td>${escapeHtml(formatOwnerName(row.owner))}</td><td class="table-actions"><div class="table-actions-inner"><button class="row-link" type="button" data-row-code="${escapeHtml(key)}" data-action-label="${escapeHtml(requestLinkLabel)}">${escapeHtml(_t("Request link"))} ${ARROW_SM}</button>${approveBtn}</div></td></tr>`;
                      })
                      .join("")
                : `<tr><td colspan="${colSpan}"><div class="empty-state">${escapeHtml(
                      _t("No items match the current view.")
                  )}</div></td></tr>`;
            updateTaskBadges();
        };

        const matchesSearch = (...parts) => {
            const query = normalize(state.search);
            if (!query) {
                return true;
            }
            return normalize(parts.filter(Boolean).join(" ")).includes(query);
        };

        const renderDecisions = () => {
            /* Server already filtered when searching all records; list is ready to render. */
            const items = decisions;
            if (!items.length) {
                const emptyMsg = normalize(state.search)
                    ? _t("No decisions match your search.")
                    : _t("No decisions right now.");
                decisionsList.innerHTML = `<div class="empty-state">${escapeHtml(emptyMsg)}</div>`;
                return;
            }
            decisionsList.innerHTML = items
                .map((item, index) => {
                    const title = item.title || item;
                    const url = item.url ? `data-url="${item.url}"` : "";
                    return `<li class="decision-item" data-action-label="${escapeHtml(title)}" ${url}><div class="decision-number">${index + 1}</div><p>${escapeHtml(title)}</p>${ARROW_SM}</li>`;
                })
                .join("");
        };

        const renderEvents = () => {
            const items = events;
            if (!items.length) {
                const emptyMsg = normalize(state.search)
                    ? _t("No events match your search.")
                    : _t("No upcoming events right now.");
                timelineList.innerHTML = `<div class="empty-state">${escapeHtml(emptyMsg)}</div>`;
                return;
            }
            timelineList.innerHTML = items
                .map((event) => {
                    const title = localizedLabel(event.title);
                    const meta = localizedLabel(event.meta || "");
                    const month = localizedLabel(event.month);
                    const status = resolveEventStatus(event);
                    const statusLabel = eventStatusLabel(status);
                    const eventColor = escapeHtml(event.color || "#286fd4");
                    const metaHtml = meta
                        ? `<p class="timeline-copy__meta">${escapeHtml(meta)}</p>`
                        : "";
                    return `<button class="timeline-item" type="button" data-action-label="${escapeHtml(title)}" data-url="${event.url || ""}"><div class="date-badge" style="background:${eventColor}"><strong>${event.day}</strong><span>${escapeHtml(month)}</span></div><div class="timeline-copy"><h4 class="timeline-copy__title">${escapeHtml(title)}</h4>${metaHtml}</div><span class="timeline-tag" style="background:${eventColor}">${escapeHtml(statusLabel)}</span>${ARROW_SM}</button>`;
                })
                .join("");
        };

        const restoreDefaultPortalLists = () => {
            newsContent = {
                general: [...defaultNewsContent.general],
                press: [...defaultNewsContent.press],
                employees: [...defaultNewsContent.employees],
            };
            decisions = [...defaultDecisions];
            events = [...defaultEvents];
            renderNews();
            renderDecisions();
            renderEvents();
        };

        const filterNewsPreview = (items) =>
            (items || []).filter((item) =>
                matchesSearch(item.title, item.subtitle || "")
            );

        const searchPortalSections = async (query) => {
            const seq = ++portalSearchSeq;
            try {
                const data = await jsonrpc("/eds_smart_theme/smart_dashboard/search", {
                    search: query,
                    limit: 50,
                });
                if (seq !== portalSearchSeq || normalize(state.search) !== normalize(query)) {
                    return;
                }
                const news = data?.news || {};
                newsContent = {
                    general: Array.isArray(news.general) ? news.general : [],
                    press: Array.isArray(news.press) ? news.press : [],
                    employees: Array.isArray(news.employees) ? news.employees : [],
                };
                decisions = Array.isArray(data?.decisions) ? data.decisions : [];
                events = Array.isArray(data?.events) ? data.events : [];
                renderNews();
                renderDecisions();
                renderEvents();
            } catch {
                if (seq !== portalSearchSeq) {
                    return;
                }
                /* Fall back to filtering the preview lists if the search RPC fails. */
                newsContent = {
                    general: filterNewsPreview(defaultNewsContent.general),
                    press: filterNewsPreview(defaultNewsContent.press),
                    employees: filterNewsPreview(defaultNewsContent.employees),
                };
                decisions = defaultDecisions.filter((item) => {
                    const title = typeof item === "string" ? item : item.title || "";
                    const subtitle = typeof item === "object" ? item.subtitle || "" : "";
                    return matchesSearch(title, subtitle);
                });
                events = defaultEvents.filter((event) =>
                    matchesSearch(
                        localizedLabel(event.title),
                        localizedLabel(event.meta || ""),
                        localizedLabel(event.month),
                        event.day
                    )
                );
                renderNews();
                renderDecisions();
                renderEvents();
            }
        };

        const renderNews = () => {
            /* Server already filtered when searching all records; list is ready to render. */
            const items = newsContent[state.newsTab] || [];
            if (!items.length) {
                const emptyMsg = normalize(state.search)
                    ? _t("No news match your search.")
                    : newsLoadedFromApi
                    ? _t("No published news in this section right now.")
                    : _t("No news match your search.");
                newsList.innerHTML = `<div class="empty-state">${escapeHtml(emptyMsg)}</div>`;
                const emptyFeaturedLabel = _t("No featured item right now.");
                featuredNews.innerHTML = `<div class="featured-news__empty"><img src="${PLACEHOLDER_FEATURED_NEWS}" alt="${escapeHtml(emptyFeaturedLabel)}" onerror="this.onerror=null;this.src='${PLACEHOLDER_AVATAR}'"/><div class="featured-news__body"><p class="featured-news__empty-msg">${escapeHtml(emptyFeaturedLabel)}</p></div></div>`;
                return;
            }
            if (!items.some((item) => String(item.id) === String(state.featuredNewsId))) {
                state.featuredNewsId = items[0].id;
            }
            newsList.innerHTML = items
                .slice()
                .reverse()
                .map((item) => {
                    const isActive = String(item.id) === String(state.featuredNewsId);
                    const title = escapeHtml(item.title);
                    const url = escapeHtml(item.url || "");
                    return `<button class="news-item ${isActive ? "active" : ""}" type="button" data-id="${item.id}" data-news-select="1"><span class="news-dot" aria-hidden="true"></span><p>${title}</p><span class="news-item__open" role="button" tabindex="0" data-news-url="${url}" aria-label="${escapeHtml(_t("Open"))}">${ARROW_SM}</span></button>`;
                })
                .join("");
            const featuredItem =
                items.find((item) => String(item.id) === String(state.featuredNewsId)) || items[0];
            const featuredImage = featuredItem.image_url || featuredItem.image || "/web/static/img/placeholder.png";
            const featuredTitle = escapeHtml(featuredItem.title);
            const featuredUrl = escapeHtml(featuredItem.url || "");
            featuredNews.innerHTML = `<button type="button" class="featured-news__link" data-news-url="${featuredUrl}" ${featuredUrl ? "" : "disabled"}><img src="${featuredImage}" alt="${featuredTitle}"/><div class="featured-news__body"><h4>${featuredTitle}</h4><time>${escapeHtml(featuredItem.date || "")}</time></div></button>`;
        };

        const renderQuickLinks = () => {
            if (!quickLinks.length) {
                return;
            }
            quickLinksRoot.innerHTML = quickLinks
                .map((link) => {
                    const iconHtml = link.iconClass
                        ? `<i class="fa ${link.iconClass}"></i>`
                        : `<span>${link.iconText || "🔗"}</span>`;
                    return `<a class="quick-link ${state.quickLink === link.label ? "active" : ""}" href="${link.href || "#"}" data-label="${link.label}" data-action-label="${link.label}" target="${link.target || ""}" rel="${link.target ? "noopener noreferrer" : ""}"><span class="quick-icon" style="background:${link.color}; color:${link.text}">${iconHtml}</span><span>${link.label}</span></a>`;
                })
                .join("");
        };

        const applyBootstrap = (data) => {
            if (!data) {
                return;
            }
            this.employeeProfileAction = data.profile_action || null;
            if (data.profile) {
                renderWelcome(data.profile, data.leave_kpis || [], data.pending_requests_count || 0);
            } else {
                renderKpis(Array.isArray(data.leave_kpis) ? data.leave_kpis : []);
            }
            if (data.news) {
                newsLoadedFromApi = true;
                newsContent = {
                    general: Array.isArray(data.news.general) ? data.news.general : [],
                    press: Array.isArray(data.news.press) ? data.news.press : [],
                    employees: Array.isArray(data.news.employees) ? data.news.employees : [],
                };
                defaultNewsContent = {
                    general: [...newsContent.general],
                    press: [...newsContent.press],
                    employees: [...newsContent.employees],
                };
            }
            if (data.decisions?.length) {
                decisions = data.decisions;
                defaultDecisions = [...data.decisions];
            }
            if (data.events?.length) {
                events = data.events;
                defaultEvents = [...data.events];
            }
            if (data.task_lists) {
                pendingActivityRows = sortRowsNewestFirst(
                    Array.isArray(data.task_lists.pending) ? data.task_lists.pending : []
                );
                closedTaskRows = sortRowsNewestFirst(
                    Array.isArray(data.task_lists.closed) ? data.task_lists.closed : []
                );
                tableLoadedFromApi = true;
            }
            if (data.request_lists) {
                pendingRequestRows = sortRowsNewestFirst(
                    Array.isArray(data.request_lists.pending)
                        ? data.request_lists.pending
                        : []
                );
                approvedRequestRows = sortRowsNewestFirst(
                    Array.isArray(data.request_lists.closed)
                        ? data.request_lists.closed
                        : []
                );
                tableLoadedFromApi = true;
            }
            if (data.new_joiners?.length) {
                newJoiners = data.new_joiners;
                joinerIndex = 0;
                renderEmployeeCarousel();
            }
            if (data.attendance) {
                renderAttendance(data.attendance);
            }
            if (Array.isArray(data.quick_links) && data.quick_links.length) {
                quickLinks = data.quick_links.map((link, index) =>
                    mapPortalLinkItem(link, index)
                );
                if (!quickLinks.some((link) => link.label === state.quickLink)) {
                    state.quickLink = quickLinks[0]?.label || "";
                }
            }
            if (Array.isArray(data.service_categories) && data.service_categories.length) {
                serviceCategories = data.service_categories.map((category) => ({
                    id: category.id,
                    key: category.key,
                    label: category.label,
                    items: (category.items || []).map((item) => mapPortalServiceItem(item)),
                }));
                if (!serviceCategories.some((cat) => cat.key === state.serviceGroup)) {
                    state.serviceGroup = serviceCategories[0].key;
                }
            }
            const firstTab = newsContent[state.newsTab];
            state.featuredNewsId = firstTab?.[0]?.id ?? null;
        };

        root.querySelector("#serviceTabs").addEventListener("click", (event) => {
            const button = event.target.closest("button[data-group]");
            if (!button) {
                return;
            }
            state.serviceGroup = button.dataset.group;
            setActiveButton(root.querySelector("#serviceTabs"), "button[data-group]", state.serviceGroup, "data-group");
            renderServices();
        });
        serviceGrid.addEventListener("click", (event) => {
            const card = event.target.closest("[data-service-id]");
            if (!card) {
                return;
            }
            const action = serviceItemActions.get(card.dataset.serviceId);
            if (!action?.type) {
                return;
            }
            event.preventDefault();
            this.actionService.doAction(action);
        });
        root.querySelector("#taskTabs").addEventListener("click", (event) => {
            const button = event.target.closest("button[data-tab]");
            if (!button) {
                return;
            }
            state.tableTab = button.dataset.tab;
            state.page = 1;
            setActiveButton(root.querySelector("#taskTabs"), "button[data-tab]", state.tableTab, "data-tab");
            updateFilterTabLabels();
            renderTable();
        });
        root.querySelector("#taskFilterTabs").addEventListener("click", (event) => {
            const button = event.target.closest("button[data-filter]");
            if (!button) {
                return;
            }
            state.tableFilter = button.dataset.filter;
            state.page = 1;
            setActiveButton(root.querySelector("#taskFilterTabs"), "button[data-filter]", state.tableFilter, "data-filter");
            renderTable();
        });
        taskBody.addEventListener("click", async (event) => {
            const approveBtn = event.target.closest("button[data-approve-activity]");
            if (approveBtn) {
                if (approveBtn.disabled || approvingActivityId !== null) {
                    return;
                }
                const activityId = Number(approveBtn.dataset.approveActivity);
                if (!activityId) {
                    return;
                }
                approvingActivityId = activityId;
                approveBtn.disabled = true;
                try {
                    const response = await jsonrpc(
                        "/eds_smart_theme/smart_dashboard/approve_activity",
                        { activity_id: activityId }
                    );
                    if (response?.action?.type) {
                        this.actionService.doAction(response.action);
                        return;
                    }
                    if (response?.success) {
                        pendingActivityRows = pendingActivityRows.filter(
                            (row) => String(row.id) !== String(activityId)
                        );
                        showToast(response.message || _t("Request approved successfully."));
                        renderTable();
                        return;
                    }
                    showToast(
                        response?.message || _t("Could not approve this request.")
                    );
                } catch {
                    showToast(_t("Could not approve this request."));
                } finally {
                    approvingActivityId = null;
                    renderTable();
                }
                return;
            }
            const link = event.target.closest("button[data-row-code]");
            if (!link) {
                return;
            }
            const action = rowActions.get(link.dataset.rowCode);
            if (action) {
                this.actionService.doAction(action);
            } else {
                showToast(_t("Opened %s", link.dataset.actionLabel));
            }
        });
        root.querySelector("#nextPage").addEventListener("click", () => {
            const totalPages = Math.max(1, Math.ceil(getTableRows().length / state.pageSize));
            state.page = state.page === totalPages ? 1 : state.page + 1;
            renderTable();
        });
        root.querySelector("#prevPage").addEventListener("click", () => {
            const totalPages = Math.max(1, Math.ceil(getTableRows().length / state.pageSize));
            state.page = state.page === 1 ? totalPages : state.page - 1;
            renderTable();
        });
        root.querySelector("#newsTabs")?.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-news]");
            if (!button) {
                return;
            }
            state.newsTab = button.dataset.news;
            const tabItems = newsContent[state.newsTab];
            state.featuredNewsId = tabItems?.[0]?.id ?? null;
            setActiveButton(root.querySelector("#newsTabs"), "button[data-news]", state.newsTab, "data-news");
            renderNews();
        });
        newsList.addEventListener("click", (event) => {
            const openBtn = event.target.closest("[data-news-url]");
            if (openBtn) {
                event.stopPropagation();
                openNewsUrl(openBtn.dataset.newsUrl);
                return;
            }
            const item = event.target.closest(".news-item[data-news-select]");
            if (!item) {
                return;
            }
            event.stopPropagation();
            const parsed = Number(item.dataset.id);
            state.featuredNewsId = Number.isNaN(parsed) ? item.dataset.id : parsed;
            renderNews();
        });
        featuredNews.addEventListener("click", (event) => {
            const link = event.target.closest("[data-news-url]");
            if (!link) {
                return;
            }
            openNewsUrl(link.dataset.newsUrl);
        });
        quickLinksRoot.addEventListener("click", (event) => {
            const item = event.target.closest(".quick-link");
            if (!item) {
                return;
            }
            state.quickLink = item.dataset.label;
            renderQuickLinks();
        });
        const joinerPrev = root.querySelector("#joinerPrev");
        const joinerNext = root.querySelector("#joinerNext");
        if (joinerPrev) {
            joinerPrev.addEventListener("click", () => {
                if (!newJoiners.length) {
                    return;
                }
                joinerIndex = (joinerIndex - 1 + newJoiners.length) % newJoiners.length;
                renderEmployeeCarousel();
            });
        }
        if (joinerNext) {
            joinerNext.addEventListener("click", () => {
                if (!newJoiners.length) {
                    return;
                }
                joinerIndex = (joinerIndex + 1) % newJoiners.length;
                renderEmployeeCarousel();
            });
        }
        root.querySelectorAll(".icon-button").forEach((button) => {
            button.addEventListener("click", () => {
                root.querySelectorAll(".icon-button").forEach((item) => item.classList.remove("is-active"));
                button.classList.add("is-active");
            });
        });
        if (searchInput) {
            searchInput.addEventListener("input", (event) => {
                state.search = event.target.value;
                state.page = 1;
                renderServices();
                renderTable();
                window.clearTimeout(portalSearchTimer);
                const query = (state.search || "").trim();
                if (!query) {
                    portalSearchSeq += 1;
                    restoreDefaultPortalLists();
                    return;
                }
                portalSearchTimer = window.setTimeout(() => {
                    searchPortalSections(query);
                }, 250);
            });
            document.dispatchEvent(
                new CustomEvent("smart-portal-dashboard-search-bound", { bubbles: true })
            );
        }
        const attendanceGrid = root.querySelector("#attendanceGrid");
        if (attendanceGrid) {
            attendanceGrid.addEventListener("click", (event) => {
                const card = event.target.closest("button[data-attendance-key]");
                if (!card) {
                    return;
                }
                const action = attendanceCardActions.get(card.dataset.attendanceKey);
                if (action?.type) {
                    this.actionService.doAction(action);
                } else {
                    showToast(_t("Cannot open the request form right now."));
                }
            });
        }
        root.addEventListener("click", (event) => {
            if (event.target.closest("button[data-attendance-key]")) {
                return;
            }
            const rowLink = event.target.closest("button[data-row-code]");
            if (rowLink) {
                return;
            }
            if (event.target.closest("button[data-approve-activity]")) {
                return;
            }
            const viewAllBtn = event.target.closest("button.section-view-all[data-view-all]");
            if (viewAllBtn) {
                const kind = viewAllBtn.dataset.viewAll;
                let url = null;
                if (kind === "news") {
                    url = VIEW_ALL_URLS.news[state.newsTab] || VIEW_ALL_URLS.news.general;
                } else if (kind === "decisions") {
                    url = VIEW_ALL_URLS.decisions;
                } else if (kind === "events") {
                    url = VIEW_ALL_URLS.events;
                }
                if (url) {
                    window.open(url, "_blank", "noopener,noreferrer");
                } else {
                    showToast(_t("Cannot open this page right now."));
                }
                return;
            }
            const actionable = event.target.closest("[data-action-label]");
            if (!actionable) {
                return;
            }
            const url = actionable.dataset.url;
            if (url && url !== "#" && !url.startsWith("javascript")) {
                window.open(url, "_blank");
                return;
            }
            showToast(_t("Opened %s", actionable.dataset.actionLabel));
        });

        renderServiceTabs();
        renderServices();
        renderTable();
        renderDecisions();
        renderEvents();
        renderAttendance(null);
        renderKpis([], { loading: true });

        try {
            const data = await jsonrpc("/eds_smart_theme/smart_dashboard/bootstrap", {});
            applyBootstrap(data);
            const firstTab = newsContent[state.newsTab];
            state.featuredNewsId = firstTab?.[0]?.id ?? null;
        } catch {
            renderKpis([]);
            if (!newsLoadedFromApi) {
                newsContent = { ...getMockNews() };
                state.featuredNewsId = newsContent.general[0]?.id ?? null;
            }
            if (!tableLoadedFromApi) {
                pendingActivityRows = getMockPendingActivityRows();
                closedTaskRows = getMockClosedTaskRows();
                pendingRequestRows = getMockPendingRequestRows();
                approvedRequestRows = getMockApprovedRequestRows();
                tableLoadedFromApi = true;
            }
        }

        updateFilterTabLabels();
        renderTable();
        renderDecisions();
        renderEvents();
        renderNews();
        renderQuickLinks();
        renderServiceTabs();
        renderServices();
        notifyUiDirection(getUiDirection());
    }
}

registry.category("actions").add("eds_smart_theme_smart_dashboard", SmartPortalDashboard);
