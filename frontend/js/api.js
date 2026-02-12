
// API request for insurance summary
async function fetch_insurance_summary(year, quarter, state = "All India") {
  const params = new URLSearchParams({
    year: year,
    quarter: quarter,
    state: state
  });

  const res = await fetch(`/insurance/summary?${params}`);
  if (!res.ok) throw new Error("Insurance API failed");
  return await res.json();
}


// API request for transaction summary
async function fetch_transaction_summary(year, quarter, state = "All India") {
  const params = new URLSearchParams({
    year: year,
    quarter: quarter,
    state: state
  });

  const res = await fetch(`/transaction/summary?${params}`);
  if (!res.ok) throw new Error("Transaction API failed");
  return await res.json();
}


// API for fecthing top 10 states per year
async function fetch_top_10_states(year) {
    const res = await fetch(`/api/top10/states?year=${year}`);
    if (!res.ok) throw new Error("Top 10 API failed");
    return await res.json();
}

async function fetch_txn_categories(year, state) {
    const res = await fetch(`/api/transaction/category?year=${year}&state=${state}`);
    if (!res.ok) throw new Error("Category API failed");
    return await res.json();
}
