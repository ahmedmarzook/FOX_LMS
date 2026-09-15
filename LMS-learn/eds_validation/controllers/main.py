"""
Created on Oct 13, 2019

@author: Zuhair Hammadi
"""

# from odoo.addons.web.controllers.main import DataSet
from odoo.addons.web.controllers.dataset import DataSet
from odoo.models import check_method_name
from odoo.api import call_kw
from odoo.http import request


class MyDataSet(DataSet):
    def _call_kw(self, model, method, args, kwargs):
        check_method_name(method)
        context = kwargs and kwargs.get("context") or {}
        print("model ==>", model)
        print("method ==>", method)
        return call_kw(
            request.env[model].with_context(
                validation_confirm=context.get("validation_confirm")
            ),
            method,
            args,
            kwargs,
        )
