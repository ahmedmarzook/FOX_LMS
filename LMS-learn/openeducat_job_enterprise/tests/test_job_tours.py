from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestJobTours(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        job_type = cls.env['op.job.type'].create({
            'name': 'Full Time',
            'code': 'TOUR-FULL',
        })
        today = fields.Date.today()
        cls.job = cls.env['op.job.post'].create({
            'name': '/',
            'job_post': 'Application Engineer',
            'street': '602 Suyojan Complex',
            'street2': 'Near Hotel President',
            'city': 'Cairo',
            'employment_type': job_type.id,
            'salary_from': 1000.0,
            'salary_upto': 2000.0,
            'start_date': today,
            'end_date': today + timedelta(days=30),
            'states': 'submit',
            'description': 'Odoo 19 test job description',
            'is_published': True,
        })

    def test_job_list_tour(self):
        self.start_tour('/campus/jobs', 'openeducat_job_list_tour')

    def test_job_detail_tour(self):
        self.start_tour(
            f'/job_post/detail/{self.job.id}',
            'openeducat_job_detail_tour',
        )

    def test_job_description_tour(self):
        self.start_tour(
            f'/job_post/detail/post/{self.job.id}',
            'openeducat_job_description_tour',
        )

    def test_job_apply_form_tour(self):
        self.start_tour(
            f'/job_post/detail/{self.job.id}',
            'openeducat_job_apply_form_tour',
        )
