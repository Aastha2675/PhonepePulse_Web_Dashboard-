// ---------------- GLOBAL STATE ----------------
let years = [];
let quarters = [];
let curr_year_idx = 0;
let select_year = null;
let select_quarter = null;
let select_category = "insurance"; // default
let select_state = "All India";

// ---------------- INIT ----------------
document.addEventListener("DOMContentLoaded", async () => {
    await get_time_filters();
    setupYearButtons();
    setupYearDropdown();
    setupQuarterButtons();
    setupDropdown();

    // ADD THESE TWO LINES HERE
    if (typeof populateTPStates === "function") populateTPStates();
    if (typeof render_tp_chart === "function") render_tp_chart();

    renderYearUI(); 
    renderQuarters();

    dropdownBtn.classList.add("insurance");
});

// ---------------- FETCH FILTERS ----------------
// Inside filter.js -> get_time_filters()
async function get_time_filters() {
    const res = await fetch("/api/filters");
    const data = await res.json();

    years = data.years.sort((a, b) => a - b);
    quarters = data.quarters;
    
    // Store the fetched states globally so render.js can see them
    window.all_states = data.states; 

    curr_year_idx = years.length - 1;
    select_year = years[curr_year_idx];

    populateYearDropdown(years);
    // Call the state population here too
    if (typeof populateTPStates === "function") populateTPStates();
}

// ---------------- DROP DOWN POPULATION ----------------
function populateYearDropdown(yearsList) {
  const tpYearSelect = document.getElementById("tp-year");
  if (!tpYearSelect) return;

  tpYearSelect.innerHTML = ""; // Clear existing hardcoded options
  yearsList.forEach((year) => {
    const opt = document.createElement("option");
    opt.value = year;
    opt.textContent = year;
    tpYearSelect.appendChild(opt);
  });
}

// ---------------- YEAR LOGIC ----------------
function setupYearButtons() {
  document.getElementById("prevYear").onclick = () => {
    if (curr_year_idx > 0) {
      curr_year_idx--;
      updateYearState();
    }
  };

  document.getElementById("nextYear").onclick = () => {
    if (curr_year_idx < years.length - 1) {
      curr_year_idx++;
      updateYearState();
    }
  };
}

// Listener for the <select id="tp-year">
function setupYearDropdown() {
  const tpYearSelect = document.getElementById("tp-year");
  if (!tpYearSelect) return;

  tpYearSelect.onchange = (e) => {
    const chosenYear = parseInt(e.target.value);
    // Update index based on selection to keep buttons in sync
    curr_year_idx = years.indexOf(chosenYear);
    updateYearState();
  };
}

function updateYearState() {
  select_year = years[curr_year_idx];
  renderYearUI();
  renderQuarters(); // Quarters might change availability (e.g. Q4 disabled)
}

function renderYearUI() {
  // Update the span text
  document.getElementById("yearText").innerText = select_year;
  
  // Update the dropdown value to match
  const tpYearSelect = document.getElementById("tp-year");
  if (tpYearSelect) tpYearSelect.value = select_year;
}

// ---------------- QUARTER LOGIC ----------------
function setupQuarterButtons() {
  document.querySelectorAll(".quarter-list button").forEach((btn) => {
    btn.onclick = () => {
      if (btn.disabled) return;

      select_quarter = btn.dataset.q;
      highlightQuarter();
      triggerDataFetch(select_state);
    };
  });
}

function renderQuarters() {
  const buttons = document.querySelectorAll(".quarter-list button");

  buttons.forEach((btn) => {
    btn.classList.remove("active");

    // Example logic: Disable Q4 for the most recent year if data isn't out yet
    if (select_year === Math.max(...years) && btn.dataset.q === "Q4") {
      btn.disabled = true;
      btn.style.opacity = 0.4;
    } else {
      btn.disabled = false;
      btn.style.opacity = 1;
    }
  });

  // AUTO SELECT latest enabled quarter
  const enabledButtons = [...buttons].filter((b) => !b.disabled);
  const lastBtn = enabledButtons[enabledButtons.length - 1];

  select_quarter = lastBtn.dataset.q;
  highlightQuarter();

  // AUTO FETCH DATA
  triggerDataFetch(select_state);
}

function highlightQuarter() {
  document.querySelectorAll(".quarter-list button").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.q === select_quarter);
  });
}

// ---------------- CENTRAL DATA FETCH ----------------
function triggerDataFetch(state) {
  if (!select_year || !select_quarter) return;

  select_state = state || "All India";

  console.log(
    "FETCHING →",
    select_category,
    select_year,
    select_quarter,
    select_state
  );

  // Note: Ensure render_summary is defined in render.js
  if (typeof render_summary === "function") {
    render_summary(
      select_category,
      select_year,
      select_quarter,
      select_state
    );
  }
}

// ---------------- DROPDOWN LOGIC (Insurance/Transaction) ----------------
const dropdownBtn = document.getElementById("dropdownBtn");
const dropdownMenu = document.getElementById("dropdownMenu");
const titleEl = document.getElementById("title");

function setupDropdown() {
  dropdownBtn.addEventListener("click", () => {
    dropdownMenu.style.display =
      dropdownMenu.style.display === "block" ? "none" : "block";
  });

  dropdownMenu.querySelectorAll(".dropdown-item").forEach((option) => {
    option.addEventListener("click", () => {
      select_category = option.dataset.value;

      if (select_category === "insurance") {
        dropdownBtn.innerText = "INSURANCE ▼";
        titleEl.innerText = "Insurance";
        // ... (rest of your text updates)
      } else {
        dropdownBtn.innerText = "TRANSACTION ▼";
        titleEl.innerText = "Transaction";
        // ... (rest of your text updates)
      }

      dropdownMenu.style.display = "none";
      triggerDataFetch(select_state);
    });
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".dropdown")) {
      dropdownMenu.style.display = "none";
    }
  });
}

// ------ NAVBAR FILTER (Map vs Top Performance) -------- //
document.addEventListener("DOMContentLoaded", () => {
  const pages = {
    map: document.getElementById("map-page"),
    top: document.getElementById("top-performance-page")
  };

  const navItems = document.querySelectorAll(".navbar nav span");

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      navItems.forEach(n => n.classList.remove("active"));
      item.classList.add("active");

      const text = item.innerText.toLowerCase();
      Object.values(pages).forEach(p => {
          if (p) p.classList.remove("active");
      });

      if (text.includes("map") && pages.map) {
        pages.map.classList.add("active");
      } else if (text.includes("top") && pages.top) {
        pages.top.classList.add("active");
      }
    });
  });
});