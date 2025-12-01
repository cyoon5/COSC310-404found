import { apiClient } from "@/lib/apiClient";
import { Movie } from "@/lib/types";

export interface MovieFilterParams {
  title?: string;
  min_rating?: number;
  max_rating?: number;
  genre?: string;
  director?: string;
  main_star?: string;
  start_date?: string; // YYYY-MM-DD
  sort_by?: "rating" | "release_date";
  descending?: boolean;
}

function toQuery(params: Record<string, any>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.append(key, String(value));
    }
  });
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export async function getAllMovies() {
  return apiClient.get<Movie[]>("/movies");
}

export async function getFilteredMovies(params: MovieFilterParams) {
  const qs = toQuery(params as any);
  return apiClient.get<Movie[]>(`/movies/get-filtered-movies${qs}`);
}

export async function createMovie(movie: Movie) {
  return apiClient.post<Movie>("/movies/create-movie", movie);
}

export async function updateMovie(title: string, movie: Movie) {
  return apiClient.put<Movie>(`/movies/update-movie/${encodeURIComponent(title)}`, movie);
}

export async function deleteMovie(title: string) {
  return apiClient.del<void>(`/movies/delete-movie/${encodeURIComponent(title)}`);
}
