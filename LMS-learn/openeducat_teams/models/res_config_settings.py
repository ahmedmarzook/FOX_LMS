# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

import json
import tempfile
from pathlib import Path

from O365 import Account, FileSystemTokenBackend

from odoo import _, fields, models
from odoo.exceptions import UserError


SCOPES = [
    "offline_access",
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/OnlineMeetings.Read",
    "https://graph.microsoft.com/OnlineMeetings.ReadWrite",
]


class TeamsConfig(models.TransientModel):
    _inherit = "res.config.settings"

    application_id = fields.Char(
        string="Application ID",
        config_parameter="openeducat_teams.application_id",
    )
    client_secret = fields.Char(
        string="Client Secret",
        config_parameter="openeducat_teams.client_secret",
    )
    redirect_url = fields.Char(
        string="Redirect URL",
        compute="_compute_redirect_url",
    )
    access_token = fields.Char(
        string="Access Token",
        config_parameter="openeducat_teams.access_token",
        readonly=True,
    )
    bearer_token = fields.Char(
        string="Bearer Token",
        config_parameter="openeducat_teams.bearer_token",
    )
    webhook_url = fields.Char(
        string="Webhook URL",
        config_parameter="openeducat_teams.webhook_url",
    )
    send_card_globally = fields.Boolean(
        string="Send Card for General",
        config_parameter="openeducat_teams.send_card_globally",
    )
    send_card_course = fields.Boolean(
        string="Send Card for Course",
        config_parameter="openeducat_teams.send_card_course",
    )

    def _compute_redirect_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param(
            "web.base.url"
        )
        for record in self:
            record.redirect_url = f"{base_url}/get_auth_token"

    def auth_token(self):
        self.ensure_one()
        if not self.application_id or not self.client_secret:
            raise UserError(
                _("Enter the Microsoft Application ID and Client Secret first.")
            )
        return {
            "type": "ir.actions.act_url",
            "url": f"/get_auth_url/{self.id}",
            "target": "new",
        }

    def do_refresh_token(self):
        params = self.env["ir.config_parameter"].sudo()
        token_json = params.get_param("openeducat_teams.bearer_token")
        application_id = params.get_param("openeducat_teams.application_id")
        client_secret = params.get_param("openeducat_teams.client_secret")

        if not token_json or not application_id or not client_secret:
            raise UserError(_("Authenticate Microsoft Teams first."))

        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "ms_token.txt"
            token_path.write_text(token_json, encoding="utf-8")
            backend = FileSystemTokenBackend(
                token_path=temp_dir,
                token_filename="ms_token.txt",
            )
            account = Account(
                credentials=(application_id, client_secret),
                scopes=SCOPES,
                token_backend=backend,
            )
            if not account.con.refresh_token():
                raise UserError(_("Microsoft token refresh failed."))

            refreshed = json.loads(token_path.read_text(encoding="utf-8"))

        params.set_param(
            "openeducat_teams.access_token",
            refreshed.get("access_token", ""),
        )
        params.set_param(
            "openeducat_teams.bearer_token",
            json.dumps(refreshed),
        )
        return True
