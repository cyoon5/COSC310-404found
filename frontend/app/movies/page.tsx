"use client";

import { useEffect, useState, FormEvent } from "react";
import {
  getAllMovies,
  getFilteredMovies,
  MovieFilterParams,
} from "@/lib/api/movies";
import { Movie, Review } from "@/lib/types";
import { addToWatchlist } from "@/lib/api/watchlist";
import { getReviews, addReview, ReviewCreatePayload } from "@/lib/api/reviews";
import { reportReview } from "@/lib/api/moderation";
import { getSession } from "@/lib/apiClient";
import { updateReview, deleteReview } from "@/lib/api/reviews";



function MovieCard({ movie }: { movie: Movie }) {
  const [showReviews, setShowReviews] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [reviewsError, setReviewsError] = useState<string | null>(null);

  const [reportingUser, setReportingUser] = useState<string | null>(null);
  const [reasonType, setReasonType] = useState("");
  const [reason, setReason] = useState("");
  const [reportError, setReportError] = useState<string | null>(null);
  const [reportSuccess, setReportSuccess] = useState<string | null>(null);

  const session = getSession(); 
  const [editingReview, setEditingReview] = useState<Review | null>(null);
  const [editForm, setEditForm] = useState({
    rating: "",
    title: "",
    body: "",
  });

  const [form, setForm] = useState<{ rating: string; title: string; body: string }>({
    rating: "",
    title: "",
    body: "",
  });

  const [limit, setLimit] = useState(10);

  async function loadReviews(newLimit = limit) {
    setReviewsLoading(true);
    setReviewsError(null);

    try {
      const data = await getReviews(movie.title, newLimit);
      setReviews(data);
      setLimit(newLimit);
    } catch (err: any) {
      if (err.message === "No reviews found for this movie") {
        setReviews([]);
      } else {
        setReviewsError(err.message ?? "Failed to load reviews");
      }
    } finally {
      setReviewsLoading(false);
    }
  }

  function handleToggleReviews() {
    const next = !showReviews;
    setShowReviews(next);
    if (next) {
      void loadReviews();
    }
  }

  async function handleAddToWatchlistClick() {
    try {
      await addToWatchlist(movie.title);
      alert("Added to watchlist");
    } catch (err: any) {
      alert(err.message ?? "Failed to add to watchlist");
    }
  }

  async function handleSubmitReview(e: FormEvent) {
    e.preventDefault();

    const ratingNum = Number(form.rating);
    if (isNaN(ratingNum) || ratingNum < 1 || ratingNum > 10) {
      alert("Rating must be between 1 and 10");
      return;
    }

    if (!form.title.trim() || !form.body.trim()) {
      alert("Title and review body cannot be empty");
      return;
    }

    const payload: ReviewCreatePayload = {
      rating: ratingNum,
      title: form.title,
      body: form.body,
    };

    try {
      await addReview(movie.title, payload);
      await loadReviews();
      setForm({ rating: "", title: "", body: "" });
    } catch (err: any) {
      alert(err.message ?? "Failed to submit review");
    }
  }

  return (
    <div className="card">
      <h3>
        {movie.title}{" "}
        <span className="badge">{movie.movieIMDbRating}/10</span>
      </h3>

      {movie.description && <p>{movie.description}</p>}

      <p>
        <strong>Genres:</strong> {movie.movieGenres.join(", ")}
      </p>

      {movie.directors?.length > 0 && (
        <p>
          <strong>Director(s):</strong> {movie.directors.join(", ")}
        </p>
      )}

      {movie.mainStars?.length > 0 && (
        <p>
          <strong>Main Stars:</strong> {movie.mainStars.join(", ")}
        </p>
      )}

      {movie.creators?.length > 0 && (
        <p>
          <strong>Creators:</strong> {movie.creators.join(", ")}
        </p>
      )}

      {movie.metaScore && (
        <p>
          <strong>Meta Score:</strong> {movie.metaScore}
        </p>
      )}

      {movie.totalUserReviews && (
        <p>
          <strong>User Reviews:</strong> {movie.totalUserReviews}
        </p>
      )}

      {movie.totalCriticReviews && (
        <p>
          <strong>Critic Reviews:</strong> {movie.totalCriticReviews}
        </p>
      )}

      {typeof movie.totalRatingCount === "number" && (
        <p>
          <strong>Rating Count:</strong>{" "}
          {movie.totalRatingCount.toLocaleString()}
        </p>
      )}

      {movie.datePublished && (
        <p>
          <strong>Release Date:</strong> {movie.datePublished.toString()}
        </p>
      )}

      {typeof movie.duration === "number" && (
        <p>
          <strong>Duration:</strong> {movie.duration} minutes
        </p>
      )}

      <button className="button" onClick={handleAddToWatchlistClick}>
        Add to watchlist
      </button>

      <button
        className="button"
        style={{ marginLeft: "0.5rem" }}
        onClick={handleToggleReviews}
      >
        {showReviews ? "Hide reviews" : "Show reviews"}
      </button>

      {showReviews && (
        <div style={{ marginTop: "1rem" }}>
          <h4>Reviews</h4>

          {reviewsLoading && <p>Loading reviews...</p>}
          {reviewsError && <p className="error">{reviewsError}</p>}

          {!reviewsLoading && !reviewsError && reviews.length === 0 && (
            <p>No reviews yet.</p>
          )}

          {!reviewsLoading && !reviewsError && reviews.length > 0 && (
            <>
              <ul>
                {reviews.map((r, idx) => (
                  <li key={idx} style={{ marginBottom: "0.75rem" }}>
                    <strong>{r.title}</strong> ({r.rating ?? "N/A"}/10) by {r.user}{" "}
                    {r.date && (
                      <>
                        {" "}
                        on <em>{r.date}</em>
                      </>
                    )}
                    <br />
                    {r.body}
                        {/* USER or ADMIN controls */}
{(session?.username === r.user || session?.role === "admin") && (
  <div style={{ marginTop: "0.5rem" }}>
    {/* EDIT BUTTON */}
    <button
      className="button"
      onClick={() => {
        setEditingReview(r);
        setEditForm({
          rating: r.rating?.toString() ?? "",
          title: r.title,
          body: r.body,
        });
      }}
    >
      Edit
    </button>

    {/* DELETE BUTTON */}
    <button
      className="button danger"
      style={{ marginLeft: "0.5rem" }}
      onClick={async () => {
        if (!confirm("Delete this review?")) return;
          try {
            await deleteReview(movie.title, r.user);
            await loadReviews(limit);
          } catch (err: any) {
            alert(err.message);   
          }
      }}
    >
      Delete
    </button>
  </div>
)}


                    <div style={{ marginTop: "0.5rem" }}>
                      <button
                        className="button danger"
                        onClick={() => {
                          console.log("Reporting user:", r.user);
                          setReportingUser(r.user);
                          setReasonType("");
                          setReason("");
                          setReportError(null);
                          setReportSuccess(null);
                        }}
                      >
                        Report Review
                      </button>
                    </div>
                  </li>
                ))}
              </ul>

              {reviews.length >= limit && (
                <button
                  className="button"
                  onClick={() => loadReviews(limit + 10)}
                  style={{ marginTop: "0.5rem" }}
                >
                  Load more reviews
                </button>
              )}
            </>
          )}

          {/* ------------------------------------------------------- */}
          {/* REPORT POPUP INSERTED HERE                               */}
          {/* ------------------------------------------------------- */}

          {reportingUser && (
            <div className="card" style={{ marginTop: "1rem", padding: "1rem" }}>
              <h4>Report review by {reportingUser}</h4>

              {reportError && <p className="error">{reportError}</p>}
              {reportSuccess && <p className="success">{reportSuccess}</p>}

              <label>Reason Type (required)</label>
              <select value={reasonType} onChange={(e) => setReasonType(e.target.value)}>
                <option value="">-- Choose --</option>
                <option value="spam">Spam</option>
                <option value="abusive">Abusive / Harassment</option>
                <option value="inappropriate">Inappropriate Content</option>
                <option value="other">Other</option>
              </select>

              {reasonType === "other" && (
                <>
                  <label>Explanation (optional)</label>
                  <textarea value={reason} onChange={(e) => setReason(e.target.value)} />
                </>
              )}

              <div style={{ marginTop: "0.75rem" }}>
                <button
                  className="button danger"
                  onClick={async () => {
                    try {
                      if (!reasonType) {
                        setReportError("You must choose a reason type.");
                        return;
                      }

                      const payload = { reasonType, reason: reason || undefined };
                      await reportReview(movie.title, reportingUser, payload);

                      setReportSuccess("Report submitted successfully.");
                      setReportingUser(null);
                      loadReviews(limit);
                    } catch (err: any) {
                      setReportError(err.message ?? "Failed to submit report.");
                    }
                  }}
                >
                  Submit Report
                </button>

                <button
                  className="button"
                  style={{ marginLeft: "0.5rem" }}
                  onClick={() => setReportingUser(null)}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

{/* ------------------------------------------------------- */}
{/* EDIT REVIEW POPUP                                       */}
{/* ------------------------------------------------------- */}

{editingReview && (
  <div className="card" style={{ marginTop: "1rem", padding: "1rem" }}>
    <h4>Edit Your Review</h4>

    <label>Rating (1–10)</label>
    <input
      type="number"
      value={editForm.rating}
      min={1}
      max={10}
      step={0.1}
      onChange={(e) =>
        setEditForm({ ...editForm, rating: e.target.value })
      }
    />

    <label>Title</label>
    <input
      value={editForm.title}
      onChange={(e) =>
        setEditForm({ ...editForm, title: e.target.value })
      }
    />

    <label>Review</label>
    <textarea
      value={editForm.body}
      onChange={(e) =>
        setEditForm({ ...editForm, body: e.target.value })
      }
    />

    <button
      className="button primary"
      onClick={async () => {
        await updateReview(movie.title, editingReview.user, {
          rating: Number(editForm.rating),
          title: editForm.title,
          body: editForm.body,
        });

        setEditingReview(null);
        await loadReviews(limit);
      }}
    >
      Save Changes
    </button>

    <button
      className="button"
      style={{ marginLeft: "0.5rem" }}
      onClick={() => setEditingReview(null)}
    >
      Cancel
    </button>
  </div>
)}


          <h5 style={{ marginTop: "1rem" }}>Add a review</h5>

          <form onSubmit={handleSubmitReview} className="review-form">
            <label>
              Rating (1–10)
              <input
                type="number"
                min={1}
                max={10}
                step="0.1"
                value={form.rating}
                onChange={(e) =>
                  setForm((f) => ({ ...f, rating: e.target.value }))
                }
              />
            </label>

            <label>
              Title
              <input
                value={form.title}
                onChange={(e) =>
                  setForm((f) => ({ ...f, title: e.target.value }))
                }
              />
            </label>

            <label>
              Review
              <textarea
                value={form.body}
                onChange={(e) =>
                  setForm((f) => ({ ...f, body: e.target.value }))
                }
              />
            </label>

            <button className="button primary" type="submit">
              Submit review
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default function MoviesPage() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<MovieFilterParams>({
    title: "",
    genre: "",
    director: "",
    main_star: "",
    min_rating: undefined,
    max_rating: undefined,
    start_date: "",
    sort_by: undefined,
    descending: false,
  });

  useEffect(() => {
    (async () => {
      try {
        const data = await getAllMovies();
        setMovies(data);
      } catch (err: any) {
        setError(err.message ?? "Failed to load movies");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function handleFilter(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await getFilteredMovies(filters);
      setMovies(data);
    } catch (err: any) {
      setError(err.message ?? "Failed to filter movies");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>Movies</h1>

      <form onSubmit={handleFilter} className="filter-form">
        <label>Title contains</label>
        <input
          value={filters.title}
          onChange={(e) =>
            setFilters((f) => ({ ...f, title: e.target.value }))
          }
        />

        <label>Genre</label>
        <input
          value={filters.genre}
          onChange={(e) =>
            setFilters((f) => ({ ...f, genre: e.target.value }))
          }
        />

        <label>Director</label>
        <input
          value={filters.director}
          onChange={(e) =>
            setFilters((f) => ({ ...f, director: e.target.value }))
          }
        />

        <label>Main Star</label>
        <input
          value={filters.main_star}
          onChange={(e) =>
            setFilters((f) => ({ ...f, main_star: e.target.value }))
          }
        />

        <label>Min rating</label>
        <input
          type="number"
          min={0}
          max={10}
          step="0.1"
          value={filters.min_rating ?? ""}
          onChange={(e) =>
            setFilters((f) => ({
              ...f,
              min_rating: e.target.value
                ? Number(e.target.value)
                : undefined,
            }))
          }
        />

        <label>Max rating</label>
        <input
          type="number"
          min={0}
          max={10}
          step="0.1"
          value={filters.max_rating ?? ""}
          onChange={(e) =>
            setFilters((f) => ({
              ...f,
              max_rating: e.target.value
                ? Number(e.target.value)
                : undefined,
            }))
          }
        />

        <label>Start date</label>
        <input
          type="date"
          value={filters.start_date}
          onChange={(e) =>
            setFilters((f) => ({ ...f, start_date: e.target.value }))
          }
        />

        <label>Sort by</label>
        <select
          value={filters.sort_by ?? ""}
          onChange={(e) =>
            setFilters((f) => ({
              ...f,
              sort_by:
                e.target.value === ""
                  ? undefined
                  : (e.target.value as "rating" | "release_date"),
            }))
          }
        >
          <option value="">None</option>
          <option value="rating">Rating</option>
          <option value="release_date">Release date</option>
        </select>
<div>
  <label
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: "0.5rem",
      flexDirection: "row-reverse",
      cursor: "pointer",
      whiteSpace: "nowrap",   

    }}
  >
    <input
      type="checkbox"
      checked={filters.descending}
      onChange={(e) =>
        setFilters((f) => ({ ...f, descending: e.target.checked }))
      }
    />
    Descending order
  </label>
</div>



        <button className="button primary" type="submit">
          Apply filters
        </button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && movies.map((m) => <MovieCard key={m.title} movie={m} />)}
    </div>
  );
}
