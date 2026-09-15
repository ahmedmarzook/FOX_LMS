odoo.define('validation.CrashManager', function (require) {
"use strict";

var CrashManager = require('web.CrashManager').CrashManager;

CrashManager.include({
    /**
     * @override
     */
    rpc_error: function (error) {
        if (error.data && error.data.ConfirmWarning) {
            
        } else {
            this._super.apply(this, arguments);
        }
    },
});

});
