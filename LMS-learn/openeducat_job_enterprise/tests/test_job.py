from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestJobModels(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.job_type = cls.env['op.job.type'].create({
            'name': 'Full Time',
            'code': 'FULL',
        })
        cls.stage = cls.env['job.post.stage'].create({
            'name': 'New',
            'sequence': 1,
        })
        today = fields.Date.today()
        cls.job = cls.env['op.job.post'].create({
            'name': '/',
            'job_post': 'Application Engineer',
            'street': 'Test Street',
            'street2': 'Test Building',
            'city': 'Cairo',
            'employment_type': cls.job_type.id,
            'salary_from': 1000.0,
            'salary_upto': 2000.0,
            'start_date': today,
            'end_date': today + timedelta(days=30),
            'states': 'submit',
            'is_published': True,
        })
        cls.applicant = cls.env['op.job.applicant'].create({
            'name': '/',
            'post_id': cls.job.id,
            'stage_id': cls.stage.id,
        })

    def test_job_workflow(self):
        self.job.set_draft()
        self.assertEqual(self.job.states, 'draft')
        self.job.set_review()
        self.assertEqual(self.job.states, 'review')
        self.job.set_submit()
        self.assertEqual(self.job.states, 'submit')
        self.job.set_done()
        self.assertEqual(self.job.states, 'done')
        self.job.set_cancel()
        self.assertEqual(self.job.states, 'cancel')
        self.job.set_recruit()
        self.assertEqual(self.job.states, 'review')

    def test_job_counts_and_website_url(self):
        self.job._compute_application_count()
        self.job._compute_new_application_count()
        self.job._compute_website_url()
        self.assertEqual(self.job.application_count, 1)
        self.assertEqual(self.job.new_application_count, 1)
        self.assertEqual(
            self.job.website_url,
            f'/job_post/detail/post/{self.job.id}',
        )

    def test_invalid_job_dates(self):
        today = fields.Date.today()
        with self.assertRaises(ValidationError):
            self.env['op.job.post'].create({
                'name': '/',
                'job_post': 'Invalid Dates Job',
                'street': 'Test Street',
                'street2': 'Test Building',
                'city': 'Cairo',
                'salary_from': 1000.0,
                'salary_upto': 2000.0,
                'start_date': today,
                'end_date': today - timedelta(days=1),
            })

    def test_applicant_helpers(self):
        values = self.applicant._onchange_post_id_internal(self.job.id)
        self.assertEqual(values['value']['stage_id'], self.stage.id)
        values = self.applicant._onchange_stage_id_internal(self.stage.id)
        self.assertFalse(values['value']['date_closed'])
        self.applicant._compute_get_attachment_number()
        self.assertEqual(self.applicant.attachment_number, 0)
        action = self.applicant.action_get_attachment_tree_view()
        self.assertEqual(action['res_model'], 'ir.attachment')


    def test_resume_fields(self):
        applicant = self.env['op.job.applicant'].create({
            'name': '/',
            'post_id': self.job.id,
            'resume': b'VEVTVA==',
            'resume_filename': 'resume.txt',
        })
        self.assertTrue(applicant.resume)
        self.assertEqual(applicant.resume_filename, 'resume.txt')
