"use client";

import { useState } from "react";
import styles from "./page.module.css";

// Match the Python TypedDict structure
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

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<RunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const triggerAgent = async () => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      // Calls the FastAPI server running on port 8000
      const res = await fetch("http://localhost:8000/api/run", {
        method: "POST",
      });

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
            <h1 className={styles.initialTitle}>Start Operations Analysis</h1>
            <p className={styles.initialSubtitle}>
              Click the Run button to start the analysis.
            </p>
            <button
              onClick={triggerAgent}
              disabled={loading}
              className={`${styles.runButton} ${styles.runButtonLarge}`}
            >
              {loading ? "Agent is investigating..." : "Run Intelligence Agent 🤖"}
            </button>
            {loading && (
              <p className={styles.statusMessage} style={{ marginTop: "1rem" }}>
                Scanning database, querying strategy manual via RAG, and drafting emails with Llama 3...
              </p>
            )}
            {error && <p style={{ color: "var(--error)", marginTop: "1rem" }}>❌ {error}</p>}
          </div>
        )}

        {data && (
          <>
            {/* TOP CONTROLLER (Minimized version for after run) */}
            <section className={styles.controlCenter}>
              <button
                onClick={triggerAgent}
                disabled={loading}
                className={styles.runButton}
              >
                {loading ? "Agent is investigating..." : "Rerun Intelligence Agent 🤖"}
              </button>
              
              {loading && (
                <p className={styles.statusMessage}>
                  Scanning database, querying strategy manual via RAG, and drafting emails with Llama 3...
                </p>
              )}
              {error && <p style={{ color: "var(--error)" }}>❌ {error}</p>}
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
                    <p style={{ color: "#a1a1aa" }}>No cost anomalies detected.</p>
                  )}
                </div>
              </div>

              {/* RIGHT: EMAIL VIEWER */}
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Generated Outreach Plan</h2>
                <div className={styles.emailViewer}>
                  {data.email_draft ? (
                    <>
                      <div className={styles.emailHeader}>
                        <div className={styles.emailLine}>
                          <strong>To:</strong> CX Team &rarr; {data.alerts[0]?.contact_email || "Restaurant"}
                        </div>
                        <div className={styles.emailLine}>
                          <strong>Subject:</strong> {data.email_draft.split("\n")[0].replace("Asunto: ", "").replace("Subject: ", "") || "Cost Alert"}
                        </div>
                      </div>
                      <div className={styles.emailBody}>
                        {/* Strip the subject line out if it was included in the text so it doesn't double-render */}
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
