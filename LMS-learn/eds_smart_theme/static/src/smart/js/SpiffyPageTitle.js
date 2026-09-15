/** @odoo-module **/

// # Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
// # See LICENSE file for full copyright and licensing details.

import { rpc as jsonrpc } from "@web/core/network/rpc";
import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(WebClient.prototype, {
    setup() {
        super.setup();
        var self = this
        jsonrpc('/get/tab/title/',{}).then(function(rec) {
            var new_title = rec
            self.title.setParts({ zopenerp: new_title })
        })
    },
});