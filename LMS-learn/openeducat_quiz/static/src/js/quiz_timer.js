/** @odoo-module **/

/*
 * OpenEduCat Quiz timer - Odoo 19
 *
 * The old implementation duplicated the timer for different screen sizes,
 * parsed URLs by numeric indexes, and used localStorage.clear(), which could
 * remove unrelated website data. This version keeps the same DOM contract
 * while using pathname segments and only removes the quiz timer key.
 */

const TIMER_KEY = "openeducat_quiz_end_time";

function getPathSegments() {
    return window.location.pathname.split("/").filter(Boolean);
}

function isQuizRecordOrScore() {
    const segments = getPathSegments();
    return segments.includes("record") || segments.includes("score");
}

function isQuizAttempt() {
    return getPathSegments().includes("attempt");
}

function getCounterElement() {
    return document.querySelector("#divCounter") || document.querySelector("#divCounterone");
}

function getTimeInputs() {
    return {
        hours: Number.parseInt(document.querySelector("#time_spent_hr")?.value, 10) || 0,
        minutes: Number.parseInt(document.querySelector("#time_spent_minute")?.value, 10) || 0,
        seconds: Number.parseInt(document.querySelector("#time_spent_second")?.value, 10) || 0,
    };
}

function saveSpentTime() {
    const timeElement = document.querySelector("#all_time");
    const form = document.querySelector("#from_quiz_dynamic");

    if (!timeElement || !form) {
        return;
    }

    let input = form.querySelector("input[name='t_spent_time']");
    if (!input) {
        input = document.createElement("input");
        input.type = "hidden";
        input.name = "t_spent_time";
        form.appendChild(input);
    }
    input.value = timeElement.textContent || "";
}

function setupTimer() {
    const counterElement = getCounterElement();
    if (!counterElement || isQuizRecordOrScore()) {
        localStorage.removeItem(TIMER_KEY);
        return;
    }

    if (!isQuizAttempt()) {
        return;
    }

    const { hours, minutes, seconds } = getTimeInputs();
    const storedEnd = localStorage.getItem(TIMER_KEY);
    let endTime = storedEnd ? Number(storedEnd) : NaN;

    if (!Number.isFinite(endTime) || endTime <= Date.now()) {
        endTime =
            Date.now() +
            ((hours * 60 * 60) + (minutes * 60) + seconds) * 1000;
        localStorage.setItem(TIMER_KEY, String(endTime));
    }

    const submitExam = document.querySelector("#submit_exam");
    let intervalId;

    const update = () => {
        const remaining = Math.max(0, endTime - Date.now());
        const totalSeconds = Math.floor(remaining / 1000);

        const hoursLeft = Math.floor(totalSeconds / 3600);
        const minutesLeft = Math.floor((totalSeconds % 3600) / 60);
        const secondsLeft = totalSeconds % 60;

        const hoursText = String(hoursLeft).padStart(2, "0");
        const minutesText = String(minutesLeft).padStart(2, "0");
        const secondsText = String(secondsLeft).padStart(2, "0");

        if (remaining <= 0) {
            if (intervalId) {
                clearInterval(intervalId);
            }
            localStorage.removeItem(TIMER_KEY);
            counterElement.textContent = "Countdown finished!";

            if (submitExam?.getAttribute("href")) {
                window.location.href = submitExam.getAttribute("href");
            }
            return;
        }

        const value = `${hoursText}:${minutesText}:${secondsText}`;
        const allTime = document.querySelector("#all_time");
        if (allTime) {
            allTime.textContent = value;
        }

        const ids = [
            ["#spanHrone", hoursText],
            ["#spanMtone", minutesText],
            ["#spanSnone", secondsText],
            ["#spanHr", hoursText],
            ["#spanMt", minutesText],
            ["#spanSn", secondsText],
        ];

        for (const [selector, text] of ids) {
            const element = document.querySelector(selector);
            if (element) {
                element.textContent = text;
            }
        }
    };

    update();
    intervalId = window.setInterval(update, 1000);

    document.querySelectorAll(".quiz_finish").forEach((button) => {
        button.addEventListener("click", saveSpentTime);
    });

    document.querySelector("#prev_timer")?.addEventListener("click", (event) => {
        event.preventDefault();
        saveSpentTime();

        const href = event.currentTarget.getAttribute("href");
        const timeElement = document.querySelector("#all_time");
        if (href) {
            const separator = href.includes("?") ? "&" : "?";
            const spentTime = encodeURIComponent(timeElement?.textContent || "");
            window.location.href = `${href}${separator}t_spent_time=${spentTime}`;
        }
    });

    window.addEventListener("beforeunload", () => {
        if (intervalId) {
            clearInterval(intervalId);
        }
    }, { once: true });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupTimer, { once: true });
} else {
    setupTimer();
}
