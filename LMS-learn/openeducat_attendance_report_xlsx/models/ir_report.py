# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("xlsx", "XLSX")],
        ondelete={"xlsx": "set default"},
    )

    @api.model
    def _render_xlsx(self, report_ref, docids, data=None):
        report = self._get_report(report_ref)
        report_model_name = f"report.{report.report_name}"
        report_model = self.env.get(report_model_name)

        if report_model is None:
            raise UserError(_("%s model was not found") % report_model_name)

        return (
            report_model.with_context(active_model=report.model)
            .sudo(False)
            .create_xlsx_report(docids, data or {})
        )

    @api.model
    def _get_report_from_name(self, report_name):
        report = super()._get_report_from_name(report_name)
        if report:
            return report

        return self.with_context(
            **self.env["res.users"].context_get()
        ).search(
            [
                ("report_type", "=", "xlsx"),
                ("report_name", "=", report_name),
            ],
            limit=1,
        )
