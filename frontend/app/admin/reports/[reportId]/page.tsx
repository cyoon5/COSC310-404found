"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { decideReport, getAllReports } from "@/lib/api/moderation";
import { Report } from "@/lib/types";

export default function AdminHandleReportPage() {
  const params = useParams() as { reportId: string };
  const reportId = params.reportId;
  const router = useRouter();

  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [action, setAction] = useState<"confirm" | "reject" | "">("");
  const [banOption, setBanOption] = useState<"3d" | "7d" | "30d" | "">("");

  useEffect(() => {
    async function loadReport() {
      try {
        const all = await getAllReports();
        const found = all.find((r) => r.reportId === Number(reportId));
        if (!found) throw new Error("Report not found");

        setReport(found);
      } catch (err: any) {
        setError(err.message ?? "Failed to load report");
      } finally {
        setLoading(false);
      }
    }

    loadReport();
  }, [reportId]);

  async function handleSubmit() {
    if (!action) {
      alert("Choose confirm or reject");
      return;
    }

    try {
      await decideReport(Number(reportId), {
        action,
        banOption: banOption || null,
      });

      alert("Report handled successfully.");
      router.push("/admin/reports");
    } catch (err: any) {
      alert(err.message ?? "Failed to decide report.");
    }
  }

  if (loading) return <p>Loading report...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!report) return <p>Report not found.</p>;

  return (
    <div>
      <h1>Handle Report #{report.reportId}</h1>

      <div className="card" style={{ padding: "1rem", marginTop: "1rem" }}>
        <p><strong>Movie:</strong> {report.review.movieTitle}</p>
        <p><strong>Review Author:</strong> {report.review.user}</p>
        <p><strong>Reported By:</strong> {report.reportedBy}</p>

        <p>
          <strong>Reason:</strong> {report.reasonType}{" "}
          {report.reason && <> — {report.reason}</>}
        </p>

        <h3 style={{ marginTop: "1rem" }}>Decision</h3>

        <label>
          Action:
          <select value={action} onChange={(e) => setAction(e.target.value as any)}>
            <option value="">-- Choose --</option>
            <option value="confirm">Confirm</option>
            <option value="reject">Reject</option>
          </select>
        </label>

        {action === "confirm" && (
          <>
            <label style={{ marginTop: "0.5rem" }}>
              Ban Duration:
              <select
                value={banOption}
                onChange={(e) => setBanOption(e.target.value as any)}
              >
                <option value="">No ban</option>
                <option value="3d">3 days</option>
                <option value="7d">7 days</option>
                <option value="30d">30 days</option>
              </select>
            </label>
          </>
        )}

        <button
          className="button primary"
          style={{ marginTop: "1rem" }}
          onClick={handleSubmit}
        >
          Submit Decision
        </button>
      </div>
    </div>
  );
}
