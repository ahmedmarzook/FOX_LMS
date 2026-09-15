from odoo import fields, models
from odoo.addons.mail.tools.discuss import Store


class DiscussChannelRtcSession(models.Model):
    _inherit = "discuss.channel.rtc.session"

    live_screen_visible = fields.Boolean(
        string="Screen Visible",
        default=True,
    )
    live_hand_raised = fields.Boolean(string="Hand Raised")
    live_emoji = fields.Char(string="Feedback Emoji", default="")
    live_badge_emoji = fields.Char(string="Badge Emoji", default="")
    live_attentive = fields.Boolean(string="Attentive", default=True)

    def _get_store_extra_fields(self):
        return [
            *super()._get_store_extra_fields(),
            "live_screen_visible",
            "live_hand_raised",
            "live_emoji",
            "live_badge_emoji",
            "live_attentive",
        ]

    def _update_and_broadcast(self, values):
        valid_custom_values = {
            "live_screen_visible",
            "live_hand_raised",
            "live_emoji",
            "live_badge_emoji",
            "live_attentive",
        }
        custom_values = {
            key: values[key]
            for key in valid_custom_values
            if key in values
        }
        standard_values = {
            key: value
            for key, value in values.items()
            if key not in valid_custom_values
        }
        if custom_values:
            self.write(custom_values)
        if standard_values:
            super()._update_and_broadcast(standard_values)
        elif custom_values:
            store = Store().add(
                self,
                extra_fields=self._get_store_extra_fields(),
            )
            self.channel_id._bus_send(
                "discuss.channel.rtc.session/update_and_broadcast",
                {
                    "data": store.get_result(),
                    "channelId": self.channel_id.id,
                },
            )

    def update_live_emoji(self, emoji):
        self.ensure_one()
        self._update_and_broadcast({
            "live_emoji": emoji or "",
            "live_badge_emoji": emoji or "",
        })
