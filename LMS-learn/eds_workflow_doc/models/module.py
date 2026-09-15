"""
Created on Apr 9, 2019

@author: Zuhair Hammadi
"""

from odoo.modules import module

original_get_module_icon = module.get_module_icon


def get_module_icon(module):
    module = module or ""
    return original_get_module_icon(module)


module.get_module_icon = get_module_icon
