from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        res = super(Http, self).session_info()

        if request:
            if request.session.get('impersonate_uid'):
                res["impersonate"] = True
            res["is_system"] = request.env.user._is_system()

        return res
