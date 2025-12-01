"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getSession, setSession, Session } from "@/lib/apiClient";

export default function NavBar() {
  const [session, setSessionState] = useState<Session | null>(null);

  // Load session AND subscribe to updates
  useEffect(() => {
    // Initial load
    setSessionState(getSession());

    // Listen for custom app-level events (login/logout)
    function handleSessionEvent() {
      setSessionState(getSession());
    }

    window.addEventListener("sessionChanged", handleSessionEvent);

    // Also refresh if localStorage changes (other tabs)
    function handleStorage(e: StorageEvent) {
      if (e.key === "session") {
        setSessionState(getSession());
      }
    }
    window.addEventListener("storage", handleStorage);

    return () => {
      window.removeEventListener("sessionChanged", handleSessionEvent);
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  function handleLogout() {
    setSession(null);

    // Tell ALL components session changed
    window.dispatchEvent(new Event("sessionChanged"));

    setSessionState(null);
  }

  return (
    <nav className="navbar">
      <div className="nav-links">
        <Link href="/">Home</Link>
        <Link href="/movies">Movies</Link>
        {session && <Link href="/watchlist">My Watchlist</Link>}
        {session?.role === "admin" && <Link href="/admin/reports">Admin</Link>}
      </div>

      <div className="nav-right">
        {session ? (
          <>
            <span>
              {session.username}{" "}
              <span className={`badge ${session.role === "admin" ? "admin" : ""}`}>
                {session.role}
              </span>
            </span>
            <button className="button danger" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link href="/login" className="button">
              Login
            </Link>
            <Link href="/register" className="button primary">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
