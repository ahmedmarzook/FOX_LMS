# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request


class OnlineJob(http.Controller):

    @http.route('/campus/jobs', type='http', auth='public', website=True, sitemap=True)
    def online_job_post(self, search='', **kwargs):
        domain = [('is_published', '=', True), ('states', '=', 'submit')]
        if search:
            domain.append(('job_post', 'ilike', search))
        jobs = request.env['op.job.post'].sudo().search(domain)
        return request.render('openeducat_job_enterprise.job_post_list', {
            'job_post_id': jobs,
        })

    @http.route('/job_post/detail/<model("op.job.post"):job_post_id>',
                type='http', auth='public', website=True, sitemap=True)
    def job_post_detail(self, job_post_id, **kwargs):
        if not job_post_id.sudo().is_published or job_post_id.sudo().states != 'submit':
            return request.not_found()
        return request.render('openeducat_job_enterprise.jobpost_detail', {
            'job_post_id': job_post_id.sudo(),
        })

    @http.route('/job_post/detail/post/<model("op.job.post"):job_description_id>',
                type='http', auth='public', website=True, sitemap=True)
    def job_description_detail(self, job_description_id, **kwargs):
        if not job_description_id.sudo().is_published or job_description_id.sudo().states != 'submit':
            return request.not_found()
        return request.render('openeducat_job_enterprise.jobpost_description', {
            'job_description_id': job_description_id.sudo(),
        })
