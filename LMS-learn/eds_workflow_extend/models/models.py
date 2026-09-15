from odoo import api, fields, models, _
import json


class WorkflowDepartmentProxy:
    """
    Proxy class that wraps hr.employee records to redirect department_id
    access to workflow_department_id for approval filter_condition evaluation.

    This allows existing XML filter_conditions like:
        record.employee_id.department_id.manager_id.user_id == user
    to automatically use workflow_department_id without modifying 50+ XML files.

    The proxy intercepts 'department_id' attribute access and returns
    workflow_department_id if set, otherwise falls back to department_id.
    """

    def __init__(self, employee):
        object.__setattr__(self, "_employee", employee)

    def __getattr__(self, name):
        employee = object.__getattribute__(self, "_employee")
        if name == "department_id":
            # Redirect to workflow_department_id for approval routing
            if (
                hasattr(employee, "workflow_department_id")
                and employee.workflow_department_id
            ):
                return employee.workflow_department_id
            return employee.department_id
        return getattr(employee, name)

    def __bool__(self):
        return bool(object.__getattribute__(self, "_employee"))

    def __eq__(self, other):
        employee = object.__getattribute__(self, "_employee")
        if isinstance(other, WorkflowDepartmentProxy):
            return employee == object.__getattribute__(other, "_employee")
        return employee == other

    def __hash__(self):
        return hash(object.__getattribute__(self, "_employee"))


class WorkflowRecordProxy:
    """
    Proxy class that wraps approval records to intercept employee_id access
    and return a WorkflowDepartmentProxy instead of the raw employee.

    This ensures that when filter_condition accesses record.employee_id.department_id,
    it goes through the WorkflowDepartmentProxy which redirects to workflow_department_id.
    """

    def __init__(self, record):
        object.__setattr__(self, "_record", record)

    def __getattr__(self, name):
        record = object.__getattribute__(self, "_record")
        value = getattr(record, name)

        # Wrap employee fields with WorkflowDepartmentProxy
        if name in ("employee_id", "x_employee_id") and value:
            if hasattr(value, "_name") and value._name == "hr.employee":
                return WorkflowDepartmentProxy(value)

        return value

    def __bool__(self):
        return bool(object.__getattribute__(self, "_record"))

    def __getitem__(self, key):
        record = object.__getattribute__(self, "_record")
        value = record[key]

        # Wrap employee fields with WorkflowDepartmentProxy
        if key in ("employee_id", "x_employee_id") and value:
            if hasattr(value, "_name") and value._name == "hr.employee":
                return WorkflowDepartmentProxy(value)

        return value

    def __setitem__(self, key, value):
        record = object.__getattribute__(self, "_record")
        record[key] = value


class ApprovalReturnState(models.Model):
    _name = "approval.return.state"

    name = fields.Char()
    state = fields.Char()
    model = fields.Char()


class ApprovalTransferState(models.Model):
    _name = "approval.transfer.state"

    name = fields.Char()
    state = fields.Char()
    model = fields.Char()


class ApprovalRecord(models.AbstractModel):
    _inherit = "approval.record"

    def _action_return(self, state, reason):
        """
        Override to fix edge case: at the last state, button_approve_enabled is False,
        causing the parent method to filter out the record and return None without
        changing the state. This override skips the button_approve_enabled filter
        when called from the wizard context (force_return=True).
        """
        # If force_return context is set, skip the button_approve_enabled filter
        if self.env.context.get("force_return"):
            old_states = {}
            for record in self:
                old_states[record] = record.state
                record._remove_approval_activity(action="return", reason=reason)
                record.with_context(reject_reason=reason).write({"state": state})

            actions = []
            for record in self:
                record._schedule_approval_activity()
                actions.append(
                    record._on_script_custom(
                        "on_return",
                        new_state=state,
                        old_state=old_states[record],
                        reason=reason,
                    )
                    or record._on_return(
                        new_state=state, old_state=old_states[record], reason=reason
                    )
                )

            return self._clean_actions(actions)

        # Default behavior - call parent
        return super()._action_return(state, reason)

    def action_transfer(self):
        action = super(ApprovalRecord, self).action_transfer()
        ApprovalTransfer = self.env["approval.transfer.state"].sudo()
        selection = dict(
            self.env[self._name]._fields["state"]._description_selection(self.env)
        )
        workflow_states = json.loads(self.workflow_states)
        res = []
        states = []
        state_ids = []
        for state in reversed(workflow_states):
            if state == self.state:
                break
            res.insert(0, (state, selection[state]))
            states.append(state)
            existing_state = ApprovalTransfer.search(
                [("state", "=", state), ("model", "=", self._name)], limit=1
            )
            if existing_state:
                if existing_state.name != selection[state]:
                    existing_state.write({"name": selection[state]})
                state_ids.append(existing_state.id)
            else:
                new_state = ApprovalTransfer.create(
                    {"name": selection[state], "state": state, "model": self._name}
                )
                state_ids.append(new_state.id)
        action["context"].update({"default_approval_state_ids": state_ids})
        return action

    def action_return(self):
        action = super(ApprovalRecord, self).action_return()
        context = dict(self._context)
        fixed_return_state_list = context.get("fixed_return_state_list")
        ApprovalReturn = self.env["approval.return.state"].sudo()
        selection = dict(
            self.env[self._name]._fields["state"]._description_selection(self.env)
        )
        workflow_states = self.workflow_states
        workflow_states = json.loads(workflow_states)
        if fixed_return_state_list:
            workflow_states = list(fixed_return_state_list)
        res = []
        states = []
        state_ids = []
        # Find the index of current state in workflow_states
        try:
            current_index = workflow_states.index(self.state)
        except ValueError:
            # Current state not in workflow_states, no states to return to
            current_index = 0
        # Collect all states before the current state
        for state in workflow_states[:current_index]:
            if state not in selection:
                continue
            res.insert(0, (state, selection[state]))
            states.append(state)
            existing_state = ApprovalReturn.search(
                [("state", "=", state), ("model", "=", self._name)], limit=1
            )
            if existing_state:
                if existing_state.name != selection[state]:
                    existing_state.write({"name": selection[state]})
                state_ids.append(existing_state.id)
            else:
                new_state = ApprovalReturn.create(
                    {"name": selection[state], "state": state, "model": self._name}
                )
                state_ids.append(new_state.id)
        action["context"].update({"default_approval_state_ids": state_ids})
        return action


class ApprovalConfigExtended(models.Model):
    _inherit = "approval.config"

    approve_button_name = fields.Char(default="Approve", translate=True)
    approve_confirm_msg = fields.Char(default="Approve ?", translate=True)

    reject_button_name = fields.Char(default="Reject", translate=True)
    reject_button_wizard = fields.Boolean(default=True)
    approve_button_wizard = fields.Boolean(default=True)
    reject_confirm_msg = fields.Char(default="Reject ?", translate=True)
