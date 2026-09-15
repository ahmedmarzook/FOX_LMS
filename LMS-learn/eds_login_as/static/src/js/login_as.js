import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { session } from "@web/session";
import { user } from "@web/core/user";

export class LoginAsSystrayItem extends Component {
    static props = ["*"];
    setup() {
        this.action = useService("action");
        // `@web/core/user` destructures is_system/uid/etc. out of `session` at
        // module-load time and deletes them from it (single-source-of-truth) —
        // by the time this component reads it, `session.is_system` is always
        // undefined. `session.impersonate` isn't part of that deleted set (it's
        // our own custom ir_http field), so it still reads fine from `session`.
        this.session = session;
        this.user = user;
        document.body.classList.toggle("o_impersonating", !!session.impersonate);
    }

    async onClick() {
        if (session.impersonate) {
            window.location.href = "/web/login_back";
        } else {
            await this.action.doAction('eds_login_as.act_login_as', {
                additionalContext: { active_id: false },
            });
        }
    }
}

LoginAsSystrayItem.template = 'eds_login_as.LoginAsSystrayItem';

registry.category("systray").add(
    "login_as",
    { Component: LoginAsSystrayItem },
    { sequence: 99 }
);
