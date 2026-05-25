"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiBaseUrl } from "@/lib/api";
import { setAdminSession } from "@/lib/auth";

type Mode = "login" | "bootstrap";

export function LoginPanel() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit() {
    setIsSubmitting(true);
    setMessage(null);
    const response = await fetch(`${apiBaseUrl}/auth/${mode === "login" ? "login" : "bootstrap-admin"}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName || undefined
      })
    });
    const payload = await response.json();
    setIsSubmitting(false);
    if (!response.ok) {
      setMessage(payload.detail ?? "Authentication failed");
      return;
    }
    setAdminSession(payload.access_token, payload.user.email);
    router.push("/upload");
  }

  return (
    <section className="w-full rounded-md border border-zinc-200 bg-white p-6">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-cobalt">Administrator</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink">
        {mode === "login" ? "Sign in" : "Create first admin"}
      </h1>
      <div className="mt-6 grid gap-4">
        {mode === "bootstrap" && (
          <label className="text-sm font-medium">
            Name
            <input
              className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
            />
          </label>
        )}
        <label className="text-sm font-medium">
          Email
          <input
            className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label className="text-sm font-medium">
          Password
          <input
            className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
      </div>
      {message && <p className="mt-4 text-sm text-coral">{message}</p>}
      <button
        type="button"
        onClick={submit}
        disabled={isSubmitting}
        className="mt-5 w-full rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
      >
        {isSubmitting ? "Working..." : mode === "login" ? "Sign in" : "Create admin"}
      </button>
      <button
        type="button"
        onClick={() => setMode(mode === "login" ? "bootstrap" : "login")}
        className="mt-3 w-full rounded-md border border-zinc-300 px-4 py-2 text-sm font-semibold"
      >
        {mode === "login" ? "Create first admin" : "Back to sign in"}
      </button>
    </section>
  );
}
