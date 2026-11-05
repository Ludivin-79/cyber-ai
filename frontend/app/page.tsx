"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Caps = {
  environment: string;
  features: Record<string, boolean>;
};

export default function Home() {
  const [caps, setCaps] = useState<Caps | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/capabilities`)
      .then((r) => r.json())
      .then(setCaps)
      .catch(() => setError("Backend injoignable"));
  }, []);

  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="text-3xl font-bold">
        CYBER <span className="text-accent">AI</span>
      </h1>
      <p className="mt-2 text-slate-400">
        Socle en place. Le chat en streaming est disponible ; OSINT et CTI
        arrivent dans les phases suivantes.
      </p>
      <a
        href="/chat"
        className="mt-4 inline-block rounded bg-accent px-4 py-2 font-medium text-bg"
      >
        Ouvrir le chat →
      </a>

      <section className="mt-8 rounded-lg bg-panel p-6">
        <h2 className="mb-4 text-lg font-semibold">
          État réel des capacités
        </h2>
        {error && <p className="text-red-400">{error}</p>}
        {!caps && !error && <p className="text-slate-500">Chargement…</p>}
        {caps && (
          <ul className="space-y-1 text-sm">
            {Object.entries(caps.features).map(([name, on]) => (
              <li key={name} className="flex items-center gap-2">
                <span className={on ? "text-accent" : "text-slate-600"}>
                  {on ? "●" : "○"}
                </span>
                <span className={on ? "" : "text-slate-500"}>{name}</span>
                <span className="text-slate-600">
                  {on ? "opérationnel" : "clé/API requise"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
