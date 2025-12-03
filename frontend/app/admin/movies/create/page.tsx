"use client";

import { useState, useEffect, FormEvent } from "react";
import { createMovie } from "@/lib/api/movies";
import { getSession } from "@/lib/apiClient";

export default function CreateMoviePage() {
  const [clientReady, setClientReady] = useState(false);
  const session = getSession();

  useEffect(() => setClientReady(true), []);

  const [form, setForm] = useState({
    title: "",
    description: "",
    movieGenres: "",
    directors: "",
    mainStars: "",
    creators: "",
    movieIMDbRating: "",
    metaScore: "",
    totalUserReviews: "",
    totalCriticReviews: "",
    totalRatingCount: "",
    datePublished: "",
    duration: "",
  });

async function handleSubmit(e: FormEvent) {
  e.preventDefault();

  const payload: any = {
    title: form.title,
    description: form.description,

    movieGenres: form.movieGenres.split(",").map((s) => s.trim()),
    directors: form.directors.split(",").map((s) => s.trim()),
    mainStars: form.mainStars.split(",").map((s) => s.trim()),
    creators: form.creators.split(",").map((s) => s.trim()),

    movieIMDbRating: Number(form.movieIMDbRating),
    datePublished: form.datePublished,
  };

  if (form.metaScore) payload.metaScore = Number(form.metaScore);
  if (form.totalUserReviews) payload.totalUserReviews = Number(form.totalUserReviews);
  if (form.totalCriticReviews) payload.totalCriticReviews = Number(form.totalCriticReviews);
  if (form.totalRatingCount) payload.totalRatingCount = Number(form.totalRatingCount);
  if (form.duration) payload.duration = Number(form.duration);

  try {
    await createMovie(payload);
    alert("Movie created!");
    window.location.href = "/movies";
  } catch (err: any) {
    alert(err.message || "Creation failed.");
  }
}


  if (!clientReady) return <p>Loading...</p>;

  if (session?.role !== "admin")
    return <p>You do not have permission to create movies.</p>;

  return (
    <div style={{ maxWidth: "600px" }}>
      <h1>Create a New Movie</h1>

      <form onSubmit={handleSubmit} className="form">
        <label>
          Title
          <input
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
        </label>

        <label>
          Description
          <textarea
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </label>

        <label>
          Genres (comma separated)
          <input
            value={form.movieGenres}
            onChange={(e) => setForm({ ...form, movieGenres: e.target.value })}
          />
        </label>

        <label>
          Directors (comma separated)
          <input
            value={form.directors}
            onChange={(e) => setForm({ ...form, directors: e.target.value })}
          />
        </label>

        <label>
          Main Stars (comma separated)
          <input
            value={form.mainStars}
            onChange={(e) => setForm({ ...form, mainStars: e.target.value })}
          />
        </label>

        <label>
          Creators (comma separated)
          <input
            value={form.creators}
            onChange={(e) => setForm({ ...form, creators: e.target.value })}
          />
        </label>

        <label>
          IMDb Rating (number)
          <input
            type="number"
            step="0.1"
            min="0"
            max="10"
            value={form.movieIMDbRating}
            onChange={(e) => setForm({ ...form, movieIMDbRating: e.target.value })}
          />
        </label>

        <label>
          Meta Score (optional)
          <input
            type="number"
            value={form.metaScore}
            onChange={(e) => setForm({ ...form, metaScore: e.target.value })}
          />
        </label>

        <label>
          Total User Reviews
          <input
            type="number"
            value={form.totalUserReviews}
            onChange={(e) => setForm({ ...form, totalUserReviews: e.target.value })}
          />
        </label>

        <label>
          Total Critic Reviews
          <input
            type="number"
            value={form.totalCriticReviews}
            onChange={(e) => setForm({ ...form, totalCriticReviews: e.target.value })}
          />
        </label>

        <label>
          Rating Count
          <input
            type="number"
            value={form.totalRatingCount}
            onChange={(e) => setForm({ ...form, totalRatingCount: e.target.value })}
          />
        </label>

        <label>
          Release Date
          <input
            type="date"
            value={form.datePublished}
            onChange={(e) => setForm({ ...form, datePublished: e.target.value })}
          />
        </label>

        <label>
          Duration (minutes)
          <input
            type="number"
            value={form.duration}
            onChange={(e) => setForm({ ...form, duration: e.target.value })}
          />
        </label>

        <button className="button primary" type="submit">
          Create Movie
        </button>
      </form>
    </div>
  );
}
