"""
Created on Sep 6, 2018

@author: Zuhair Hammadi
"""

import threading


from odoo import models, fields, api
from odoo.exceptions import AccessError

import logging

_logger = logging.getLogger(__name__)


class AuditDelete(models.TransientModel):
    _name = "audit.delete"
    _description = "audit.delete"

    @api.model
    def _models_ids_domain(self):
        cr = self._cr
        cr.execute("select distinct model_id from audit_log")
        res = cr.fetchall()
        models_ids = [model_id for model_id, in res]
        return [("id", "in", models_ids)]

    @api.model
    def _calc_record_count(self):
        # return self.env["audit.log"].sudo().search([], count=True)
        records = self.env["audit.log"].sudo().search([])
        return len(records)

    @api.model
    def _calc_table_size(self):
        cr = self._cr
        cr.execute(
            "select pg_size_pretty(sum(pg_total_relation_size(relid))) FROM pg_catalog.pg_statio_user_tables where relname in ('audit_log','audit_log_detail')"
        )
        (res,) = cr.fetchone()
        return res

    table_size = fields.Char("Table Size", default=_calc_table_size, readonly=True)

    record_count = fields.Integer(
        "Record Count", default=_calc_record_count, readonly=True
    )

    models_ids = fields.Many2many("ir.model", domain=_models_ids_domain)

    date = fields.Datetime("To Date")

    records_to_delete = fields.Integer(
        "Records to Delete", compute="_calc_records_to_delete"
    )

    domain = fields.Binary(compute="_calc_records_to_delete")

    type_ids = fields.Many2many("audit.type")

    @api.depends("models_ids", "date", "type_ids")
    def _calc_records_to_delete(self):
        for record in self:
            domain = []
            if record.models_ids:
                domain.append(("model_id", "in", record.models_ids.ids))
            if record.date:
                domain.append(("date", "<=", record.date))
            if record.type_ids:
                domain.append(("type", "in", record.mapped("type_ids.value")))
            record.records_to_delete = len(self.env["audit.log"].sudo().search(domain))
            # (self.env["audit.log"].sudo().search(domain, count=True)))
            record.domain = domain

    # def process(self):
    #     if not self.user_has_groups("eds_user_audit.group_audit_admin"):
    #         raise AccessError("Only Administrator")
    #
    #     cr = self._cr
    #     cr.autocommit(True)
    #
    #     query = self.env["audit.log"]._where_calc(self.domain)
    #     from_clause, where_clause, where_clause_params = query.get_sql()
    #
    #     sql = "delete from %s" % from_clause
    #
    #     if where_clause:
    #         sql = "%s where %s" % (sql, where_clause)
    #
    #     _logger.info(sql)
    #     _logger.info(where_clause_params)
    #
    #     cr.execute(sql, where_clause_params)
    #     _logger.info("Records Deleted %d" % cr.rowcount)
    #
    #     cr.execute("VACUUM audit_log")
    #     cr.execute("VACUUM audit_log_detail")
    def process(self):
        if not self.user_has_groups("eds_user_audit.group_audit_admin"):
            raise AccessError("Only Administrator")

        cr = self.env.cr

        try:
            query = self.env["audit.log"]._where_calc(self.domain)
            from_clause, where_clause, where_clause_params = query.get_sql()

            sql = "DELETE FROM %s" % from_clause

            if where_clause:
                sql = "%s WHERE %s" % (sql, where_clause)

            _logger.info(sql)
            _logger.info(where_clause_params)

            cr.execute(sql, where_clause_params)
            deleted_count = cr.rowcount
            _logger.info("Records Deleted %d" % deleted_count)

            # Commit the transaction after delete
            self.env.cr.commit()

            # Schedule VACUUM as a separate thread
            threading.Thread(target=self._vacuum_tables).start()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": f"{deleted_count} records have been deleted. VACUUM scheduled.",
                    "type": "success",
                },
            }

        except Exception as e:
            _logger.error("Error during audit log deletion: %s", str(e))
            raise

    @api.model
    def _vacuum_tables(self):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            try:
                new_cr.autocommit = True
                new_cr.execute("VACUUM audit_log")
                new_cr.execute("VACUUM audit_log_detail")
                _logger.info("VACUUM completed successfully")
            except Exception as e:
                _logger.error("Error during VACUUM: %s", str(e))
            finally:
                new_cr.close()
