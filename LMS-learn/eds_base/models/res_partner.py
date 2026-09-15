from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_avatar(self, avatar_field, image_field):
        """
        Override _compute_avatar to bypass AccessError on res.users when evaluating user_ids.
        This fixes the issue where a portal user trying to view a partner's avatar
        crashes during 'partner.user_ids - partner.user_ids.filtered('share')'.
        """
        # Run the standard compute in sudo mode to avoid AccessError.
        super(ResPartner, self.sudo())._compute_avatar(avatar_field, image_field)
        for record in self:
            record[avatar_field] = record.sudo()[avatar_field]
