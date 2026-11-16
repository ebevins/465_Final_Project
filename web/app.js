const byId = (id) => document.getElementById(id);
const money = (value) => new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(Number(value || 0));

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("The local server returned an unreadable response.");
  }
  if (!response.ok) throw new Error(payload.error || "The request could not be completed.");
  return payload;
}

function showMessage(message, isError = false) {
  const notice = byId("global-message");
  notice.textContent = message;
  notice.classList.toggle("error", isError);
  notice.classList.remove("hidden");
  notice.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function clearMessage() {
  byId("global-message").classList.add("hidden");
}

function showTab(name) {
  document.querySelectorAll(".tab").forEach((tab) => {
    const selected = tab.dataset.tab === name;
    tab.classList.toggle("active", selected);
    tab.setAttribute("aria-selected", selected ? "true" : "false");
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    const selected = panel.id === `panel-${name}`;
    panel.classList.toggle("active", selected);
    panel.hidden = !selected;
  });
  clearMessage();
}

async function loadCards() {
  const form = new FormData(byId("search-form"));
  const query = new URLSearchParams({
    player: form.get("player") || "",
    sport: form.get("sport") || "",
    team: form.get("team") || "",
    status: form.get("status") || "",
  });
  const cards = await request(`/api/cards?${query}`);
  byId("card-count").textContent = `${cards.length} ${cards.length === 1 ? "card" : "cards"}`;
  const body = byId("cards-body");
  if (!cards.length) {
    body.innerHTML = '<tr><td colspan="9" class="empty-cell">No matching cards found.</td></tr>';
    return;
  }
  body.innerHTML = cards.map((card) => {
    const statusClass = String(card.Status || "").toLowerCase();
    return `<tr>
      <td>${card.CardID}</td>
      <td class="player-cell">${escapeHtml(card.PlayerName)}</td>
      <td>${escapeHtml(card.Sport)}</td>
      <td>${escapeHtml(card.Team || "—")}</td>
      <td>${card.CardYear}</td>
      <td>${escapeHtml([card.Brand, card.CardSet].filter(Boolean).join(" · "))}</td>
      <td>${card.Grade == null ? "—" : escapeHtml(card.Grade)}</td>
      <td><span class="status-badge ${statusClass}">${escapeHtml(card.Status)}</span></td>
      <td><button class="row-button" type="button" data-view-card="${card.CardID}">Details</button></td>
    </tr>`;
  }).join("");
}

async function loadDetails(cardId) {
  const id = String(cardId || "").trim();
  if (!/^\d+$/.test(id) || Number(id) < 1) throw new Error("Enter a valid CardID.");
  const card = await request(`/api/card?id=${encodeURIComponent(id)}`);
  const fields = [
    ["Card ID", card.CardID], ["Player", card.PlayerName], ["Sport", card.Sport],
    ["Team", card.Team], ["Year", card.CardYear], ["Brand", card.Brand],
    ["Set", card.CardSet], ["Card number", card.CardNumber], ["Description", card.Description],
    ["Condition", card.RawGraded], ["Grading company", card.GradingCompany], ["Grade", card.Grade],
    ["Serial number", card.SerialNumber], ["Status", card.Status],
    ["Purchase price", card.PurchasePrice == null ? null : money(card.PurchasePrice)],
    ["Purchase date", card.PurchaseDate], ["Seller", card.SellerName],
    ["Sale price", card.SalePrice == null ? null : money(card.SalePrice)],
    ["Sale date", card.SaleDate], ["Buyer", card.BuyerName],
  ];
  byId("details-content").classList.remove("muted-card");
  byId("details-content").innerHTML = fields.map(([label, value]) =>
    `<div class="detail-item"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value ?? "Not recorded")}</strong></div>`
  ).join("");
  byId("details-form").elements.card_id.value = id;
  return card;
}

async function loadCatalogs() {
  const catalogs = await request("/api/catalogs");
  const sellerSelect = byId("seller-select");
  sellerSelect.innerHTML = '<option value="">Choose a seller</option>' + catalogs.sellers.map((seller) =>
    `<option value="${seller.SellerID}">${escapeHtml(seller.FirstName)} ${escapeHtml(seller.LastName)} (#${seller.SellerID})</option>`
  ).join("");
  const buyerSelect = byId("buyer-select");
  buyerSelect.innerHTML = '<option value="">Choose a buyer</option>' + catalogs.buyers.map((buyer) =>
    `<option value="${buyer.BuyerID}">${escapeHtml(buyer.FirstName)} ${escapeHtml(buyer.LastName)} (#${buyer.BuyerID})</option>`
  ).join("");
  const cardSelect = byId("sale-card-select");
  cardSelect.innerHTML = '<option value="">Choose an active card</option>' + catalogs.active_cards.map((card) =>
    `<option value="${card.CardID}">#${card.CardID} · ${escapeHtml(card.PlayerName)} — ${escapeHtml(card.Sport)}</option>`
  ).join("");
}

async function loadReport() {
  const report = await request("/api/summary");
  const totals = report.totals;
  byId("metric-active").textContent = totals.active_count;
  byId("metric-cost").textContent = money(totals.inventory_cost);
  byId("metric-average-cost").textContent = money(totals.average_cost);
  byId("metric-sold").textContent = totals.sold_count;
  byId("metric-revenue").textContent = money(totals.revenue);
  byId("metric-average-sale").textContent = money(totals.average_sale);
  byId("sports-body").innerHTML = report.sports.length
    ? report.sports.map((row) => `<tr><td>${escapeHtml(row.Sport)}</td><td>${row.CardCount}</td></tr>`).join("")
    : '<tr><td colspan="2" class="empty-cell">No cards found.</td></tr>';
}

async function refreshAll() {
  clearMessage();
  try {
    await Promise.all([loadCards(), loadCatalogs(), loadReport()]);
    byId("connection-status").textContent = "Connected to sports_cards.db";
    document.querySelector(".connection-dot").classList.add("connected");
  } catch (error) {
    byId("connection-status").textContent = "Database unavailable";
    document.querySelector(".connection-dot").classList.remove("connected");
    showMessage(error.message, true);
  }
}

function formObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function submitJson(url, payload) {
  return request(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

function setLocalDate(input) {
  const today = new Date();
  const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  input.value = localDate;
}

document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => showTab(tab.dataset.tab)));
byId("refresh-all").addEventListener("click", refreshAll);
byId("refresh-report").addEventListener("click", async () => {
  try { await loadReport(); showMessage("Report refreshed."); }
  catch (error) { showMessage(error.message, true); }
});
byId("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try { await loadCards(); clearMessage(); }
  catch (error) { showMessage(error.message, true); }
});
byId("clear-search").addEventListener("click", async () => {
  byId("search-form").reset();
  try { await loadCards(); clearMessage(); }
  catch (error) { showMessage(error.message, true); }
});
byId("cards-body").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-view-card]");
  if (!button) return;
  try {
    showTab("details");
    await loadDetails(button.dataset.viewCard);
  } catch (error) { showMessage(error.message, true); }
});
byId("details-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try { await loadDetails(event.currentTarget.elements.card_id.value); clearMessage(); }
  catch (error) { showMessage(error.message, true); }
});

