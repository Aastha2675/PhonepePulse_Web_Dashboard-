// ---------- Insurance and Transaction Summary ---------- //
async function render_summary(type, year, quarter, state) {
  try {
    let data;

    // Fetch data based on selected category
    if (type === "insurance") {
      data = await fetch_insurance_summary(year, quarter, state);
    } else {
      data = await fetch_transaction_summary(year, quarter, state);
    }

    const totalLabel = document.getElementById("total-label");
    const totalValue = document.getElementById("total");
    const txnCategoriesDiv = document.getElementById("txn-categories");

    // 1. Handle Visibility & Main Cards
    if (type === "transaction") {
      // For Transaction: Change "Total Policies" to "Total Transactions"
      totalLabel.innerText = "Total Transactions";
      totalValue.innerText = (data.total_count ?? 0).toLocaleString();
    } else {
      // For Insurance: Reset to "Total Policies"
      totalLabel.innerText = "Total Policies";
      totalValue.innerText = (data.total_policies ?? 0).toLocaleString();
    }

    // 2. Common Fields (Premium/Amount and Average)
    // Converts to Crores for readability
    const mainAmount = data.total_premium ?? data.total_amount ?? 0;
    document.getElementById("premium").innerText = `₹ ${(mainAmount / 1e7).toFixed(2)} Cr`;

    const avgValue = data.avg_premium ?? data.avg_payment_value ?? 0;
    document.getElementById("avg").innerText = `₹ ${Math.round(avgValue).toLocaleString()}`;

    // 3. Transaction Categories List (Dynamic)
    txnCategoriesDiv.innerHTML = ""; // Clear old categories

    if (type === "transaction" && data.categories) {
      const heading = document.createElement("h2");
      heading.className = "section-heading";
      heading.innerText = "No. of Transactions per Category";
      txnCategoriesDiv.appendChild(heading);

      data.categories.forEach(cat => {
        const row = document.createElement("div");
        row.className = "category-row";
        row.innerHTML = `
          <span>${cat.name}</span>
          <span class="category-count">${cat.count.toLocaleString()}</span>
        `;
        txnCategoriesDiv.appendChild(row);
      });
    }

    // 4. Update the Top 10 List (Top Performance Page)
    if (typeof renderTop10List === "function") {
      renderTop10List(year);
    }

  } catch (err) {
    console.error("Render summary error:", err);
    setEmpty();
  }
}


// ---------- Top 10 States Ranking ---------- //
async function renderTop10List(year) {
  const listContainer = document.getElementById("top10-list");
  const top10Heading = document.querySelector(".tp-right h3");
  
  if (!listContainer) return;

  // Update dynamic heading for Top 10
  if (top10Heading) {
    top10Heading.innerText = `Top 10 States in year ${year} (in Cr.)`;
  }

  try {
    const response = await fetch_top_10_states(year);
    listContainer.innerHTML = ""; 

    if (response.has_data) {
      response.data.forEach((item, index) => {
        const li = document.createElement("li");
        const amountCr = (item.total_amount / 1e7).toFixed(2);
        
        li.innerHTML = `
          <div class="rank-item">
            <span class="rank-number">#${index + 1}</span>
            <span class="state-name">${item.state_name}</span>
            <span class="state-amount">₹${amountCr}</span>
          </div>
        `;
        listContainer.appendChild(li);
      });
    } else {
      listContainer.innerHTML = "<p class='no-data'>No data available for this year</p>";
    }
  } catch (err) {
    console.error("Error rendering Top 10:", err);
  }
}

function setEmpty() {
  document.getElementById("total").innerText = "--";
  document.getElementById("premium").innerText = "--";
  document.getElementById("avg").innerText = "--";
  document.getElementById("txn-categories").innerHTML = "";
}


let tpChartInstance = null; // Global variable to store the chart instance

// Function to populate the State Dropdown
function populateTPStates() {
    const stateSelect = document.getElementById("tp-state");
    if (!stateSelect) return;

    stateSelect.innerHTML = ""; // Clear existing

    // Add "India" or "All India" as first option
    const defaultOpt = document.createElement("option");
    defaultOpt.value = "India";
    defaultOpt.innerText = "All India";
    stateSelect.appendChild(defaultOpt);

    // Use the global window.all_states we just set in filter.js
    if (window.all_states) {
        window.all_states.forEach(state => {
            if (state !== "India") { // Avoid duplicates
                const opt = document.createElement("option");
                opt.value = state;
                opt.innerText = state;
                stateSelect.appendChild(opt);
            }
        });
    }
}

async function render_tp_chart() {
    const year = document.getElementById("tp-year").value;
    const state = document.getElementById("tp-state").value;

    try {
        const response = await fetch_txn_categories(year, state);
        
        // Use a dark color for text if your chart background is light
        const textColor = '#2d143f'; 

        const quarters = ["Q1", "Q2", "Q3", "Q4"];
        const yLabels = quarters.map(q => `${year} ${q}`);
        const categories = [...new Set(response.data.map(d => d.txn_type_name))];
        
        const datasets = categories.map((cat, index) => {
            const colors = ['#5a259f', '#7b1fa2', '#d46cff', '#4deeea', '#38e1ff'];
            return {
                label: cat,
                data: quarters.map(q => {
                    const found = response.data.find(d => d.quarter == q.replace('Q', '') && d.txn_type_name === cat);
                    return found ? found.txn_amount / 1e7 : 0; 
                }),
                backgroundColor: colors[index % colors.length]
            };
        });

        const ctx = document.getElementById('transactionBarChart').getContext('2d');
        if (tpChartInstance) tpChartInstance.destroy();

        tpChartInstance = new Chart(ctx, {
            type: 'bar',
            data: { labels: yLabels, datasets: datasets },
            options: {
                indexAxis: 'y', // This makes it horizontal
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { 
                        ticks: { color: textColor }, // Changed from #fff
                        title: { display: true, text: 'Amount (₹ Cr)', color: textColor }
                    },
                    y: { 
                        ticks: { color: textColor } // Changed from #fff
                    }
                },
                plugins: {
                    legend: { 
                        display: true,
                        labels: { color: textColor } // Changed from #fff
                    }
                }
            }
        });
    } catch (err) {
        console.error("Chart Render Error:", err);
    }
}

// Event Listeners for filters
document.getElementById("tp-year").addEventListener("change", render_tp_chart);
document.getElementById("tp-state").addEventListener("change", render_tp_chart);

// Initial Call
populateTPStates();