"""
Created on Jan 10, 2022

@author: Zuhair Hammadi
"""

from odoo import models, api, fields


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def systray_get_activities_separation(self):
        today = fields.Date.context_today(self)
        user_id = self.env.uid

        activities = self.env["mail.activity"].search_read(
            [("user_id", "=", user_id)],
            ["res_model", "date_deadline", "res_model_id", "res_type"],
        )

        user_activities = {}
        models = set()

        for activity in activities:
            model = activity["res_model"]
            models.add(model)

            if activity["date_deadline"]:
                days_diff = (today - activity["date_deadline"]).days
                if days_diff == 0:
                    state = "today"
                elif days_diff > 0:
                    state = "overdue"
                else:
                    state = "planned"
            else:
                state = "planned"

            menu_line = self.env["mail.activity.menu.line"].search(
                [
                    (
                        "model_id",
                        "=",
                        (
                            activity["res_model_id"][0]
                            if isinstance(activity["res_model_id"], tuple)
                            else activity["res_model_id"]
                        ),
                    ),
                    ("name", "=", activity["res_type"]),
                ],
                limit=1,
            )

            if not menu_line:
                continue

            key = (model, menu_line.id)

            if key not in user_activities:
                user_activities[key] = {
                    "name": menu_line.name,
                    "model": model,
                    "type": "activity",
                    "view_type": "list",
                    "total_count": 0,
                    "today_count": 0,
                    "overdue_count": 0,
                    "planned_count": 0,
                    "action_id": menu_line.action_id.id,
                    "main_menu_id": menu_line.main_menu_id.id,
                }

                if menu_line.icon:
                    user_activities[key]["icon"] = "/web/image/%s/%d/icon" % (
                        menu_line._name,
                        menu_line.id,
                    )
                elif menu_line.main_menu_id.web_icon_data:
                    user_activities[key]["icon"] = "/web/image/%s/%d/web_icon_data" % (
                        menu_line.main_menu_id._name,
                        menu_line.main_menu_id.id,
                    )

            user_activities[key]["%s_count" % state] += 1
            if state in ("today", "overdue"):
                user_activities[key]["total_count"] += 1

            user_activities[key]["actions"] = [
                {"icon": "fa-clock-o", "name": "Summary"}
            ]

        return list(user_activities.values()), models

    @api.model
    def systray_get_activities(self):
        activities = super(Users, self).systray_get_activities()
        (
            separation_activities,
            separation_models,
        ) = self.systray_get_activities_separation()

        res = []
        for activity in activities:
            found = False
            for separation_activity in separation_activities:
                if activity["model"] == separation_activity["model"]:
                    found = True
                    break
            if not found:
                res.append(activity)

        res.extend(separation_activities)

        return res
