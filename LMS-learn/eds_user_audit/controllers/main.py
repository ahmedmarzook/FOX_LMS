"""
Created on Aug 29, 2018

@author: Zuhair Hammadi
"""

from odoo import http, SUPERUSER_ID
from odoo.http import request
from .. import WRITE


def remove_duplicates(lines):
    res = []
    added = set()
    for vals in lines:
        value = (
            vals["field"],
            vals["old_value"],
            vals["new_value"],
            vals["user"],
            vals["date"],
        )
        if value in added:
            continue
        added.add(value)
        res.append(vals)
    return res


class UserAudit(http.Controller):
    @http.route("/eds_user_audit/create_xml_id", type="json", auth="user")
    def create_xml_id(self, model, record_id):
        record = request.env[model].browse(record_id)
        if not record._context.get("lang") != "en_US":
            record = record.with_context(lang="en_US")
        xml_id = record._create_external_id()
        return xml_id

    @http.route("/eds_user_audit/record_info", type="json", auth="user")
    def record_info(self, model, record_id):
        record = request.env[model].browse(record_id)

        model_id = request.env["ir.model"]._get_id(model)

        format_datetime = lambda value: request.env[
            "ir.qweb.field.datetime"
        ].value_to_html(value, {})

        data = {
            "id": record.id,
            "name": record.display_name,
            "create_date": "create_date" in record
            and format_datetime(record.create_date),
            "create_uid": "create_uid" in record and record.create_uid.display_name,
            "write_date": "write_date" in record and format_datetime(record.write_date),
            "write_uid": "write_uid" in record and record.write_uid.display_name,
            "lines": [],
            "tracking_value_count": 0,
            "log_count": 0,
            "update_log_count": 0,
        }

        env_sudo = request.env(user=SUPERUSER_ID)

        model_data = env_sudo["ir.model.data"].search(
            [("model", "=", model), ("res_id", "=", record_id)], order="id", limit=1
        )
        if model_data:
            data["xmlid"] = model_data.complete_name
            data["noupdate"] = str(model_data.noupdate)
            data["xmlid_id"] = model_data.id

        log_ids = (
            env_sudo["audit.log"]
            .search(
                [
                    ("record_id", "=", record_id),
                    ("model_id", "=", model_id),
                    ("type", "=", WRITE),
                ]
            )
            .ids
        )

        data["log_count"] = env_sudo["audit.log"].search(
            [("record_id", "=", record_id), ("model_id.model", "=", model)], count=True
        )
        message_ids = env_sudo["mail.message"].search(
            [("model", "=", model), ("res_id", "=", record_id)]
        )
        data["tracking_value_count"] = env_sudo["mail.tracking.value"].search(
            [("mail_message_id", "in", message_ids.ids)], count=True
        )

        if log_ids:
            data["update_log_count"] = env_sudo["audit.log.detail"].search(
                [("log_id", "in", log_ids)], count=True
            )
            for detail in env_sudo["audit.log.detail"].search(
                [("log_id", "in", log_ids)], order="id desc", limit=100
            ):
                data["lines"].append(
                    {
                        "field": detail.field_id.field_description,
                        "old_value": detail.old_value_display,
                        "new_value": detail.new_value_display,
                        "user": detail.log_id.user_id.display_name,
                        "date": format_datetime(detail.log_id.date),
                        "id": detail.id,
                        "date_value": detail.log_id.date,
                    }
                )

        if message_ids:
            tracking_value_ids = env_sudo["mail.tracking.value"].search(
                [("mail_message_id", "in", message_ids.ids)], order="id desc", limit=100
            )
            for value_id in tracking_value_ids:
                data["lines"].append(
                    {
                        "field": value_id.field_desc,
                        "old_value": value_id.get_old_display_value()[0],
                        "new_value": value_id.get_new_display_value()[0],
                        "user": value_id.create_uid.display_name,
                        "date": format_datetime(value_id.create_date),
                        "id": value_id.id,
                        "date_value": value_id.create_date,
                    }
                )

        if "approval.log" in env_sudo:
            log_ids = env_sudo["approval.log"].search(
                [("record_id", "=", record_id), ("model_id", "=", "model_id")],
                order="id desc",
                limit=100,
            )
            for log_id in log_ids:
                data["lines"].append(
                    {
                        "field": env_sudo[model]._fields["state"].string,
                        "old_value": log_id.old_name,
                        "new_value": log_id.name,
                        "user": log_id.user_id.display_name,
                        "date": format_datetime(log_id.date),
                        "id": log_id.id,
                        "date_value": log_id.date,
                    }
                )

        data["lines"] = sorted(
            data["lines"],
            key=lambda vals: (vals["date_value"], vals["id"]),
            reverse=True,
        )

        data["lines"] = remove_duplicates(data["lines"])

        data["lines"] = data["lines"][:100]

        for vals in data["lines"]:
            vals.pop("id")
            vals.pop("date_value")

        return data
