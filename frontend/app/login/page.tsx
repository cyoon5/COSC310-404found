"use client";

import { FormEvent, useState } from "react";
import { loginUser } from "@/lib/api/auth";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

async function handleSubmit(e: FormEvent) {
  e.preventDefault();
  setError(null);
  setLoading(true);

  try {
    const result = await loginUser({ username, password });

    const session = {
      username,
      role: result.role,  
    };
    window.localStorage.setItem("session", JSON.stringify(session));

    window.dispatchEvent(new Event("sessionChanged"));

    router.push("/");
  } catch (err: any) {
    setError(err.message ?? "Login failed");
  } finally {
    setLoading(false);
  }
}


  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <label>Username</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p className="error">{error}</p>}

        <button className="button primary" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
