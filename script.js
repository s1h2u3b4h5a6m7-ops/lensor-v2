const DATA_URL = `./data/nifty50.json?v=${Date.now()}`;

const els = {
  companyCount: document.getElementById("companyCount"),
  updatedAt: document.getElementById("updatedAt"),
  sourceLabel: document.getElementById("sourceLabel"),
  searchBox: document.getElementById("searchBox"),
  visibleRows: document.getElementById("visibleRows"),
  statusPill: document.getElementById("statusPill"),
  tableHeadRow: document.getElementById("tableHeadRow"),
  tableBody: document.getElementById("tableBody"),
};

const state = {
  rows: [],
  filteredRows: [],
  columns: [],
  sortKey: null,
  sortDir: "asc",
  query: "",
};

function formatCount(n) {
  const value = Number(n || 0);
  return new Intl.NumberFormat("en-IN").format(value);
}

function guessColumns(data) {
  if (Array.isArray(data.columns) && data.columns.length) return data.columns;
  if (Array.isArray(data.rows) && data.rows.length) return Object.keys(data.rows[0]);
  return [];
}

function normalizeText(value) {
  return String(value ?? "").toLowerCase().trim();
}

function rowMatchesQuery(row, query) {
  if (!query) return true;
  return Object.values(row).some((value) => normalizeText(value).includes(query));
}

function parseComparable(value) {
  const raw = String(value ?? "").trim();
  if (!raw) return { type: "text", value: "" };

  const numericCandidate = raw.replace(/[^0-9.-]/g, "");
  const num = Number(numericCandidate);
  if (!Number.isNaN(num) && numericCandidate !== "" && /[0-9]/.test(numericCandidate)) {
    return { type: "number", value: num };
  }
  return { type: "text", value: raw.toLowerCase() };
}

function compareRows(a, b, key, dir) {
  const av = parseComparable(a?.[key]);
  const bv = parseComparable(b?.[key]);

  let result = 0;
  if (av.type === "number" && bv.type === "number") {
    result = av.value - bv.value;
  } else {
    result = av.value.localeCompare(bv.value, undefined, { numeric: true, sensitivity: "base" });
  }

  return dir === "asc" ? result : -result;
}

function applyFiltersAndSort() {
  const query = normalizeText(els.searchBox.value);
  state.query = query;

  const base = state.rows.filter((row) => rowMatchesQuery(row, query));

  if (state.sortKey) {
    base.sort((a, b) => compareRows(a, b, state.sortKey, state.sortDir));
  }

  state.filteredRows = base;
  renderTable();
  renderMeta();
}

function renderMeta() {
  els.visibleRows.textContent = `${formatCount(state.filteredRows.length)} row${state.filteredRows.length === 1 ? "" : "s"}`;
  els.statusPill.textContent = state.filteredRows.length ? "Live table" : "No matching rows";
}

function renderCards(data) {
  els.companyCount.textContent = formatCount(data.count ?? state.rows.length);
  els.updatedAt.textContent = data.updated_ist || "Not yet synced";
  els.sourceLabel.textContent = "Official NSE";
}

function renderHead() {
  els.tableHeadRow.innerHTML = "";

  state.columns.forEach((column) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.className = "sortable";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "sort-btn";
    button.setAttribute("aria-label", `Sort by ${column}`);
    button.textContent = column;

    const indicator = document.createElement("span");
    indicator.className = "sort-indicator";
    indicator.textContent = state.sortKey === column ? (state.sortDir === "asc" ? "▲" : "▼") : "↕";

    button.appendChild(indicator);
    button.addEventListener("click", () => {
      if (state.sortKey === column) {
        state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
      } else {
        state.sortKey = column;
        state.sortDir = "asc";
      }
      applyFiltersAndSort();
      renderHead();
    });

    th.appendChild(button);
    els.tableHeadRow.appendChild(th);
  });
}

function renderTable() {
  els.tableBody.innerHTML = "";

  if (!state.filteredRows.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = Math.max(state.columns.length, 1);
    td.className = "empty";
    td.textContent = "No data to show.";
    tr.appendChild(td);
    els.tableBody.appendChild(tr);
    return;
  }

  const fragment = document.createDocumentFragment();

  state.filteredRows.forEach((row) => {
    const tr = document.createElement("tr");

    state.columns.forEach((column) => {
      const td = document.createElement("td");
      const value = row?.[column] ?? "";
      td.textContent = value;
      tr.appendChild(td);
    });

    fragment.appendChild(tr);
  });

  els.tableBody.appendChild(fragment);
}

async function loadData() {
  try {
    const response = await fetch(DATA_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    state.rows = Array.isArray(data.rows) ? data.rows : [];
    state.columns = guessColumns(data);
    state.filteredRows = [...state.rows];

    if (!state.columns.length && state.rows.length) {
      state.columns = Object.keys(state.rows[0]);
    }

    renderCards(data);
    renderHead();
    applyFiltersAndSort();
    els.statusPill.textContent = "Synced";
  } catch (error) {
    console.error(error);
    state.rows = [];
    state.columns = ["Message"];
    state.filteredRows = [{ Message: "Unable to load data/nifty50.json. Run the robot workflow first." }];
    renderCards({});
    renderHead();
    renderTable();
    els.statusPill.textContent = "Offline";
  }
}

els.searchBox.addEventListener("input", applyFiltersAndSort);

loadData();
