/** @odoo-module **/
/* ═══════════════════════════════════════════════════════════════════
   hr_employee_dashboard.js  —  بوابة الموظف الحكومية
   Odoo 19 OWL — eds_smart_theme — Full dynamic data from Odoo models
   ═══════════════════════════════════════════════════════════════════ */
import { registry }   from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";
import { session } from "@web/session";

export class HrEmployeeDashboard extends Component {
    static template = "eds_smart_theme.HrDashboard";
    static props = ["*"];

    setup() {
        this.orm    = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            activeTab:   "tasks",
            taskFilter:  "active",
            deptFilter:  "hr",
            currentPage: 1,
            totalPages:  1,
            todayDate:   this._fmtDate(new Date()),

            employee: null,   // hr.employee id (resolved after load)

            user: {
                name:            session.name || "الموظف",
                jobTitle:        "—",
                department:      "—",
                code:            "—",
                leaveBalance:    0,
                pendingRequests: 0,
                hireDate:        "—",
                grade:           "—",
                lastReview:      "—",
                yearsOfService:  0,
                avatarUrl:       session.uid
                    ? `/web/image/res.users/${session.uid}/avatar_128`
                    : null,
            },

            announcements: [],
            news:          [],
            featuredNews:  { name: "—", date: "—" },
            events:        [],
            requestStatus: [],
            tasks:         [],
            taskCount:     0,

            servicesHr:  [
                { id:1,  name:"التبليغ عن مشكلة أو نسيان استخدام نظام البصمة" },
                { id:2,  name:"طلب إجازة" },
                { id:3,  name:"نموذج طلب الاعتذار/الانسحاب النهائي من الدراسة" },
                { id:4,  name:"نموذج طلب التعويض عن الرسوم الدراسية" },
                { id:5,  name:"نموذج طلب تحديث السجل الأكاديمي" },
                { id:6,  name:"نموذج طلب الالتحاق بالدراسة" },
                { id:7,  name:"تقييم الأداء للفترة التجريبية" },
                { id:8,  name:"نموذج تحويل وتثبيت الراتب" },
                { id:9,  name:"ملاحظات التأمين الطبي" },
                { id:10, name:"نموذج طلب صرف بدل اتصال" },
                { id:11, name:"طلب بطاقة عمل" },
                { id:12, name:"نظام الاستفسارات والدعم لخدمات الموارد البشرية" },
                { id:13, name:"طلب تحديث بيانات شخصية" },
                { id:14, name:"منح بدل التعليم" },
                { id:15, name:"العمل عن بعد" },
                { id:16, name:"رحلة عمل" },
                { id:17, name:"تدريب" },
                { id:18, name:"نموذج خطاب تعريف" },
            ],
            servicesFin: [
                { id:101, name:"طلب صرف مكافأة" },
                { id:102, name:"طلب سلفة راتب" },
                { id:103, name:"مطالبة مصاريف سفر" },
                { id:104, name:"طلب تسوية عهدة مالية" },
                { id:105, name:"نموذج طلب شراء" },
                { id:106, name:"طلب دفع فاتورة خارجية" },
                { id:107, name:"نموذج اعتماد ميزانية" },
                { id:108, name:"كشف حساب الموظف" },
                { id:109, name:"تقرير حضانة الأصول" },
                { id:110, name:"طلب تدقيق مالي داخلي" },
                { id:111, name:"إجراءات الجرد السنوي" },
                { id:112, name:"طلب شطب أصل" },
            ],

            kpiBoxes: [],
            attendance: { present: 0, late: 0, remote: 0, absent: 0 },

            quickLinks: [
                { label:"الموارد البشرية",          icon:"fa-users",            iconClass:"teal",  action:"hr.open_view_employee_list_my" },
                { label:"طلبات الإجازة",             icon:"fa-calendar",         iconClass:"green", action:"hr_holidays.action_hr_leave_allocation" },
                { label:"المهام والمشاريع",           icon:"fa-tasks",            iconClass:"teal",  action:"project.action_view_all_task" },
                { label:"سجل الحضور",                icon:"fa-clock-o",          iconClass:"green", action:"hr_attendance.hr_attendance_action" },
                { label:"لوحة تحكم الإجازات",        icon:"fa-umbrella",         iconClass:"teal",  action:"hr_holidays.action_hr_leave" },
                { label:"الرواتب والمستحقات",        icon:"fa-money",            iconClass:"green", action:null },
                { label:"النماذج والقوالب",           icon:"fa-file-text-o",      iconClass:"teal",  action:null },
                { label:"حجز قاعة الاجتماعات",       icon:"fa-calendar-check-o", iconClass:"green", action:null },
            ],
        });

        onMounted(() => this._loadData());
    }

    // ═══════════════════════════════════════════════════════════════
    //  ORCHESTRATOR
    // ═══════════════════════════════════════════════════════════════
    async _loadData() {
        this.state.loading = true;
        try {
            // Step 1: resolve employee record (needed by most other loaders)
            await this._loadEmployee();

            // Step 2: all other loaders in parallel
            await Promise.allSettled([
                this._loadLeaveData(),
                this._loadTasks(),
                this._loadAttendance(),
                this._loadActivities(),
                this._loadAnnouncements(),
            ]);

            // Step 3: build KPI boxes from already-loaded state
            this._buildKpi();
        } catch (e) {
            console.warn("HrDashboard _loadData:", e);
        } finally {
            this.state.loading = false;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    //  1. EMPLOYEE  (hr.employee linked to the current user)
    // ═══════════════════════════════════════════════════════════════
    async _loadEmployee() {
        const uid = session.uid;
        if (!uid) return;

        const fields = ["name", "job_title", "department_id", "barcode",
                        "contract_date_start", "user_id"];
        let emps = [];
        try {
            emps = await this.orm.searchRead(
                "hr.employee",
                [["user_id", "=", uid], ["active", "=", true]],
                fields,
                { limit: 1 }
            );
        } catch (_) {
            // hr module might not be installed
            return;
        }

        if (!emps.length) return;
        const emp = emps[0];
        this.state.employee = emp.id;

        this.state.user.name       = emp.name || this.state.user.name;
        this.state.user.jobTitle   = emp.job_title || "—";
        this.state.user.department = emp.department_id ? emp.department_id[1] : "—";
        this.state.user.code       = emp.barcode || String(emp.id);
        this.state.user.avatarUrl  = `/web/image/hr.employee/${emp.id}/avatar_128`;

        if (emp.contract_date_start) {
            const d = new Date(emp.contract_date_start);
            this.state.user.hireDate = `${String(d.getDate()).padStart(2,"0")}/${String(d.getMonth()+1).padStart(2,"0")}/${d.getFullYear()}`;
            const diffYears = Math.floor((Date.now() - d.getTime()) / (365.25 * 24 * 3600 * 1000));
            this.state.user.yearsOfService = diffYears;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    //  2. LEAVE DATA  (balance + pending count + request status)
    // ═══════════════════════════════════════════════════════════════
    async _loadLeaveData() {
        const uid = session.uid;
        if (!uid) return;

        // ── 2a. Leave balance from hr.leave.type ──
        try {
            const leaveTypes = await this.orm.searchRead(
                "hr.leave.type",
                [["requires_allocation", "=", true]],
                ["name", "virtual_remaining_leaves"],
                { limit: 10 }
            );
            // Sum up all remaining leaves across types
            const totalRemaining = leaveTypes.reduce(
                (sum, t) => sum + (t.virtual_remaining_leaves || 0), 0
            );
            this.state.user.leaveBalance = Math.max(0, Math.round(totalRemaining));
        } catch (_) {}

        // ── 2b. Pending requests count (hr.leave in 'confirm') ──
        try {
            const domain = [["user_id", "=", uid], ["state", "=", "confirm"]];
            const pendingCount = await this.orm.searchCount("hr.leave", domain);
            this.state.user.pendingRequests = pendingCount;
        } catch (_) {}

        // ── 2c. Request status: last 5 leave requests ──
        try {
            const leaves = await this.orm.searchRead(
                "hr.leave",
                [["user_id", "=", uid]],
                ["name", "state", "holiday_status_id", "date_from", "create_date"],
                { limit: 5, order: "create_date desc" }
            );

            const STATE_MAP = {
                confirm:  { label: "قيد المراجعة", badge: "orange", border: "ob" },
                validate1:{ label: "موافقة جزئية", badge: "teal",   border: "tb" },
                validate: { label: "مكتمل",         badge: "teal",   border: "tb" },
                refuse:   { label: "مرفوض",          badge: "red",    border: "rb" },
                draft:    { label: "مسودة",           badge: "gray",   border: "gb" },
            };

            this.state.requestStatus = leaves.map((l, i) => {
                const st = STATE_MAP[l.state] || { label: l.state, badge: "gray", border: "gb" };
                const ago = l.create_date ? this._timeAgo(new Date(l.create_date)) : "";
                return {
                    id:          l.id,
                    name:        l.holiday_status_id ? l.holiday_status_id[1] : (l.name || "طلب إجازة"),
                    ago,
                    statusLabel: st.label,
                    badgeClass:  st.badge,
                    borderClass: st.border,
                };
            });
        } catch (_) {}
    }

    // ═══════════════════════════════════════════════════════════════
    //  3. TASKS  (project.task assigned to current user)
    // ═══════════════════════════════════════════════════════════════
    async _loadTasks() {
        const uid = session.uid;
        if (!uid) return;
        try {
            const tasks = await this.orm.searchRead(
                "project.task",
                [["user_ids", "in", [uid]], ["project_id", "!=", false]],
                ["name", "state", "stage_id", "project_id", "sequence"],
                { limit: 50, order: "sequence asc, create_date desc" }
            );

            const STATE_LABEL = {
                "01_in_progress": { label: "تحت التنفيذ", cls: "blue",   state: "active" },
                "1_done":         { label: "منتهية",       cls: "teal",   state: "done"   },
                "1_canceled":     { label: "ملغاة",        cls: "red",    state: "done"   },
                "03_approved":    { label: "معتمدة",       cls: "teal",   state: "done"   },
                "04_waiting_normal":{ label: "معلقة",      cls: "orange", state: "locked" },
            };

            this.state.tasks = tasks.map((t, i) => {
                const stInfo = STATE_LABEL[t.state] || { label: t.stage_id?.[1] || "جارية", cls: "blue", state: "active" };
                const proj   = t.project_id ? t.project_id[1] : "—";
                const prefix = proj.includes("مال") || proj.toLowerCase().includes("fin") ? "FIN" : "HR";
                return {
                    id:          t.id,
                    ref:         `${prefix}-${new Date().getFullYear()}-${String(t.id).padStart(4, "0")}`,
                    name:        t.name,
                    submitter:   proj,
                    state:       stInfo.state,
                    statusLabel: stInfo.label,
                    statusClass: stInfo.cls,
                };
            });

            this.state.taskCount = tasks.filter(t => {
                const s = STATE_LABEL[t.state];
                return !s || s.state === "active";
            }).length;

            this.state.totalPages  = Math.max(1, Math.ceil(this.state.tasks.length / 10));
            this.state.currentPage = 1;
        } catch (_) {}
    }

    // ═══════════════════════════════════════════════════════════════
    //  4. ATTENDANCE  (hr.attendance — current month)
    // ═══════════════════════════════════════════════════════════════
    async _loadAttendance() {
        const empId = this.state.employee;
        if (!empId) return;
        try {
            const now   = new Date();
            const start = new Date(now.getFullYear(), now.getMonth(), 1);
            const startStr = start.toISOString().slice(0, 10);
            const endStr   = now.toISOString().slice(0, 10);

            const records = await this.orm.searchRead(
                "hr.attendance",
                [
                    ["employee_id", "=", empId],
                    ["date", ">=", startStr],
                    ["date", "<=", endStr],
                ],
                ["date", "check_in", "check_out", "worked_hours"],
                { limit: 100 }
            );

            // Distinct present days
            const presentDays = new Set(records.map(r => r.date)).size;

            // Late: check_in after 09:00 (local time) — adjust threshold as needed
            const lateDays = records.filter(r => {
                if (!r.check_in) return false;
                const d = new Date(r.check_in);
                return d.getHours() > 9 || (d.getHours() === 9 && d.getMinutes() > 0);
            }).length;

            this.state.attendance = {
                present: presentDays,
                late:    lateDays,
                remote:  0,
                absent:  Math.max(0, this._workingDaysThisMonth() - presentDays),
            };
        } catch (_) {}
    }

    // ═══════════════════════════════════════════════════════════════
    //  5. ACTIVITIES  (mail.activity — upcoming, as events)
    // ═══════════════════════════════════════════════════════════════
    async _loadActivities() {
        const uid = session.uid;
        if (!uid) return;
        try {
            const today    = new Date().toISOString().slice(0, 10);
            const inTwoWeeks = new Date(Date.now() + 14 * 86400000).toISOString().slice(0, 10);

            const acts = await this.orm.searchRead(
                "mail.activity",
                [
                    ["user_id", "=", uid],
                    ["date_deadline", ">=", today],
                    ["date_deadline", "<=", inTwoWeeks],
                ],
                ["summary", "note", "date_deadline", "activity_type_id", "res_model"],
                { limit: 5, order: "date_deadline asc" }
            );

            const AR_MONTHS = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                               "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"];
            const COLORS = ["purple", "teal", "orange", "blue", "green"];

            this.state.events = acts.map((a, i) => {
                const d = new Date(a.date_deadline);
                const isPast = d < new Date();
                return {
                    id:          a.id,
                    day:         String(d.getDate()).padStart(2, "0"),
                    month:       AR_MONTHS[d.getMonth()],
                    color:       COLORS[i % COLORS.length],
                    name:        a.summary || a.activity_type_id?.[1] || "نشاط",
                    subtitle:    a.res_model || "",
                    statusLabel: isPast ? "منتهي" : "قادم",
                    statusClass: isPast ? "red"   : (i % 2 === 0 ? "orange" : "teal"),
                };
            });
        } catch (_) {}
    }

    // ═══════════════════════════════════════════════════════════════
    //  6. ANNOUNCEMENTS  (mail.message from HR/company channels)
    // ═══════════════════════════════════════════════════════════════
    async _loadAnnouncements() {
        try {
            // Try to read messages from discuss.channel named 'general' or 'HR'
            // or fall back to hr.employee chatter messages (subtype = note/comment)
            const msgs = await this.orm.searchRead(
                "mail.message",
                [
                    ["message_type", "in", ["comment", "email"]],
                    ["res_model", "in", ["hr.employee", "res.company", "discuss.channel"]],
                    ["subtype_id.internal", "=", false],
                ],
                ["subject", "body", "author_id", "date"],
                { limit: 5, order: "date desc" }
            );

            if (msgs.length) {
                this.state.announcements = msgs.map((m, i) => ({
                    id:   m.id,
                    name: m.subject || this._stripHtml(m.body).slice(0, 80) || "تعميم",
                }));

                // Use the most recent one as featured news
                const first = msgs[0];
                this.state.featuredNews = {
                    name: first.subject || this._stripHtml(first.body).slice(0, 100) || "أحدث الأخبار",
                    date: first.date ? this._fmtDate(new Date(first.date)) : "—",
                };

                // Use messages 1-5 as news list
                this.state.news = msgs.map((m, i) => ({
                    id:       m.id,
                    name:     m.subject || this._stripHtml(m.body).slice(0, 70) || "خبر",
                    dotColor: i % 2 === 0 ? "orange" : "teal",
                }));
            }
        } catch (_) {}
    }

    // ═══════════════════════════════════════════════════════════════
    //  7. KPI BOXES  (built from loaded state)
    // ═══════════════════════════════════════════════════════════════
    _buildKpi() {
        this.state.kpiBoxes = [
            {
                label: "رصيد الإجازات",
                value: String(this.state.user.leaveBalance),
                sub:   "يوم متبقي",
                color: "",
                highlight: true,
            },
            {
                label: "الطلبات المعلقة",
                value: String(this.state.user.pendingRequests),
                sub:   "قيد المراجعة",
                color: this.state.user.pendingRequests > 0 ? "orange" : "",
                highlight: false,
            },
            {
                label: "المهام الجارية",
                value: String(this.state.taskCount),
                sub:   "تحت التنفيذ",
                color: "teal",
                highlight: false,
            },
            {
                label: "أيام الحضور",
                value: String(this.state.attendance.present),
                sub:   "هذا الشهر",
                color: "",
                highlight: false,
            },
            {
                label: "الأنشطة القادمة",
                value: String(this.state.events.length),
                sub:   "خلال أسبوعين",
                color: "",
                highlight: false,
            },
        ];
    }

    // ═══════════════════════════════════════════════════════════════
    //  COMPUTED
    // ═══════════════════════════════════════════════════════════════
    get filteredTasks() {
        const f = this.state.taskFilter;
        if (f === "active") return this.state.tasks.filter(t => t.state === "active");
        if (f === "done")   return this.state.tasks.filter(t => t.state === "done");
        if (f === "locked") return this.state.tasks.filter(t => t.state === "locked");
        return this.state.tasks;
    }
    get filteredServices() {
        return this.state.deptFilter === "fin" ? this.state.servicesFin : this.state.servicesHr;
    }
    get emptyMsg() {
        return {
            active: "لا يوجد مهام تحت التنفيذ",
            locked: "لا يوجد مهام مقفلة",
            done:   "لا يوجد مهام منتهية",
        }[this.state.taskFilter] || "لا توجد مهام";
    }

    // ═══════════════════════════════════════════════════════════════
    //  HELPERS
    // ═══════════════════════════════════════════════════════════════
    initials(n) {
        if (!n) return "؟";
        const p = n.trim().split(/\s+/);
        return p.length > 1 ? p[0][0] + p[1][0] : n.substring(0, 2);
    }

    _fmtDate(d) {
        const days   = ["الأحد","الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت"];
        const months = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                        "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"];
        return `${days[d.getDay()]}، ${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
    }

    _timeAgo(date) {
        const diff = Math.floor((Date.now() - date.getTime()) / 1000);
        if (diff < 3600)   return `منذ ${Math.floor(diff / 60)} دقيقة`;
        if (diff < 86400)  return `منذ ${Math.floor(diff / 3600)} ساعة`;
        if (diff < 604800) return `منذ ${Math.floor(diff / 86400)} أيام`;
        return `منذ ${Math.floor(diff / 604800)} أسابيع`;
    }

    _stripHtml(html) {
        if (!html) return "";
        return html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    }

    /** Count Mon–Fri days from start of month until today */
    _workingDaysThisMonth() {
        const now   = new Date();
        const start = new Date(now.getFullYear(), now.getMonth(), 1);
        let count   = 0;
        for (let d = new Date(start); d <= now; d.setDate(d.getDate() + 1)) {
            const day = d.getDay();
            if (day !== 5 && day !== 6) count++; // Skip Fri+Sat (Arabic work week)
        }
        return count;
    }

    // ═══════════════════════════════════════════════════════════════
    //  STATE SETTERS
    // ═══════════════════════════════════════════════════════════════
    setTab(t)    { this.state.activeTab  = t; }
    setFilter(f) { this.state.taskFilter = f; }
    setDept(d)   { this.state.deptFilter = d; }

    // ═══════════════════════════════════════════════════════════════
    //  NAVIGATION
    // ═══════════════════════════════════════════════════════════════
    go(xmlid) {
        if (!xmlid) return;
        this.action.doAction(xmlid).catch(() => {});
    }

    goLeaveRequest() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.leave",
            view_mode: "form",
            views: [[false, "form"]],
            name: "طلب إجازة",
        }).catch(() => {});
    }

    goMyRequests() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.leave",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            name: "طلباتي",
        }).catch(() => {});
    }

    openTask(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "project.task",
            res_id: id,
            view_mode: "form",
            views: [[false, "form"]],
        }).catch(() => {});
    }

    async refresh() {
        await this._loadData();
    }
}

registry.category("actions").add("eds_hr_employee_dashboard", HrEmployeeDashboard);
