"""
Created on Aug 26, 2018

@author: Admin
"""

from odoo import models, api, fields, SUPERUSER_ID
from .. import READ, CREATE, WRITE, UNLINK
import base64


def intersect(list1, list2):
    for item in list1:
        if item in list2:
            return True
    return False


def get_display(record):
    if not record:
        return ""
    if record:
        return "[%d] %s" % (record.id, record.sudo().display_name)
    else:
        return ""


def binary_info(value):
    if isinstance(value, (str, bytes)):
        try:
            return "%d bytes" % len(base64.b64decode(value))
        except Exception as e:
            return "Invalid base64 data"
    else:
        return "Not a base64 string"


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Base, self).create(vals_list)
        for record in records:
            record._audit_log(CREATE)
        return records

    def write(self, vals):
        self._audit_log(WRITE, vals)
        return super(Base, self).write(vals)

    def unlink(self):
        self._audit_log(UNLINK)
        return super(Base, self).unlink()

    def read(self, fields=None, load="_classic_read"):
        self._audit_log(READ, fields)
        return super(Base, self).read(fields=fields, load=load)

    def _audit_log(self, operation, vals=None):
        if self._name.startswith("audit."):
            return
        if self.env.uid == SUPERUSER_ID:
            return
        # Skip audit logging during web_read nested operations (performance optimization)
        if self.env.context.get("skip_audit_log"):
            return
        config_ids = self.env["audit.config"]._get_audit_config(self._name, operation)
        if not config_ids:
            return
        env_sudo = self.env(su=True)
        config_ids = env_sudo["audit.config"].browse(config_ids)
        for config in config_ids:
            if config.field_ids and vals:
                if not intersect(config.mapped("field_ids.name"), vals):
                    continue
            action_id = self._context.get("params", {}).get("action")
            if (
                not isinstance(action_id, int)
                or not env_sudo["ir.actions.act_window"].browse(action_id).exists()
            ):
                action_id = False
            for record in self:
                record_name = getattr(
                    record.sudo(),
                    "name",
                    getattr(record.sudo(), "display_name", record._name),
                )
                log_id = env_sudo["audit.log"].create(
                    {
                        # "name": record.sudo().name,
                        "name": record_name,
                        "record_id": record.id,
                        "model_id": self.env["ir.model"]._get_id(record._name),
                        "user_id": self.env.uid,
                        "date": fields.Datetime.now(),
                        "type": operation,
                        "action_id": action_id,
                    }
                )
                if config.full_log and operation == WRITE:
                    for name in vals:
                        field = self._fields[name]
                        if field.type == "many2one":
                            old_value = get_display(record[name])
                            new_value = vals[name]

                            if new_value:
                                if not isinstance(new_value, int):
                                    new_value = new_value
                                else:
                                    new_value = env_sudo[field.comodel_name].browse(
                                        new_value
                                    )
                            new_value = get_display(new_value)
                        elif field.type == "one2many":
                            continue
                        else:
                            old_value = record[name]
                            new_value = vals[name]

                        if field.type == "binary":
                            old_value = binary_info(old_value)
                            new_value = binary_info(new_value)
                        self.env["ir.model.fields"]._get_ids(record._name).get

                        detail_log = (
                            env_sudo["audit.log.detail"]
                            .sudo()
                            .create(
                                {
                                    "log_id": log_id.id,
                                    "field_id": self.env["ir.model.fields"]
                                    .search(
                                        [
                                            ("model", "=", record._name),
                                            ("name", "=", name),
                                        ],
                                        limit=1,
                                    )
                                    .id,
                                    "old_value": old_value,
                                    "new_value": new_value,
                                }
                            )
                        )
