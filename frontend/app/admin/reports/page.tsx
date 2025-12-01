"use client";

import { useEffect, useState } from "react";
import { getPendingReports } from "@/lib/api/moderation";
import { Report } from "@/lib/types";
import Link from "next/link";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getPendingReports();
        setReports(data);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div>
      <h1>Pending Reports</h1>

      {loading && <p>Loading...</p>}

      {!loading && reports.length === 0 && <p>No pending reports.</p>}

      {!loading &&
        reports.map((r) => (
          <div
            key={r.reportId}
            className="card"
            style={{ padding: "1rem", marginTop: "1rem" }}
          >
            <h3>
              Report #{r.reportId} — <em>{r.review.movieTitle}</em>
            </h3>

            <p>
              <strong>Reported Review Author:</strong> {r.review.user}
            </p>

            <p>
              <strong>Reason:</strong> {r.reasonType}{" "}
              {r.reason && <span>— {r.reason}</span>}
            </p>

            <p>
              <strong>Review Title:</strong> {r.review.title}
            </p>

            <p>
              <strong>Review Body:</strong>
              <br />
              {r.review.body}
            </p>

            <Link
              href={`/admin/reports/${r.reportId}`}
              className="button"
              style={{ marginTop: "0.5rem", display: "inline-block" }}
            >
              Handle Report
            </Link>
          </div>
        ))}
    </div>
  );
}
