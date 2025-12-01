"use client";

import { useEffect, useState } from "react";
import { getMyWatchlist, removeFromWatchlist } from "@/lib/api/watchlist";

export default function WatchlistPage() {
  const [items, setItems] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await getMyWatchlist();
        setItems(data.watchlist);
      } catch (err: any) {
        setError(err.message ?? "Failed to load watchlist");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function handleRemove(title: string) {
    try {
      const res = await removeFromWatchlist(title);
      setItems(res.watchlist);
    } catch (err: any) {
      alert(err.message ?? "Failed to remove");
    }
  }

  return (
    <div>
      <h1>My Watchlist</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!loading &&
        !error &&
        (items.length === 0 ? (
          <p>Your watchlist is empty.</p>
        ) : (
          items.map((t) => (
            <div className="card" key={t}>
              <strong>{t}</strong>
              <button
                className="button danger"
                style={{ marginLeft: "0.5rem" }}
                onClick={() => handleRemove(t)}
              >
                Remove
              </button>
            </div>
          ))
        ))}
    </div>
  );
}
