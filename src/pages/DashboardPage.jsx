import React, { useEffect, useState } from "react";

function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/stats/summary")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        return res.json();
      })
      .then(setStats)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div className="dashboard-error">Error: {error}</div>;
  }

  if (!stats) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="stats-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem" }}>
        <div className="stat-item" style={{ padding: "1rem", border: "1px solid #ccc", borderRadius: "4px" }}>
          <h2>Total Members</h2>
          <p>{stats.total_members ?? "N/A"}</p>
        </div>
        <div className="stat-item" style={{ padding: "1rem", border: "1px solid #ccc", borderRadius: "4px" }}>
          <h2>Active Today</h2>
          <p>{stats.active_today ?? "N/A"}</p>
        </div>
        <div className="stat-item" style={{ padding: "1rem", border: "1px solid #ccc", borderRadius: "4px" }}>
          <h2>Revenue This Month</h2>
          <p>${stats.revenue_this_month ?? "0"}</p>
        </div>
        <div className="stat-item" style={{ padding: "1rem", border: "1px solid #ccc", borderRadius: "4px" }}>
          <h2>Classes Today</h2>
          <p>{stats.classes_today ?? "N/A"}</p>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
