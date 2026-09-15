/** @odoo-module **/

import { RPCError } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";

patch(RPCError.prototype, {
    set data(errorData) {
        if (errorData && errorData.debug) {
            console.debug("RPC Debug:", errorData.debug);
        }
        this._data = errorData;
    },

    get data() {
        return this._data;
    }
});