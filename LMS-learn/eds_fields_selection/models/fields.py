from odoo import fields

super_description_selection = fields.Selection._description_selection
super_get_values = fields.Selection.get_values


def _get_selection(self, env):
    if "ir.model.fields.selection.custom" not in env:
        return
    field_id = env["ir.model.fields"]._get(self.model_name, self.name).id
    return env["ir.model.fields.selection.custom"]._get_selection(field_id)


def _get_approval_selection(self, env):
    if "approval.record" not in env:
        return
    model = env[self.model_name]
    if model._isinstance("approval.record") and self.name == "state":
        return model._get_state()


def _description_selection(self, env):
    custom_selection = _get_selection(self, env)
    if custom_selection:
        return custom_selection

    approval_selection = _get_approval_selection(self, env)
    if approval_selection:
        return approval_selection

    return super_description_selection(self, env)


def get_values(self, env):
    custom_selection = _get_selection(self, env)
    if custom_selection:
        return [sel[0] for sel in custom_selection]

    approval_selection = _get_approval_selection(self, env)
    if approval_selection:
        return list(map(lambda item: item[0], approval_selection))

    return super_get_values(self, env)


fields.Selection._description_selection = _description_selection
fields.Selection.get_values = get_values