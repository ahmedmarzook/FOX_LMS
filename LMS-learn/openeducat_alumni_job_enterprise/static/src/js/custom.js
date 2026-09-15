/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function fillStates(select, states, selectedId = null) {
    select.replaceChildren();

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select State";
    select.appendChild(placeholder);

    for (const state of states) {
        const option = document.createElement("option");
        option.value = String(state.id);
        option.textContent = state.name;
        option.selected = selectedId && String(state.id) === String(selectedId);
        select.appendChild(option);
    }
}

document.addEventListener("change", async (event) => {
    const countrySelect = event.target.closest("#country_dropdown");
    if (!countrySelect) {
        return;
    }

    const form = countrySelect.closest("form") || document;
    const stateSelect = form.querySelector("#states_on_country");
    if (!stateSelect) {
        return;
    }

    const countryId = Number(countrySelect.value);
    if (!countryId) {
        fillStates(stateSelect, []);
        return;
    }

    try {
        const data = await rpc("/get/country_data", {
            country_id: countryId,
        });
        fillStates(stateSelect, data.state_list || []);
    } catch (error) {
        console.error("Unable to load states", error);
        fillStates(stateSelect, []);
    }
});
