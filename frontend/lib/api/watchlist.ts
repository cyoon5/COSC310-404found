import { apiClient } from "@/lib/apiClient";
import { WatchlistResponse } from "@/lib/types";

export async function getMyWatchlist() {
  return apiClient.get<WatchlistResponse>("/watchlist");
}

export async function addToWatchlist(title: string) {
  const encoded = encodeURIComponent(title);
  return apiClient.post(`/watchlist/${encoded}`, null);
}

export async function removeFromWatchlist(title: string) {
  const encoded = encodeURIComponent(title);
  return apiClient.del<WatchlistResponse & { message: string }>(
    `/watchlist/${encoded}`
  );
}
