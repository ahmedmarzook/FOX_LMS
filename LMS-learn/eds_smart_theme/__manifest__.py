# -*- coding: utf-8 -*-
{
    'name': 'ثيم بوابة الموظف والعقارات',
    'name_en': 'Employee Portal & Property Theme',
    'version': '19.0.2.1.0',
    'category': 'Themes/Backend',
    'summary': 'ثيم احترافي عربي RTL — بوابة الموظف الحكومية + نظام إدارة العقارات',
    'description': """
        Employee Portal + Property Management Theme
        ============================================
        * بوابة الموظف الحكومية (لوحة تحكم جديدة بالكامل):
            - بطاقة الملف الشخصي مع إحصائيات الموظف
            - بانر الترحيب مع التاريخ والطلبات الجديدة
            - التعاميم والقرارات
            - لوحة الأخبار مع بطاقة مميزة
            - الأحداث القادمة والإجراءات السريعة
            - حالة الطلبات
            - لوحة المهام (تحت التنفيذ / المقفلة / المنتهية)
            - الخدمات الذاتية (HR + المالية)
            - معلوماتي (بيانات + أداء + حضور)
            - روابط سريعة
        * ثيم العقارات الأصلي محتفظ به
        * خط Alexandria — ألوان #6D299A و #01B59A — RTL كامل
        * متوافق مع Odoo 19 Community
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'license': 'LGPL-3',

    'depends': [
        'web',
        'mail',
        'portal',
        'base_setup',
        'resource',
        'hr',
        'hr_skills',
        'hr_holidays',
    ],

    'data': [
        # --- security ---
        'security/ir.model.access.csv',
        # --- smart_theme data (noupdate config/migration records) ---
        'data/smart_theme/backend_config_data.xml',
        'data/smart_theme/migrate_default_color.xml',
        'data/smart_theme/global_level_config.xml',
        # --- smart_dashboard data ---
        'data/smart_dashboard/smart_portal_service_category_data.xml',
        'data/smart_dashboard/smart_portal_service_data.xml',
        'data/smart_dashboard/smart_portal_quick_link_data.xml',
        'data/smart_dashboard/dashboard_action.xml',
        # --- smart_theme views ---
        'views/smart_theme/manifest.xml',
        'views/smart_theme/pwa_offline.xml',
        'views/smart_theme/spiffy_app_group_view.xml',
        'views/smart_theme/backend_configurator_view.xml',
        'views/smart_theme/res_users_view.xml',
        'views/smart_theme/ir_module_view.xml',
        'views/smart_theme/pwa_shortcuts_view.xml',
        'views/smart_theme/res_config_setting.xml',
        'views/smart_theme/menuitems.xml',
        'views/smart_theme/global_search_view.xml',
        'views/smart_theme/backend_configurator_template.xml',
        'views/smart_theme/login_page_style.xml',
        'views/smart_theme/templates_inherit.xml',
        'views/smart_theme/to_do_list_template.xml',
        'views/smart_theme/push_notification_menu_view.xml',
        # --- smart_dashboard views ---
        'views/smart_dashboard/res_users_views.xml',
        'views/smart_dashboard/smart_portal_quick_link_views.xml',
        'views/smart_dashboard/smart_portal_service_views.xml',
        # --- existing eds_smart_theme views ---
        'views/property_theme_dashboard_views.xml',
        # 'views/hr_employee_dashboard_views.xml',
    ],

    'demo': [
        'data/smart_theme/spiffy_default_images.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # 1. الخط أولاً
            'eds_smart_theme/static/src/css/01_fonts.css',
            # 2. المتغيرات والـ Base
            'eds_smart_theme/static/src/css/02_variables.css',
            # 3. تطبيق الخط على كامل Odoo
            'eds_smart_theme/static/src/css/03_global_override.css',
            # 4. تنسيق مكونات Odoo
            'eds_smart_theme/static/src/css/04_odoo_components.css',
            # 5. لوحة تحكم العقارات الأصلية
            'eds_smart_theme/static/src/css/05_dashboard.css',
            'eds_smart_theme/static/src/css/06_overlay_menu.css',
            'eds_smart_theme/static/src/css/07_global_topbar.css',
            # 6. بوابة الموظف الجديدة
            # 'eds_smart_theme/static/src/css/08_hr_dashboard.css',
            # 9. Community-native home menu (replaces smart's dropped ent_home_menu.js)
            'eds_smart_theme/static/src/css/09_home_menu.css',

            # --- smart_theme: qweb templates ---
            'eds_smart_theme/static/src/smart/xml/web_inherit.xml',
            'eds_smart_theme/static/src/smart/xml/menu.xml',
            'eds_smart_theme/static/src/smart/xml/bookmark.xml',
            'eds_smart_theme/static/src/smart/xml/spiffy_app_menu_group.xml',
            'eds_smart_theme/static/src/smart/xml/base.xml',
            'eds_smart_theme/static/src/smart/xml/fileviewer.xml',
            'eds_smart_theme/static/src/smart/xml/view_button_icons.xml',
            'eds_smart_theme/static/src/smart/xml/list_renderer.xml',
            'eds_smart_theme/static/src/smart/xml/form_statusbar.xml',
            'eds_smart_theme/static/src/smart/js/widgets/spiffyDocumentViewer.xml',
            'eds_smart_theme/static/src/smart/js/split_view/split_view_form.xml',

            # --- smart_theme: scss ---
            'eds_smart_theme/static/src/smart/scss/custom_varibles.scss',
            'eds_smart_theme/static/src/smart/scss/font_icons.scss',
            'eds_smart_theme/static/src/smart/scss/font-family.scss',
            'eds_smart_theme/static/src/smart/scss/modal.scss',
            'eds_smart_theme/static/src/smart/scss/search_modal.scss',
            'eds_smart_theme/static/src/smart/scss/chat_window.scss',
            'eds_smart_theme/static/src/smart/scss/common_view.scss',
            'eds_smart_theme/static/src/smart/scss/discuss_style.scss',
            'eds_smart_theme/static/src/smart/scss/list_view.scss',
            'eds_smart_theme/static/src/smart/scss/kanban_view.scss',
            'eds_smart_theme/static/src/smart/scss/form_view.scss',
            'eds_smart_theme/static/src/smart/scss/form_chatter.scss',
            'eds_smart_theme/static/src/smart/scss/tree_form_split_view.scss',
            'eds_smart_theme/static/src/smart/scss/top_menu_horizontal.scss',
            'eds_smart_theme/static/src/smart/scss/top_menu_vertical_mini.scss',
            'eds_smart_theme/static/src/smart/scss/top_menu_vertical.scss',
            'eds_smart_theme/static/src/smart/scss/activity_view.scss',
            'eds_smart_theme/static/src/smart/scss/pivot_view.scss',
            'eds_smart_theme/static/src/smart/scss/graph_view.scss',
            'eds_smart_theme/static/src/smart/scss/dashboards.scss',
            'eds_smart_theme/static/src/smart/scss/calendear_view.scss',
            'eds_smart_theme/static/src/smart/scss/setting_page.scss',
            'eds_smart_theme/static/src/smart/scss/tab_styles.scss',
            'eds_smart_theme/static/src/smart/scss/popup_styles.scss',
            'eds_smart_theme/static/src/smart/scss/checkbox_styles.scss',
            'eds_smart_theme/static/src/smart/scss/radio_styles.scss',
            'eds_smart_theme/static/src/smart/scss/separator_styles.scss',
            'eds_smart_theme/static/src/smart/scss/search_panel.scss',
            'eds_smart_theme/static/src/smart/scss/loader.scss',
            'eds_smart_theme/static/src/smart/scss/appdrawer.scss',
            'eds_smart_theme/static/src/smart/scss/bookmarks.scss',
            'eds_smart_theme/static/src/smart/scss/controlpannel.scss',
            'eds_smart_theme/static/src/smart/scss/responsive.scss',
            'eds_smart_theme/static/src/smart/scss/notification.scss',
            'eds_smart_theme/static/src/smart/scss/burger_menu.scss',
            'eds_smart_theme/static/src/smart/scss/ent_voip.scss',
            'eds_smart_theme/static/src/smart/scss/studio.scss',
            'eds_smart_theme/static/src/smart/scss/website_menu.scss',
            'eds_smart_theme/static/src/smart/scss/multi_tab.scss',
            'eds_smart_theme/static/src/smart/scss/to_do_list.scss',
            'eds_smart_theme/static/src/smart/scss/datetime_pickers.scss',
            'eds_smart_theme/static/src/smart/js/widgets/spiffyDocumentViewer.scss',
            'eds_smart_theme/static/src/smart/scss/menu_shape_styles.scss',

            # --- smart_theme: js ---
            # Odoo 19's web.assets_backend no longer bundles jQuery by default (only
            # web.assets_frontend and web.tests_assets do); mohiba's JS below is written
            # against global $/jQuery, so load Odoo's own copy first.
            'web/static/lib/jquery/jquery.js',
            'eds_smart_theme/static/src/smart/js/jquery-ui/jquery-ui.min.js',
            'eds_smart_theme/static/src/smart/js/jquery-ui/jquery-ui.min.css',
            'eds_smart_theme/static/src/smart/js/widgets/spiffyDocumentViewer.js',
            'eds_smart_theme/static/src/smart/js/color_pallet.js',
            'eds_smart_theme/static/src/smart/js/flip_min.js',
            'eds_smart_theme/static/src/smart/js/menu.js',
            'eds_smart_theme/static/src/smart/js/user_menu.js',
            'eds_smart_theme/static/src/smart/js/apps_menu.js',
            'eds_smart_theme/static/src/smart/js/SwitchCompanyMenu.js',
            'eds_smart_theme/static/src/smart/js/form_view_renderer.js',
            'eds_smart_theme/static/src/smart/js/form_controller.js',
            'eds_smart_theme/static/src/smart/js/split_view/split_view_components.js',
            'eds_smart_theme/static/src/smart/js/split_view/split_view_form.js',
            'eds_smart_theme/static/src/smart/js/split_view/split_view_controller.js',
            'eds_smart_theme/static/src/smart/js/split_view/split_view_container.js',
            'eds_smart_theme/static/src/smart/js/list_view_renderer.js',
            'eds_smart_theme/static/src/smart/js/SpiffyPageTitle.js',
            'eds_smart_theme/static/src/smart/js/pwebapp.js',
            'eds_smart_theme/static/src/smart/js/iconpack_load.js',
            'eds_smart_theme/static/src/smart/js/action_service.js',
            'eds_smart_theme/static/src/smart/js/menu_service.js',
            'eds_smart_theme/static/src/smart/js/dialog.js',

            # --- smart_dashboard: js (dependency order) ---
            'eds_smart_theme/static/src/smart_dashboard/js/ui_direction.js',
            'eds_smart_theme/static/src/smart_dashboard/js/quick_links_bar.js',
            'eds_smart_theme/static/src/smart_dashboard/js/webclient_default_action.js',
            'eds_smart_theme/static/src/smart_dashboard/js/backend_nav.js',
            'eds_smart_theme/static/src/smart_dashboard/js/smart_dashboard.js',
            # --- smart_dashboard: scss ---
            'eds_smart_theme/static/src/smart_dashboard/scss/backend_nav.scss',
            'eds_smart_theme/static/src/smart_dashboard/scss/smart_dashboard.scss',
            # --- smart_dashboard: xml ---
            'eds_smart_theme/static/src/smart_dashboard/xml/quick_links_bar.xml',
            'eds_smart_theme/static/src/smart_dashboard/xml/backend_nav.xml',
            'eds_smart_theme/static/src/smart_dashboard/xml/smart_dashboard.xml',

            # --- Community-native home menu (new, replaces smart's ent_home_menu.js) ---
            'eds_smart_theme/static/src/js/home_menu.js',
            'eds_smart_theme/static/src/js/home_menu_overlay.js',
            'eds_smart_theme/static/src/xml/home_menu.xml',

            # JS
            'eds_smart_theme/static/src/js/date_field_patch.js',
            'eds_smart_theme/static/src/js/global_topbar.js',
            'eds_smart_theme/static/src/js/property_theme_dashboard.js',
            # 'eds_smart_theme/static/src/js/hr_employee_dashboard.js',
            # XML Templates
            'eds_smart_theme/static/src/xml/global_topbar.xml',
            'eds_smart_theme/static/src/xml/property_theme_dashboard.xml',
            # 'eds_smart_theme/static/src/xml/hr_employee_dashboard.xml',
        ],
        'web.assets_frontend': [
            'eds_smart_theme/static/src/smart/scss/loginpage.scss',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
