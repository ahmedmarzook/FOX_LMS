/**
 * date_field_patch.js
 * Always show full date (including year) in date/datetime fields.
 *
 * By default Odoo omits the year when the date is in the current year
 * (toLocaleDateString removes format.year). We patch DateTimeField to
 * always use the numeric format, which relies on localization.dateFormat
 * and always includes the year.
 */

import { patch } from "@web/core/utils/patch";
import { DateTimeField } from "@web/views/fields/datetime/datetime_field";

patch(DateTimeField.prototype, {
    /**
     * Override to always include year in the formatted value.
     * The `numeric` flag forces use of localization.dateFormat (e.g. dd/MM/yyyy)
     * instead of toLocaleDateString which drops the year for current-year dates.
     */
    getFormattedValue(valueIndex, numeric = true) {
        return super.getFormattedValue(valueIndex, numeric);
    },
});
