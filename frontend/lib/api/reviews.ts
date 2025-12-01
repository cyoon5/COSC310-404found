import { apiClient } from "@/lib/apiClient";
import { Review } from "@/lib/types";

export async function getReviews(movieTitle: string, amount = 10): Promise<Review[]> {
  const encoded = encodeURIComponent(movieTitle);

  // Fetch raw backend CSV rows
  const raw = await apiClient.get<any[]>(`/reviews/${encoded}?amount=${amount}`);

  // Map CSV headers -> our frontend fields
  return raw.map((r) => ({
    movieTitle: r["Movie Title"] ?? r.movieTitle,
    user: r.user ?? r["User"],
    date: r["Date of Review"] ?? r.date,
    rating: r["User's Rating out of 10"]
      ? Number(r["User's Rating out of 10"])
      : r.rating ?? null,
    title: r["Review Title"] ?? r.title ?? "",
    body: r["Review"] ?? r.body ?? "",
    usefulVotes: r["Usefulness Vote"]
      ? Number(r["Usefulness Vote"])
      : r.usefulVotes ?? 0,
    totalVotes: r["Total Votes"]
      ? Number(r["Total Votes"])
      : r.totalVotes ?? 0,
    reportCount: r["Reports"]
      ? Number(r["Reports"])
      : r.reportCount ?? 0,
  }));
}


export interface ReviewCreatePayload {
  rating: number;
  title: string;
  body: string;
}

export async function addReview(
  movieTitle: string,
  payload: ReviewCreatePayload
): Promise<{ message: string }> {
  const encoded = encodeURIComponent(movieTitle);
  // Backend expects body: { rating, title, body }
  return apiClient.post<{ message: string }>(`/reviews/${encoded}`, payload);
}

export async function updateReview(
  movieTitle: string,
  username: string,
  body: Partial<{ rating: number; title: string; body: string }>
) {
  const mt = encodeURIComponent(movieTitle);
  const un = encodeURIComponent(username);

  return apiClient.put<{ message: string }>(
    `/reviews/${mt}/${un}`,
    body
  );
}

export async function deleteReview(movieTitle: string, username: string) {
  const mt = encodeURIComponent(movieTitle);
  const un = encodeURIComponent(username);

  return apiClient.del<{ message: string }>(`/reviews/${mt}/${un}`);
}

