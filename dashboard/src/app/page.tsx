"use client";

import { useState, useEffect } from "react";
import styles from "./page.module.css";

// ── Type Definitions ────────────────────────────────────────────────────────

interface Alert {
  restaurant_id: number;
  restaurant_name: string;
  contact_email: string;
  ingredient: string;
  first_price: number;
  last_price: number;
  pct_increase: number;
  weeks_observed: number;
}

interface RunResponse {
  status: string;
  alerts_found: number;
  alerts: Alert[];
  email_draft: string;
  notification_sent: boolean;
}

interface PriceRow {
  restaurant_name: string;
  contact_email: string;
  date: string;
  ingredient: string;
  unit_price: number;
}

const API_BASE = "http://localhost:8000";

// ── Component ───────────────────────────────────────────────────────────────

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<RunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Prices state
  const [prices, setPrices] = useState<PriceRow[]>([]);
  const [pricesLoading, setPricesLoading] = useState(true);

  // Add Invoice form state
  const [formIngredient, setFormIngredient] = useState("");
  const [formPrice, setFormPrice] = useState("");
  const [formDate, setFormDate] = useState("");
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  // ── Fetch latest prices ─────────────────────────────────────────────────

  const fetchPrices = async () => {
    setPricesLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/prices`);
      const json = await res.json();
      setPrices(json.prices || []);
    } catch {
      console.error("Could not fetch prices");
    } finally {
      setPricesLoading(false);
    }
  };

  useEffect(() => {
    fetchPrices();
  }, []);

  // ── Add invoice ─────────────────────────────────────────────────────────

  const handleAddInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitting(true);
    setFormSuccess(null);

    try {
      const res = await fetch(`${API_BASE}/api/invoice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ingredient: formIngredient,
          unit_price: parseFloat(formPrice),
          date: formDate || undefined,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to add invoice");
      }

      const result = await res.json();
      setFormSuccess(
        `✅ Added ${result.ingredient} at ${result.unit_price.toFixed(2)}€/kg for ${result.date}`
      );
      setFormIngredient("");
      setFormPrice("");
      setFormDate("");

      // Refresh prices table
      await fetchPrices();
    } catch (err: any) {
      setFormSuccess(`❌ ${err.message}`);
    } finally {
      setFormSubmitting(false);
    }
  };

  // ── Run agent ───────────────────────────────────────────────────────────

  const triggerAgent = async () => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const res = await fetch(`${API_BASE}/api/run`, { method: "POST" });

      if (!res.ok) {
        throw new Error(`API returned status: ${res.status}`);
      }

      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "Something went wrong connecting to the agent.");
    } finally {
      setLoading(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className={styles.container}>
      {/* HEADER */}
      <header className={styles.header}>
        <div className={styles.title}>
          Company<span>Flow</span>
        </div>
        <div style={{ fontSize: "0.9rem", color: "#a1a1aa" }}>
          Internal Ops Intelligence Dashboard
        </div>
      </header>

      {/* MAIN LAYOUT */}
      <main className={styles.main}>
        {!data && (
          <div className={styles.initialLanding}>
            <h1 className={styles.initialTitle}>Operations Analysis</h1>
            <p className={styles.initialSubtitle}>
              Review current ingredient prices, add new data, and run the intelligence agent.
            </p>

            {/* ── PRICES TABLE ────────────────────────────────────────── */}
            <div className={styles.pricesSection}>
              <h2 className={styles.pricesSectionTitle}>
                Latest Ingredient Prices — Restaurante Paco
              </h2>
              {pricesLoading ? (
                <p className={styles.statusMessage}>Loading prices...</p>
              ) : prices.length === 0 ? (
                <p className={styles.statusMessage}>No price data found. Run seed_db.py first.</p>
              ) : (
                <table className={styles.pricesTable}>
                  <thead>
                    <tr>
                      <th>Ingredient</th>
                      <th>Price (€/kg)</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {prices.map((p, idx) => (
                      <tr key={idx}>
                        <td>{p.ingredient}</td>
                        <td className={styles.priceCell}>
                          {p.unit_price.toFixed(2)} €
                        </td>
                        <td className={styles.dateCell}>{p.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* ── ADD INVOICE FORM ────────────────────────────────────── */}
            <div className={styles.addInvoiceSection}>
              <h2 className={styles.pricesSectionTitle}>Add New Invoice Entry</h2>
              <form onSubmit={handleAddInvoice} className={styles.addForm}>
                <div className={styles.formRow}>
                  <label className={styles.formLabel}>
                    Ingredient
                    <select
                      value={formIngredient}
                      onChange={(e) => setFormIngredient(e.target.value)}
                      required
                      className={styles.formSelect}
                    >
                      <option value="">Select...</option>
                      <option value="Tomates">Tomates</option>
                      <option value="Aceite de Oliva">Aceite de Oliva</option>
                      <option value="Pollo">Pollo</option>
                      <option value="Arroz">Arroz</option>
                      <option value="Cebollas">Cebollas</option>
                    </select>
                  </label>

                  <label className={styles.formLabel}>
                    Price (€/kg)
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={formPrice}
                      onChange={(e) => setFormPrice(e.target.value)}
                      required
                      placeholder="e.g. 15.00"
                      className={styles.formInput}
                    />
                  </label>

                  <label className={styles.formLabel}>
                    Date (optional)
                    <input
                      type="date"
                      value={formDate}
                      onChange={(e) => setFormDate(e.target.value)}
                      className={styles.formInput}
                    />
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={formSubmitting}
                  className={styles.addButton}
                >
                  {formSubmitting ? "Adding..." : "Add Invoice Entry"}
                </button>
              </form>
              {formSuccess && (
                <p
                  className={styles.formFeedback}
                  style={{
                    color: formSuccess.startsWith("✅")
                      ? "var(--success)"
                      : "var(--error)",
                  }}
                >
                  {formSuccess}
                </p>
              )}
            </div>

            {/* ── RUN AGENT BUTTON ────────────────────────────────────── */}
            <button
              onClick={triggerAgent}
              disabled={loading}
              className={`${styles.runButton} ${styles.runButtonLarge}`}
            >
              {loading
                ? "Agent is investigating..."
                : "Run Intelligence Agent 🤖"}
            </button>
            {loading && (
              <p className={styles.statusMessage} style={{ marginTop: "0.5rem" }}>
                Scanning database, querying strategy manual via RAG, and
                drafting emails with Llama 3...
              </p>
            )}
            {error && (
              <p style={{ color: "var(--error)", marginTop: "0.5rem" }}>
                ❌ {error}
              </p>
            )}
          </div>
        )}

        {data && (
          <>
            {/* TOP CONTROLLER (Minimized after run) */}
            <section className={styles.controlCenter}>
              <button
                onClick={() => {
                  setData(null);
                  fetchPrices();
                }}
                className={styles.backButton}
              >
                ← Back to Prices
              </button>
              <button
                onClick={triggerAgent}
                disabled={loading}
                className={styles.runButton}
              >
                {loading
                  ? "Agent is investigating..."
                  : "Rerun Intelligence Agent 🤖"}
              </button>

              {loading && (
                <p className={styles.statusMessage}>
                  Scanning database, querying strategy manual via RAG, and
                  drafting emails with Llama 3...
                </p>
              )}
              {error && (
                <p style={{ color: "var(--error)" }}>❌ {error}</p>
              )}
            </section>

            {/* RESULTS GRID */}
            <section className={styles.resultsGrid}>
              {/* LEFT: ALERTS */}
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>
                  Detected Anomalies ({data.alerts_found})
                </h2>
                <div className={styles.alertList}>
                  {data.alerts.map((alert, idx) => (
                    <div key={idx} className={styles.alertCard}>
                      <h3>
                        {alert.ingredient}
                        <span className={styles.badge}>
                          +{alert.pct_increase}%
                        </span>
                      </h3>
                      <p className={styles.alertDetail}>
                        <strong>{alert.restaurant_name}</strong>
                      </p>
                      <p className={styles.alertDetail}>
                        Spike from {alert.first_price.toFixed(2)}€ to{" "}
                        {alert.last_price.toFixed(2)}€/kg over{" "}
                        {alert.weeks_observed} weeks.
                      </p>
                    </div>
                  ))}
                  {data.alerts.length === 0 && (
                    <p style={{ color: "#a1a1aa" }}>
                      No cost anomalies detected.
                    </p>
                  )}
                </div>
              </div>

              {/* RIGHT: EMAIL VIEWER */}
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>
                  Generated Outreach Plan
                </h2>
                <div className={styles.emailViewer}>
                  {data.email_draft ? (
                    <>
                      <div className={styles.emailHeader}>
                        <div className={styles.emailLine}>
                          <strong>To:</strong> CX Team &rarr;{" "}
                          {data.alerts[0]?.contact_email || "Restaurant"}
                        </div>
                        <div className={styles.emailLine}>
                          <strong>Subject:</strong>{" "}
                          {data.email_draft
                            .split("\n")[0]
                            .replace("Asunto: ", "")
                            .replace("Subject: ", "") || "Cost Alert"}
                        </div>
                      </div>
                      <div className={styles.emailBody}>
                        {data.email_draft
                          .replace(/^Asunto:.*?\n/i, "")
                          .replace(/^Subject:.*?\n/i, "")
                          .trim()}
                      </div>
                    </>
                  ) : (
                    <p style={{ color: "#a1a1aa" }}>No email drafted.</p>
                  )}
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
