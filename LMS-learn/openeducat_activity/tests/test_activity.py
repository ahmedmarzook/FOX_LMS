###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging

from .test_activity_common import TestActivityCommon

_logger = logging.getLogger(__name__)


class TestActivity(TestActivityCommon):

    def test_case_activity_1(self):
        activity = self.op_activity.search([])
        if not activity:
            raise AssertionError('Error in data, please check for reference')

        _logger.info('Details of Activity')

        for record in activity:
            _logger.info('Student : %s', record.student_id.name)
            _logger.info('Faculty : %s', record.faculty_id.name)
            _logger.info('Activity Type : %s', record.type_id.name)
            _logger.info('Description : %s', record.description)
            _logger.info('Date : %s', record.date)


class TestActivityType(TestActivityCommon):

    def test_case_1_activity_type(self):
        activity_type = self.op_activity_type.search([])
        if not activity_type:
            raise AssertionError('Error in data, please check for Activity type')

        _logger.info('Details of achievement_type')

        for category in activity_type:
            _logger.info('Activity : %s', category.name)


class TestStudentMigrateWizard(TestActivityCommon):

    def test_case_1_student_migrate_wizard(self):
        student_migrate = self.op_student_migrate_wizard.create({
            'course_from_id': self.env.ref('openeducat_core.op_course_2').id,
            'course_to_id': self.env.ref('openeducat_core.op_course_3').id,
            'batch_id': self.env.ref('openeducat_core.op_batch_2').id,
            'student_ids': [(6, 0, [self.env.ref('openeducat_core.op_student_1').id])],
        })

        student_migrate1 = self.op_student_migrate_wizard.create({
            'course_from_id': self.env.ref('openeducat_core.op_course_3').id,
            'course_to_id': self.env.ref('openeducat_core.op_course_2').id,
            'batch_id': self.env.ref('openeducat_core.op_batch_1').id,
            'student_ids': [(6, 0, [self.env.ref('openeducat_core.op_student_2').id])],
        })

        student_migrate.student_migrate_forward()
        student_migrate1.student_by_course()
