# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OpParent(models.Model):
    _name = "op.parent"
    _description = "Parent"

    name = fields.Many2one('res.partner', 'Name', required=True)
    user_id = fields.Many2one('res.users', string='User', store=True)
    student_ids = fields.Many2many('op.student', string='Student(s)')
    mobile = fields.Char(string='Mobile', related='name.phone', readonly=False)
    active = fields.Boolean(default=True)
    relationship_id = fields.Many2one(
        'op.parent.relationship',
        string='Relation with Student',
        required=True
    )

    _sql_constraints = [(
        'unique_parent',
        'unique(name)',
        'Can not create parent multiple times.!'
    )]

    @api.onchange('name')
    def _onchange_name(self):
        self.user_id = self.name.user_id.id if self.name.user_id else False

    @api.model_create_multi
    def create(self, vals_list):
        records = super(OpParent, self).create(vals_list)
        for record in records:
            record._update_parent_child_users()
        return records

    def write(self, vals):
        res = super(OpParent, self).write(vals)
        for record in self:
            record._update_parent_child_users()
        return res

    def unlink(self):
        for record in self:
            if record.user_id and hasattr(record.user_id, 'child_ids'):
                record.user_id.child_ids = [(6, 0, [])]
        return super(OpParent, self).unlink()

    def _update_parent_child_users(self):
        for record in self:
            if record.user_id and hasattr(record.user_id, 'child_ids'):
                user_ids = [
                    student.user_id.id
                    for student in record.student_ids
                    if student.user_id
                ]
                record.user_id.child_ids = [(6, 0, user_ids)]

    def create_parent_user(self):
        users_res = self.env['res.users']

        for record in self:
            if not record.name.email:
                raise UserError(_('Update parent email id first.'))

            if not record.name.user_id:
                child_user_ids = [
                    student.user_id.id
                    for student in record.student_ids
                    if student.user_id
                ]

                vals = {
                    'name': record.name.name,
                    'partner_id': record.name.id,
                    'login': record.name.email,
                    'is_parent': True,
                    'tz': self._context.get('tz'),
                }

                if 'child_ids' in users_res._fields:
                    vals['child_ids'] = [(6, 0, child_user_ids)]

                user_id = users_res.create(vals)

                # Add groups after user creation only if the field exists.
                if 'group_ids' in user_id._fields:
                    parent_group = self.env.ref(
                        'openeducat_parent.group_op_parent',
                        raise_if_not_found=False
                    )
                    portal_group = self.env.ref(
                        'base.group_portal',
                        raise_if_not_found=False
                    )
                    groups = (portal_group | parent_group) if portal_group and parent_group else (portal_group or parent_group)
                    if groups:
                        user_id.group_ids = [(4, group.id) for group in groups]

                record.user_id = user_id.id
                record.name.user_id = user_id.id


class OpStudent(models.Model):
    _inherit = "op.student"

    parent_ids = fields.Many2many('op.parent', string='Parent')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(OpStudent, self).create(vals_list)
        for record in records:
            for parent in record.parent_ids:
                parent._update_parent_child_users()
        return records

    def write(self, vals):
        res = super(OpStudent, self).write(vals)
        if vals.get('parent_ids') or vals.get('user_id'):
            for record in self:
                for parent in record.parent_ids:
                    parent._update_parent_child_users()
        return res

    def unlink(self):
        parents = self.mapped('parent_ids')
        res = super(OpStudent, self).unlink()
        for parent in parents:
            parent._update_parent_child_users()
        return res

    def get_parent(self):
        action = self.env.ref(
            'openeducat_parent.act_open_op_parent_view'
        ).read()[0]
        action['domain'] = [('student_ids', 'in', self.ids)]
        return action


class OpSubjectRegistration(models.Model):
    _inherit = "op.subject.registration"

    @api.model_create_multi
    def create(self, vals_list):
        if hasattr(self.env.user, 'child_ids') and self.env.user.child_ids:
            raise UserError(_(
                'Invalid Action!\nParent can not create Subject Registration!'
            ))
        return super(OpSubjectRegistration, self).create(vals_list)

    def write(self, vals):
        if hasattr(self.env.user, 'child_ids') and self.env.user.child_ids:
            raise UserError(_(
                'Invalid Action!\nParent can not edit Subject Registration!'
            ))
        return super(OpSubjectRegistration, self).write(vals)
