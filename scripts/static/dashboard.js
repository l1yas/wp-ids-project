let logsData = [];
let currentSort = { key: "timestamp", dir: "desc" };

let attackChart = null;
let dayChart = null;

function parseTimestamp(ts) {
    if (!ts) return null;

    const d = new Date(ts);
    if (!isNaN(d.getTime())) return d;

    const m = ts.match(/(\d{2})\/(\w{3})\/(\d{4}):(\d{2}):(\d{2}):(\d{2})/);

    if (m) {
        const [, day, mon, year, h, min, s] = m;

        const months = {
            Jan: 0, Feb: 1, Mar: 2, Apr: 3,
            May: 4, Jun: 5, Jul: 6, Aug: 7,
            Sep: 8, Oct: 9, Nov: 10, Dec: 11
        };

        return new Date(Date.UTC(year, months[mon], day, h, min, s));
    }

    return null;
}

function toTimestamp(ts) {
    const d = parseTimestamp(ts);
    return d ? d.getTime() : 0;
}

function formatTimestamp(ts) {
    const d = parseTimestamp(ts);
    if (!d) return "";
    return d.toISOString().replace("T", " ").split(".")[0];
}

function sortLogs(data, key, dir = "desc") {
    return [...data].sort((a, b) => {
        let x = a[key];
        let y = b[key];

        if (key === "timestamp" || key === "date") {
            x = toTimestamp(x);
            y = toTimestamp(y);
        }

        if (x < y) return dir === "asc" ? -1 : 1;
        if (x > y) return dir === "asc" ? 1 : -1;
        return 0;
    });
}

function renderTable(data) {
    let html = "";

    data.forEach(e => {
        html += `
        <tr>
            <td>${formatTimestamp(e.timestamp || e.date)}</td>
            <td>${e.subtype || ""}</td>
            <td>${e.attack || e.type || ""}</td>
            <td>${e.ip || ""}</td>
            <td>${e.username || ""}</td>
            <td>${e.severity || ""}</td>
        </tr>`;
    });

    document.getElementById("logs").innerHTML = html;
}

function buildAttackStats(data) {
    const c = {};

    data.forEach(e => {
        const k = (e.subtype || "unknown").toUpperCase();
        c[k] = (c[k] || 0) + 1;
    });

    return c;
}

function getColor(type) {
    const map = {
        "SQLI": "#ff3b30",
        "LFI": "#ff9500",
        "XSS": "#af52de",
        "COMMANDINJECTION": "#ff2d55",
        "FILEDISCLOSURE": "#5ac8fa",
        "WEBSHELL": "#ffcc00",
        "UNKNOWN": "#8e8e93"
    };

    return map[type] || "#8e8e93";
}

function renderAttackChart(data) {
    const stats = buildAttackStats(data);

    const labels = Object.keys(stats);
    const values = Object.values(stats);
    const colors = labels.map(getColor);

    if (attackChart) attackChart.destroy();

    attackChart = new Chart(document.getElementById("attackChart"), {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Attack types",
                data: values,
                backgroundColor: colors
            }]
        }
    });
}

function buildDayStats(data) {
    const c = {};

    data.forEach(e => {
        const t = parseTimestamp(e.timestamp || e.date);
        if (!t) return;

        const day = t.toISOString().slice(0, 10);
        c[day] = (c[day] || 0) + 1;
    });

    return c;
}

function renderDayChart(data) {
    const stats = buildDayStats(data);

    const sorted = Object.entries(stats)
        .sort((a, b) => new Date(a[0]) - new Date(b[0]));

    const labels = sorted.map(x => x[0]);
    const values = sorted.map(x => x[1]);

    if (dayChart) dayChart.destroy();

    dayChart = new Chart(document.getElementById("timeChart"), {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Attacks per day",
                data: values
            }]
        }
    });
}

function applyFilters(data) {
    const type = document.getElementById("typeFilter").value;
    const severity = document.getElementById("severityFilter").value;
    const search = document.getElementById("searchInput").value.toLowerCase();

    return data.filter(e => {
        const matchType = type === "all" || e.type === type;
        const matchSeverity = severity === "all" || String(e.severity) === severity;

        const matchSearch =
            !search ||
            (e.ip || "").toLowerCase().includes(search) ||
            (e.username || "").toLowerCase().includes(search) ||
            (e.subtype || "").toLowerCase().includes(search);

        return matchType && matchSeverity && matchSearch;
    });
}

async function fetch_logs() {
    try {
        const res = await fetch("/events");
        const data = await res.json();

        logsData = data.map(e => ({
            ...e,
            _ts: toTimestamp(e.timestamp || e.date)
        }));

        const sorted = sortLogs(logsData, currentSort.key, currentSort.dir);
        const filtered = applyFilters(sorted);

        renderTable(filtered);
        renderAttackChart(filtered);
        renderDayChart(filtered);

    } catch (err) {
        console.error("Fetch error:", err);
    }
}

function setSort(key) {
    if (currentSort.key === key) {
        currentSort.dir = currentSort.dir === "asc" ? "desc" : "asc";
    } else {
        currentSort.key = key;
        currentSort.dir = "desc";
    }

    const sorted = sortLogs(logsData, currentSort.key, currentSort.dir);
    renderTable(applyFilters(sorted));
}

fetch_logs();
setInterval(fetch_logs, 2000);