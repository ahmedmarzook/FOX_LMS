# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.service import security
from odoo.addons.web.controllers.home import Home


class LoginAs(Home):
    @http.route("/web/login_as/<int:user_id>", type="http", auth="user", sitemap=False)
    def switch_to_user(self, user_id, **kwargs):
        uid = request.env.user.id
        if request.env.user._is_system():
            request.session['impersonate_uid'] = uid
            uid = user_id
            request.session['uid'] = uid
            request.session.session_token = security.compute_session_token(
                request.session, request.env
            )

        return request.redirect(self._login_redirect(uid))

    @http.route("/web/login_back", type="http", auth="user", sitemap=False)
    def switch_back(self, **kwargs):
        uid = request.env.user.id
        impersonate_uid = request.session.get('impersonate_uid')
        if impersonate_uid:
            uid = impersonate_uid
            request.session['uid'] = uid
            request.session['impersonate_uid'] = False
            request.session.session_token = security.compute_session_token(
                request.session, request.env
            )

        return request.redirect(self._login_redirect(uid))
