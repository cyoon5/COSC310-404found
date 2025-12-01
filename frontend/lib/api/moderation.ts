import { apiClient } from "@/lib/apiClient";
import { Ban, Report, ReportCreate, ReportDecisionRequest } from "@/lib/types";

export async function reportReview(
  movieTitle: string,
  reviewUser: string,
  body: ReportCreate
) {
  const mt = encodeURIComponent(movieTitle);
  const ru = encodeURIComponent(reviewUser);
  return apiClient.post<{ message: string; report: Report }>(
    `/moderation/reports/${mt}/${ru}`,
    body
  );
}

export async function decideReport(reportId: number, body: ReportDecisionRequest) {
  return apiClient.post<{ message: string; report: Report; ban?: Ban }>(
    `/moderation/reports/${reportId}/decision`,
    body
  );
}

export async function getPendingReports() {
  return apiClient.get<Report[]>(`/moderation/reports/pending`);
}

export async function getAllReports(status?: "pending" | "confirmed" | "rejected") {
  const qs = status ? `?status=${status}` : "";
  return apiClient.get<Report[]>(`/moderation/reports${qs}`);
}

export async function getBans(userName?: string) {
  const qs = userName ? `?userName=${encodeURIComponent(userName)}` : "";
  return apiClient.get<Ban[]>(`/moderation/bans${qs}`);
}
