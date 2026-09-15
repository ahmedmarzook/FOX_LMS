"""
Created on Jun 12, 2018

@author: Zuhair Hammadi
"""

from odoo.exceptions import UserError


class ConfirmWarning(UserError):
    def __init__(self, msg):
        super(ConfirmWarning, self).__init__(msg)
