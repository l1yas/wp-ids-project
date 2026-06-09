let logsData = [];
let currentSort = { key: "timestamp", dir: "desc" };

let attackChart = null;
let timeChart = null;

/* =========================
   TIMESTAMP NORMALIZATION
========================= */

function parseTimestamp(ts) {
    if (!ts) return null;

    let d = new Date(ts);
    if (!isNaN(d.getTime())) return d;

    // Apache format: 28/Apr/2026:12:13:30 +0000
    const m = ts.match(
        /(\d{2})\/(\w{3})\/(\d{4}):(\d{2}):(\d{2}):(\d{2})/
    );

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

/* =========================
   SORTING
========================= */

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

/* =========================
   TABLE RENDER
========================= */

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
        </tr>`;
    });

    document.getElementById("logs").innerHTML = html;
}

/* =========================
   STATS BUILD
========================= */

function buildAttackStats(data) {
    const c = {};
    data.forEach(e => {
        const k = e.attack || e.type || "unknown";
        c[k] = (c[k] || 0) + 1;
    });
    return c;
}

function buildTimeStats(data) {
    const c = {};

    data.forEach(e => {
        const t = new Date(e.timestamp || e.date);
        if (isNaN(t)) return;

        const key = t.toISOString().slice(0, 16); // minute
        c[key] = (c[key] || 0) + 1;
    });

    return c;
}

/* =========================
   CHARTS
========================= */

function renderAttackChart(data) {
    const stats = buildAttackStats(data);

    const labels = Object.keys(stats);
    const values = Object.values(stats);

    if (attackChart) attackChart.destroy();

    attackChart = new Chart(
        document.getElementById("attackChart"),
        {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Attacks",
                    data: values
                }]
            }
        }
    );
}

function renderTimeChart(data) {
    const stats = buildTimeStats(data);

    const labels = Object.keys(stats).slice(-20);
    const values = Object.values(stats).slice(-20);

    if (timeChart) timeChart.destroy();

    timeChart = new Chart(
        document.getElementById("timeChart"),
        {
            type: "line",
            data: {
                labels,
                datasets: [{
                    label: "Events/min",
                    data: values,
                    tension: 0.3
                }]
            }
        }
    );
}

/* =========================
   FETCH LOOP
========================= */

async function fetch_logs() {
    try {
        const res = await fetch("/events");
        const data = await res.json();

        logsData = data.map(e => ({
            ...e,
            _ts: toTimestamp(e.timestamp || e.date)
        }));

        const sorted = sortLogs(
            logsData,
            currentSort.key,
            currentSort.dir
        );

        renderTable(sorted);
        renderAttackChart(logsData);
        renderTimeChart(logsData);

    } catch (err) {
        console.error("Fetch error:", err);
    }
}

/* =========================
   SORT CONTROL
========================= */

function setSort(key) {
    if (currentSort.key === key) {
        currentSort.dir = currentSort.dir === "asc" ? "desc" : "asc";
    } else {
        currentSort.key = key;
        currentSort.dir = "desc";
    }

    const sorted = sortLogs(logsData, currentSort.key, currentSort.dir);
    renderTable(sorted);
}

/* =========================
   INIT
========================= */

fetch_logs();
setInterval(fetch_logs, 2000);