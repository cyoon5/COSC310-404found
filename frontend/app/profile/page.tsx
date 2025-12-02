"use client";

import { FormEvent, useState } from "react";
import { getSession, setSession } from "@/lib/apiClient";
import {
  changePassword,
  updateBio,
  changeUsername,
} from "@/lib/api/profile";

export default function ProfilePage() {
  const session = getSession();

  if (!session) {
    return (
      <div>
        <h1>Profile</h1>
        <p>You must be logged in to view this page.</p>
      </div>
    );
  }

  const [passwordForm, setPasswordForm] = useState({
    old_password: "",
    new_password: "",
  });
  const [bio, setBio] = useState("");
  const [newUsername, setNewUsername] = useState("");

  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ───────────────── Change password ─────────────────
  async function handlePasswordSubmit(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    setError(null);

    try {
      await changePassword({
        username: session!.username,
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
      });

      setMessage("Password updated successfully.");
      setPasswordForm({ old_password: "", new_password: "" });
    } catch (err: any) {
      setError(err.message ?? "Failed to update password.");
    }
  }

  // ──────────────── Update bio ────────────────
  async function handleBioSubmit(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    setError(null);

    try {
      await updateBio({
        username: session!.username,
        bio,
      });

      setMessage("Bio updated successfully.");
    } catch (err: any) {
      setError(err.message ?? "Failed to update bio.");
    }
  }

  // ──────────────── Change username ────────────────
  async function handleUsernameSubmit(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    setError(null);

    try {
      const res = await changeUsername({ newUsername });

      // update local session so the app knows about the new username
      setSession({ username: res.newUsername, role: session!.role });

      setMessage("Username changed successfully.");
      setNewUsername("");
    } catch (err: any) {
      setError(err.message ?? "Failed to change username.");
    }
  }

  return (
    <div>
      <h1>Profile</h1>
      <p>Logged in as: <strong>{session!.username}</strong></p>

      {error && <p className="error" style={{ color: "red" }}>{error}</p>}
      {message && <p className="success" style={{ color: "green" }}>{message}</p>}

      {/* Change password */}
      <div className="card" style={{ marginTop: "1rem", padding: "1rem" }}>
        <h2>Change Password</h2>
        <form onSubmit={handlePasswordSubmit}>
          <label>
            Current password
            <input
              type="password"
              value={passwordForm.old_password}
              onChange={(e) =>
                setPasswordForm((f) => ({
                  ...f,
                  old_password: e.target.value,
                }))
              }
            />
          </label>

          <label>
            New password
            <input
              type="password"
              value={passwordForm.new_password}
              onChange={(e) =>
                setPasswordForm((f) => ({
                  ...f,
                  new_password: e.target.value,
                }))
              }
            />
          </label>

          <button className="button primary" type="submit">
            Update password
          </button>
        </form>
      </div>

      {/* Update bio */}
      <div className="card" style={{ marginTop: "1rem", padding: "1rem" }}>
        <h2>Update Bio</h2>
        <form onSubmit={handleBioSubmit}>
          <label>
            Bio
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={3}
            />
          </label>

          <button className="button primary" type="submit">
            Save bio
          </button>
        </form>
      </div>

      {/* Change username */}
      <div className="card" style={{ marginTop: "1rem", padding: "1rem" }}>
        <h2>Change Username</h2>
        <form onSubmit={handleUsernameSubmit}>
          <label>
            New username
            <input
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
            />
          </label>

          <button className="button primary" type="submit">
            Change username
          </button>
        </form>
      </div>
    </div>
  );
}
