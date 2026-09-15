"""
Created on Nov 11, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields, api
import json


class ApprovalTransferWizard(models.TransientModel):
    _name = "approval.transfer.wizard"
    _description = "Approval Transfer Wizard"

    @api.model
    def _get_state(self):
        print("self._context 1***>>>", self._context)
        flds = ["record_ref", "model", "record_id", "state", "reason"]
        self.default_get(flds)
        print("self._context 2***>>>", self._context)
        model = self._context.get("active_model")
        print("model ==>", self.model)
        print("model55 ==>", self._context)
        print("model66 ==>", self.env.context)

        if not model:
            return []

        selection = dict(
            self.env[model]._fields["state"]._description_selection(self.env)
        )
        print("selection ==>", selection)
        record = self.env[model].browse(self._context.get("active_id"))
        print("record ==>", record)
        workflow_states = json.loads(record.workflow_states)
        print("workflow_states ==>", workflow_states)
        print("reversed(workflow_states) ==>", reversed(workflow_states))
        res = []
        for state in reversed(workflow_states):
            if state == record.state:
                break
            res.insert(0, (state, selection[state]))
        print("res ==>", res)
        return res

    model = fields.Char(
        default=lambda self: self._context.get("active_model"), required=True
    )
    record_id = fields.Integer(
        default=lambda self: self._context.get("active_id"),
        required=True,
        string="Record ID",
    )
    record_ref = fields.Char("Record", compute="_calc_record_ref")

    reason = fields.Text(required=True)

    # state = fields.Selection(_get_state, required=True, string="Status")
    # state = fields.Selection(
    #     selection=[
    #         ("Employee of E-Learning Department", "موظف في قسم التعليم الإلكتروني"),
    #         ("approved", "موافق عليه"),
    #     ],
    #     string="Status",
    #     required=True,
    # )
    @api.model
    def _get_state_selection(self):
        """Dynamically fetch the available state selections"""

        active_model = self._context.get("active_model")
        print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", self._context)
        print("ppppppppppppppppppppppppppppppppppppppppppppp", active_model)
        active_id = self._context.get("active_id")
        print("22222222222222222222222222222222222222222222222", active_id)

        if not active_model or not active_id:
            return []

        try:
            record = self.env[active_model].browse(active_id)
            state_field = self.env[active_model]._fields["state"]
            all_states = dict(state_field._description_selection(self.env))

            workflow_states = (
                json.loads(record.workflow_states) if record.workflow_states else []
            )
            print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk", workflow_states)

            available_states = []
            for state in reversed(workflow_states):
                if state == record.state:
                    break
                if state in all_states:
                    available_states.insert(0, (state, all_states[state]))

            return available_states

        except Exception as e:
            _logger.error("Error in _get_state_selection: %s", str(e))
            return []

    state = fields.Selection(
        selection=lambda self: self._get_state_selection(),
        string="State",
        required=True,
        store=True,
        readonly=False,
    )

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     print("Default Get Context:", self._context)
    #     states = self._get_state_selection()
    #     self._fields["state"].selection = states
    #     print("1111111111111111111111111111111111111111111111",states)
    #     if states:
    #         res["state"] = states[0][0]  # Set the first value as the default
    #
    #     return res

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     print("Default Get Context:", self._context)
    #     states = self._get_state_selection()
    #     print("Default Get State:", states)
    #     self._fields["state"].selection = states
    #     print("Default Get Result:", self._fields["state"].selection)
    #     return res

    @api.depends("model", "record_id")
    def _calc_record_ref(self):
        for wizard in self:
            record = self.env[wizard.model].browse(wizard.record_id).exists()
            wizard.record_ref = record and "%s,%d" % (record._name, record.id)

    def action_transfer(self):
        ctx = self.env.context.copy()
        ctx.pop("default_state", False)
        ctx.pop("fixed_transfer_state", False)
        record = self.env[self.model].browse(self.record_id)
        action = record.with_context(ctx)._action_transfer(self.state, self.reason)
        return action or {"type": "ir.actions.client", "tag": "soft_reload"}