byId("condition-select").addEventListener("change", (event) => {
  const graded = event.target.value === "Graded";
  ["grading-company-wrap", "grade-wrap"].forEach((id) => byId(id).classList.toggle("disabled-field", !graded));
  const form = byId("purchase-form");
  form.elements.grading_company.disabled = !graded;
  form.elements.grade.disabled = !graded;
  form.elements.grading_company.required = graded;
  form.elements.grade.required = graded;
  if (!graded) {
    form.elements.grading_company.value = "";
    form.elements.grade.value = "";
  }
});
byId("purchase-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = formObject(form);
  payload.seller_id = Number(payload.seller_id);
  payload.year = Number(payload.year);
  payload.purchase_price = Number(payload.purchase_price);
  if (payload.grade !== "") payload.grade = Number(payload.grade);
  try {
    const result = await submitJson("/api/purchases", payload);
    form.reset();
    setLocalDate(form.elements.purchase_date);
    byId("condition-select").dispatchEvent(new Event("change"));
    await refreshAll();
    showMessage(`${result.message} CardID ${result.card_id}; PurchaseID ${result.purchase_id}.`);
  } catch (error) { showMessage(error.message, true); }
});

byId("update-field").addEventListener("change", (event) => {
  const isStatus = event.target.value === "Status";
  byId("update-value-wrap").classList.toggle("hidden", isStatus);
  byId("update-status-wrap").classList.toggle("hidden", !isStatus);
  byId("update-value").required = false;
});
byId("update-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const field = form.elements.field.value;
  const value = field === "Status" ? byId("update-status").value : byId("update-value").value;
  try {
    const result = await submitJson("/api/cards/update", {
      card_id: Number(form.elements.card_id.value), field, value,
    });
    await refreshAll();
    showMessage(result.message);
  } catch (error) { showMessage(error.message, true); }
});

byId("sale-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = formObject(form);
  payload.card_id = Number(payload.card_id);
  payload.buyer_id = Number(payload.buyer_id);
  payload.sale_price = Number(payload.sale_price);
  payload.fees = Number(payload.fees || 0);
  payload.shipping_cost = Number(payload.shipping_cost || 0);
  const selected = form.elements.card_id.selectedOptions[0]?.textContent || "this card";
  if (!window.confirm(`Record the sale of ${selected}?`)) return;
  try {
    const result = await submitJson("/api/sales", payload);
    form.reset();
    setLocalDate(form.elements.sale_date);
    form.elements.fees.value = "0";
    form.elements.shipping_cost.value = "0";
    await refreshAll();
    showMessage(`${result.message} SaleID ${result.sale_id}.`);
  } catch (error) { showMessage(error.message, true); }
});

setLocalDate(byId("purchase-form").elements.purchase_date);
setLocalDate(byId("sale-form").elements.sale_date);
byId("update-field").dispatchEvent(new Event("change"));
refreshAll();
