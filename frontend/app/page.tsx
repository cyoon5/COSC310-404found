"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getSession, Session } from "@/lib/apiClient";

export default function HomePage() {
  const [session, setSessionState] = useState<Session | null>(null);

  useEffect(() => {
    // Load initial session
    setSessionState(getSession());

    function updateSession() {
      setSessionState(getSession());
    }

    // Listen for session changes (login/logout)
    window.addEventListener("sessionChanged", updateSession);

    // Detect updates from other tabs or windows
    window.addEventListener("storage", updateSession);

    return () => {
      window.removeEventListener("sessionChanged", updateSession);
      window.removeEventListener("storage", updateSession);
    };
  }, []);

  return (
    <div>
      <h1>Movie Reviews App</h1>
      <p>Welcome! Use the navigation bar to browse movies, login, or manage your watchlist.</p>

      <div style={{ marginTop: "1rem" }}>

        {/* MOVIES CARD */}
        <div className="card">
          <h2>Movies</h2>
          <p>Browse and filter all movies from the IMDb dataset.</p>
          <Link href="/movies" className="button primary">
            Go to Movies
          </Link>
        </div>

        {/* ACCOUNT CARD — hidden if logged in */}
        {!session && (
          <div className="card">
            <h2>Account</h2>
            <p>Login or register to create reviews and manage your watchlist.</p>
            <Link href="/login" className="button">Login</Link>{" "}
            <Link href="/register" className="button">Register</Link>
          </div>
        )}
      </div>
    </div>
  );
}
