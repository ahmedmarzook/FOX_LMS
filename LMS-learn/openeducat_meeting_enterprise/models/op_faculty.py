# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, models


class OpFaculty(models.Model):
    _inherit = "op.faculty"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        category = self.env['res.partner.category'].search(
            [('name', '=', 'Faculty')], limit=1)
        if category:
            for record in records:
                partner = record.partner_id
                if partner:
                    partner.write({'category_id': [(4, category.id)]})
        return records
