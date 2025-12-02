"use client";

import { useEffect, useState, FormEvent } from "react";
import { getAllMovies, updateMovie } from "@/lib/api/movies";
import { getSession } from "@/lib/apiClient";

export default function EditMoviePage({ params }: any) {
  const [clientReady, setClientReady] = useState(false);
  const [form, setForm] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const session = getSession();
  const title = decodeURIComponent(params.title);

  useEffect(() => {
    setClientReady(true);
  }, []);

  useEffect(() => {
    if (!clientReady) return;

    (async () => {
      try {
        const movies = await getAllMovies();
        const movie = movies.find((m) => m.title === title);

        if (!movie) {
          alert("Movie not found.");
          window.location.href = "/movies";
          return;
        }

        setForm({
          ...movie,
          movieGenres: movie.movieGenres.join(", "),
          directors: movie.directors.join(", "),
          mainStars: movie.mainStars.join(", "),
          creators: movie.creators.join(", "),
        });
      } catch (err) {
        alert("Failed to load movie.");
      } finally {
        setLoading(false);
      }
    })();
  }, [clientReady, title]);

  useEffect(() => {
    if (!clientReady) return;

    if (!session || session.role !== "admin") {
      window.location.href = "/login";
    }
  }, [clientReady, session]);

  if (!clientReady) return <p>Loading...</p>;

  if (loading || !form) return <p>Loading movie data...</p>;

  function updateField(key: string, value: string) {
    setForm((prev: any) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const payload = {
      ...form,
      movieGenres: form.movieGenres.split(",").map((s: string) => s.trim()),
      directors: form.directors.split(",").map((s: string) => s.trim()),
      mainStars: form.mainStars.split(",").map((s: string) => s.trim()),
      creators: form.creators.split(",").map((s: string) => s.trim()),
    };

    try {
      await updateMovie(title, payload);
      alert("Movie updated successfully!");
      window.location.href = "/movies";
    } catch (err: any) {
      alert(err.message || "Failed to update movie.");
    }
  }

  return (
    <div style={{ maxWidth: "600px" }}>
      <h1>Edit Movie: {title}</h1>

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
      >
        {Object.entries(form).map(([key, value]) =>
          typeof value === "object" ? null : (
            <label key={key} style={{ display: "flex", flexDirection: "column" }}>
              {key}
              <input
                value={String(value ?? "")}
                onChange={(e) => updateField(key, e.target.value)}
                style={{ padding: "0.5rem" }}
              />
            </label>
          )
        )}

        <button className="button primary" type="submit">
          Save Changes
        </button>
      </form>
    </div>
  );
}
