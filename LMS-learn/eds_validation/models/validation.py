"""
Created on Jun 5, 2018

@author: Zuhair Hammadi
"""

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from .exceptions import ConfirmWarning


class Validation(models.Model):
    _name = "validation"
    _description = "validation"
    _inherit = ["mail.thread"]
    _order = "group_sequence,group_id,sequence,id"

    name = fields.Char(required=True)

    sequence = fields.Integer(default=1)

    group_id = fields.Many2one("validation.group", required=True, ondelete="cascade")

    model_id = fields.Many2one(
        "ir.model",
        related="group_id.model_id",
        readonly=True,
        string="Object",
        ondelete="cascade",
    )

    model = fields.Char(related="model_id.model", readonly=True)

    group_sequence = fields.Integer(
        related="group_id.sequence", store=True, readonly=True
    )
    code = fields.Char()

    active = fields.Boolean(default=True, tracking=True)

    type = fields.Selection(
        [
            ("raise", "Raise Warning"),
            ("confirm", "Confirm Warning"),
            ("log", "Log Warning"),
            ("notify", "Notify Warning"),
        ],
        required=True,
    )

    message = fields.Text(translate=True, required=True)

    on_create = fields.Boolean("On Creation")
    on_write = fields.Boolean("On Update")
    be_write = fields.Boolean("Before Update")
    on_unlink = fields.Boolean("On Deletion")

    condition = fields.Text(
        "Trigger Condition", default="#result = record.start_date > record.end_date"
    )

    log_count = fields.Integer(compute="_calc_log_count")

    log_ids = fields.One2many("validation.log", "validation_id")

    valid_from = fields.Date(related="group_id.valid_from", readonly=True)
    valid_to = fields.Date(related="group_id.valid_to", readonly=True)

    group_ids = fields.Many2many("res.groups", string="Confirm Groups")

    domain = fields.Text(default="[]", required=True)

    group_domain = fields.Text(
        related="group_id.domain", readonly=True, string="Group Domain"
    )

    sticky = fields.Boolean("Sticky Warning")

    @api.depends("log_ids")
    def _calc_log_count(self):
        for record in self:
            record.log_count = len(record.log_ids)

    def action_log(self):
        action = self.env.ref("eds_validation.action_validation_log").read()[0]
        action["domain"] = [("validation_id", "in", self.ids)]
        return action

    @api.model
    @tools.ormcache()
    def _get_validation_group_ids(self):
        cr = self.env.cr
        res = {}
        cr.execute("select model_id,id from validation_group where active")
        for model_id, group_id in cr.fetchall():
            res.setdefault(model_id, [])
            res[model_id].append(group_id)
        return res

    @api.model
    @tools.ormcache("model", "trigger")
    def _get_validation_ids(self, model, trigger):
        model_id = self.env["ir.model"]._get_id(model)
        group_ids = self._get_validation_group_ids().get(model_id)
        if not group_ids:
            return
        validation_ids = self.sudo().search(
            [("group_id", "in", group_ids), ("active", "=", True), (trigger, "=", True)]
        )
        return validation_ids._ids

    def _get_eval_context(self, **kwargs):
        record = kwargs.get("record")
        vals = record.env["ir.actions.actions"]._get_eval_context()

        def log(message, level="info"):
            with self.pool.cursor() as cr:
                cr.execute(
                    """
                    INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                    VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        record.env.uid,
                        "server",
                        self._cr.dbname,
                        __name__,
                        level,
                        message,
                        "validation",
                        self.id,
                        self.name,
                    ),
                )

        vals.update(
            {
                "today": fields.Date.today(),
                "now": fields.Datetime.now(),
                "context": record.env.context,
                "env": record.env,
                "relativedelta": relativedelta,
                "Warning": UserError,
                "log": log,
            }
        )
        vals.update(kwargs)
        return vals

    @api.model
    def _dynamic_validation(self, records, trigger, vals=None):
        if vals is None:
            vals = {}
        if not self.pool.ready:
            return

        if self.env.context.get("_skip_all_validation"):
            return

        validation_ids = self._get_validation_ids(records._name, trigger)
        if not validation_ids:
            return
        if (
            self.env["ir.config_parameter"].sudo().get_param("validation_active")
            != "True"
        ):
            return

        validation_confirm = self.env.context.get("validation_confirm") or ()

        today = fields.Date.today()

        for validation_id in validation_ids:
            validation = self.sudo().browse(validation_id)

            if validation.valid_from > today:
                continue

            if validation.valid_to and validation.valid_to < today:
                continue

            for record in records:
                if not record._match_domain(validation.group_domain):
                    continue
                if not record._match_domain(validation.domain):
                    continue

                localdict = validation._get_eval_context(
                    record=record,
                    object=record,
                    vals=vals,
                    trigger=trigger,
                    _validation=validation,
                )

                safe_eval(validation.condition, localdict, mode="exec", nocopy=True)
                if localdict.get("result"):
                    context = dict(self.env.context, **localdict)
                    message = (
                        self.env["mail.template"]
                        .with_context(context)
                        ._render_template(validation.message, record._name, record.ids)[
                            record.id
                        ]
                    )
                    if validation.code:
                        message = "%s\n%s" % (message, validation.code)
                    if validation.type == "raise":
                        raise ValidationError(message)
                    if validation.type == "confirm":
                        if validation.group_ids and not (
                            self.env.user.group_ids & validation.group_ids
                        ):
                            raise ValidationError(message)
                        if message not in validation_confirm:
                            raise ConfirmWarning(message)
                        continue
                    if validation.type != "notify":
                        self.env["validation.log"].sudo().create(
                            {
                                "res_id": record.id,
                                "validation_id": validation.id,
                                "user_id": self.env.user.id,
                                "date": fields.Datetime.now(),
                                "message": message,
                                trigger: True,
                            }
                        )
                    title = "%s : %s" % (record._description, record.display_name)
                    self.env["bus.bus"]._sendone(self.env.user.partner_id, "simple_notification", {"title": title, "message": message, "sticky": validation.sticky, "type": "warning"})

    @api.model_create_multi
    def create(self, vals_list):
        self.invalidate_model()
        return super(Validation, self).create(vals_list)

    def write(self, vals):
        self.invalidate_model()
        return super(Validation, self).write(vals)

    def unlink(self):
        self.invalidate_model()
        return super(Validation, self).unlink()
