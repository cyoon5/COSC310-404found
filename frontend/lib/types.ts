export interface Movie {
  title: string;
  movieIMDbRating: number;
  totalRatingCount: number;
  totalUserReviews: string;
  totalCriticReviews: string;
  metaScore: string;
  movieGenres: string[];
  directors: string[];
  datePublished: string;
  creators: string[];
  mainStars: string[];
  description?: string;
  duration: number;
}


export interface Review {
  movieTitle: string;
  user: string;
  date: string;
  rating?: number | null;
  usefulVotes?: number | null;
  totalVotes?: number | null;
  title: string;
  body: string;
  reportCount?: number | null;
}

export interface ReviewCreate {
  rating: number;
  title: string;
  body: string;
}

export interface ReviewUpdate {
  rating?: number;
  title?: string;
  body?: string;
}

export interface ReviewSnapshot {
  movieTitle: string;
  user: string;
  rating: number;
  usefulVotes: number;
  totalVotes: number;
  title: string;
  body: string;
  reportCount: number;
}

export type ReportStatus = "pending" | "confirmed" | "rejected";

export interface ReportCreate {
  reasonType: string;
  reason?: string | null;
}

export interface Report {
  reportId: number;
  review: ReviewSnapshot;
  reportedBy: string;
  status: ReportStatus;
  dateReported: string;
  reasonType: string;
  reason?: string | null;
  handledByAdmin?: string | null;
  handledAt?: string | null;
  banDurationSeconds?: number | null;
}

export interface ReportDecisionRequest {
  action: "confirm" | "reject";
  banOption?: "3d" | "7d" | "30d" | null;
}

export interface Ban {
  banId: number;
  userName: string;
  reportedBy: string;
  reportId: number;
  movieTitle: string;
  reviewUser: string;
  reasonType: string;
  reason?: string | null;
  banOption: "3d" | "7d" | "30d";
  banDurationSeconds: number;
  bannedAt: string;
  bannedUntil: string;
}

export type Role = "user" | "admin";

export interface WatchlistResponse {
  watchlist: string[];
}
