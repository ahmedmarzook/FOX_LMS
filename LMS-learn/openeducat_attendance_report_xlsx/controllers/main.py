# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

import json
import logging

import werkzeug.exceptions
from werkzeug.urls import url_parse

from odoo import http
from odoo.http import content_disposition, request, route
from odoo.tools.misc import html_escape
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers.report import ReportController

_logger = logging.getLogger(__name__)


class XLSXReportController(ReportController):

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == "xlsx":
            report = request.env["ir.actions.report"]._get_report_from_name(
                reportname
            )
            context = dict(request.env.context)

            if docids:
                docids = [
                    int(item)
                    for item in docids.split(",")
                    if item.isdigit()
                ]

            if data.get("options"):
                data.update(json.loads(data.pop("options")))

            if data.get("context"):
                data_context = json.loads(data.pop("context"))
                context.update(data_context)

            xlsx = report.with_context(**context)._render_xlsx(
                reportname,
                docids,
                data=data,
            )[0]

            headers = [
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet",
                ),
                ("Content-Length", len(xlsx)),
            ]
            return request.make_response(xlsx, headers=headers)

        return super().report_routes(
            reportname,
            docids=docids,
            converter=converter,
            **data,
        )

    @route()
    def report_download(
        self,
        data,
        context=None,
        token=None,
        readonly=True,
    ):
        request_content = json.loads(data)
        url, report_type = request_content[0], request_content[1]

        if report_type != "xlsx":
            return super().report_download(
                data,
                context,
                token=token,
                readonly=readonly,
            )

        reportname = "unknown"
        try:
            reportname = url.split("/report/xlsx/")[1].split("?")[0]
            docids = None

            if "/" in reportname:
                reportname, docids = reportname.split("/", 1)

            if docids:
                response = self.report_routes(
                    reportname,
                    docids=docids,
                    converter="xlsx",
                    context=context,
                )
            else:
                query_data = url_parse(url).decode_query(cls=dict)
                if "context" in query_data:
                    base_context = json.loads(context or "{}")
                    data_context = json.loads(query_data.pop("context"))
                    context = json.dumps({**base_context, **data_context})

                response = self.report_routes(
                    reportname,
                    converter="xlsx",
                    context=context,
                    **query_data,
                )

            report = request.env[
                "ir.actions.report"
            ]._get_report_from_name(reportname)
            filename = f"{report.name}.xlsx"

            if docids:
                ids = [
                    int(item)
                    for item in docids.split(",")
                    if item.isdigit()
                ]
                records = request.env[report.model].browse(ids)

                if report.print_report_name and len(records) == 1:
                    report_name = safe_eval(
                        report.print_report_name,
                        {"object": records, "time": time},
                    )
                    filename = f"{report_name}.xlsx"

            if not response.headers.get("Content-Disposition"):
                response.headers.add(
                    "Content-Disposition",
                    content_disposition(filename),
                )

            return response

        except Exception as error:
            _logger.warning(
                "Error while generating XLSX report %s",
                reportname,
                exc_info=True,
            )
            serialized = http.serialize_exception(error)
            payload = {
                "code": 0,
                "message": "Odoo Server Error",
                "data": serialized,
            }
            response = request.make_response(
                html_escape(json.dumps(payload))
            )
            raise werkzeug.exceptions.InternalServerError(
                response=response
            ) from error
