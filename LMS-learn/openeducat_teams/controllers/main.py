import json
import tempfile
from pathlib import Path

from O365 import Account, FileSystemTokenBackend
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_teams.models.res_config_settings import SCOPES


class AuthController(http.Controller):

    @http.route(
        "/get_auth_url/<int:current_id>",
        type="http",
        methods=["GET"],
        auth="user",
    )
    def get_auth_url(self, current_id, **kwargs):
        settings = request.env["res.config.settings"].sudo().browse(
            current_id
        ).exists()
        if not settings or not settings.application_id or not settings.client_secret:
            return request.render("openeducat_teams.token_refused")

        temp_dir = tempfile.mkdtemp(prefix="openeducat_teams_")
        backend = FileSystemTokenBackend(
            token_path=temp_dir,
            token_filename="ms_token.txt",
        )
        account = Account(
            credentials=(settings.application_id, settings.client_secret),
            scopes=SCOPES,
            token_backend=backend,
        )
        auth_url, state = account.con.get_authorization_url(
            requested_scopes=SCOPES,
            redirect_uri=settings.redirect_url,
        )

        params = request.env["ir.config_parameter"].sudo()
        params.set_param("openeducat_teams.oauth_state", state)
        params.set_param("openeducat_teams.oauth_temp_dir", temp_dir)
        return redirect(auth_url)

    @http.route(
        "/get_auth_token",
        type="http",
        methods=["GET"],
        auth="user",
        website=True,
    )
    def get_auth_token(self, **kwargs):
        params = request.env["ir.config_parameter"].sudo()
        application_id = params.get_param("openeducat_teams.application_id")
        client_secret = params.get_param("openeducat_teams.client_secret")
        state = params.get_param("openeducat_teams.oauth_state")
        temp_dir = params.get_param("openeducat_teams.oauth_temp_dir")
        redirect_url = (
            params.get_param("web.base.url").rstrip("/") + "/get_auth_token"
        )

        if not all([application_id, client_secret, state, temp_dir]):
            return request.render("openeducat_teams.token_refused")

        backend = FileSystemTokenBackend(
            token_path=temp_dir,
            token_filename="ms_token.txt",
        )
        account = Account(
            credentials=(application_id, client_secret),
            scopes=SCOPES,
            token_backend=backend,
        )
        result = account.con.request_token(
            request.httprequest.url,
            state=state,
            redirect_uri=redirect_url,
            store_token=True,
        )
        token_path = Path(temp_dir) / "ms_token.txt"
        if not result or not token_path.exists():
            return request.render("openeducat_teams.token_refused")

        token_data = json.loads(token_path.read_text(encoding="utf-8"))
        params.set_param(
            "openeducat_teams.access_token",
            token_data.get("access_token", ""),
        )
        params.set_param(
            "openeducat_teams.bearer_token",
            json.dumps(token_data),
        )
        params.set_param("openeducat_teams.oauth_state", "")
        params.set_param("openeducat_teams.oauth_temp_dir", "")
        return request.render("openeducat_teams.token_confirmed")
