import base64

from odoo.http import Controller, request, route


class BackendThemeController(Controller):

    @route("/app-menu-logo", type="http", auth="user")
    def app_menu_logo(self, **kwargs):
        logo = request.env.user.company_id.logo
        if not logo:
            return request.not_found()
        return request.make_response(
            base64.b64decode(logo),
            headers=[
                ("Content-Type", "image/png"),
                ("Cache-Control", "private, max-age=3600"),
            ],
        )

    @route(
        "/web/backend_theme_customizer/read",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def customizer_read(self):
        user = request.env.user
        company = user.company_id
        return {
            "user_settings": {
                "chatter_position": user.chatter_position,
                "dark_mode": user.dark_mode,
            },
            "company_settings": {
                "theme_menu_style": company.theme_menu_style,
                "theme_font_name": company.theme_font_name,
                "theme_color_brand": company.theme_color_brand,
                "theme_background_color": company.theme_background_color,
                "theme_sidebar_color": company.theme_sidebar_color,
                "google_font": company.google_font,
            },
            "can_manage_company": user.has_group("base.group_erp_manager"),
        }

    @route(
        "/web/backend_theme_customizer/write",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def customizer_write(self, company_settings=None, user_settings=None):
        user = request.env.user

        allowed_user = {"chatter_position", "dark_mode"}
        values = {
            key: value
            for key, value in (user_settings or {}).items()
            if key in allowed_user
        }
        if values:
            user.sudo().write(values)

        if company_settings and user.has_group("base.group_erp_manager"):
            allowed_company = {
                "theme_menu_style",
                "theme_font_name",
                "theme_color_brand",
                "theme_background_color",
                "theme_sidebar_color",
                "google_font",
            }
            values = {
                key: value
                for key, value in company_settings.items()
                if key in allowed_company
            }
            if values:
                user.company_id.sudo().write(values)
        return True
