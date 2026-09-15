# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpAlumniGroup(models.Model):
    _name = "op.alumni.group"
    _inherit = ["mail.thread", "website.seo.metadata", "website.published.multi.mixin"]
    _description = "Alumni Group"
    _order = "name"

    name = fields.Char(string="Name", required=True, tracking=True)
    description = fields.Html(string="Description")
    image = fields.Image()
    alumni_student_line = fields.One2many("op.student", "alumni_id", string="Students")
    forum_id = fields.Many2one("forum.forum", string="Forum", readonly=True, copy=False)
    fees_id = fields.Many2one("product.product", string="Fees")
    alumni_fees_amount = fields.Float(string="Fees Amount")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, index=True)
    active = fields.Boolean(default=True)

    def createforum(self):
        for record in self:
            if not record.forum_id:
                record.forum_id = self.env["forum.forum"].create({"name": record.name})
        return True
