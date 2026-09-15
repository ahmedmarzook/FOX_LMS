"""
Created on Sep 6, 2021

@author: Fatima Shubbar
"""

from odoo import models, fields, api, _


class CancellationRecord(models.Model):
    _name = "cancellation.record"
    _inherit = ["approval.record", "mail.thread", "mail.activity.mixin"]
    _description = "Cancellation Record Workflow Log"
    _order = "id desc"

    name = fields.Char(
        string="Number", required=True, readonly=True, copy=False, default=_("New")
    )
    requester_id = fields.Many2one("res.users")
    model_id = fields.Many2one(
        "ir.model", string="Object", required=True, ondelete="cascade"
    )
    record_id = fields.Integer(required=True)
    model_name = fields.Char()
    rec_ref = fields.Char(compute="_calc_rec_ref")
    reason = fields.Text()

    def _calc_rec_ref(self):
        for record in self:
            ref = ""
            if record.record_id and record.model_id:
                rec = record.get_record()
                if rec.exists():
                    ref = "%s,%s" % (record.model_id.model, record.record_id)
            record.rec_ref = ref

    def get_record(self):
        return self.env[self.model_id.model].browse(self.record_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(self._name)
        return super(CancellationRecord, self).create(vals_list)

    def _on_approve(self):
        rec = self.get_record()
        cancel_state = rec._on_cancel()
        if cancel_state:
            rec.write({"state": cancel_state})
        super(CancellationRecord, self)._on_approve()
