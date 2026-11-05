"use client";

import { useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Msg = { role: "user" | "assistant"; content: string };
type Model = { id: string; label: string; kind: string };

export default function ChatPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [model, setModel] = useState("echo");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${API}/chat/models`)
      .then((r) => r.json())
      .then((d) => {
        setModels(d.models);
        if (d.models[0]) setModel(d.models[0].id);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    const next = [...messages, { role: "user" as const, content: text }];
    setMessages([...next, { role: "assistant", content: "" }]);
    setInput("");
    setBusy(true);

    try {
      const resp = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: next, model }),
      });
      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = line.slice(6);
          if (data === "[DONE]") continue;
          try {
            const obj = JSON.parse(data);
            if (obj.delta) {
              setMessages((prev) => {
                const copy = [...prev];
                copy[copy.length - 1] = {
                  role: "assistant",
                  content: copy[copy.length - 1].content + obj.delta,
                };
                return copy;
              });
            }
          } catch {
            /* fragment incomplet : ignoré */
          }
        }
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex h-screen max-w-3xl flex-col p-4">
      <header className="mb-3 flex items-center justify-between">
        <h1 className="text-xl font-bold">
          CYBER <span className="text-accent">AI</span> — Chat
        </h1>
        <select
          className="rounded bg-panel px-2 py-1 text-sm"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        >
          {models.map((m) => (
            <option key={m.id} value={m.id}>
              {m.label}
            </option>
          ))}
        </select>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto rounded-lg bg-panel p-4">
        {messages.length === 0 && (
          <p className="text-slate-500">Pose une question pour commencer…</p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={m.role === "user" ? "text-slate-100" : "text-accent"}
          >
            <span className="mr-2 text-xs uppercase text-slate-500">
              {m.role === "user" ? "toi" : "ia"}
            </span>
            <span className="whitespace-pre-wrap">{m.content}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3 flex gap-2">
        <input
          className="flex-1 rounded bg-panel px-3 py-2"
          placeholder="Écris ton message…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={busy}
        />
        <button
          className="rounded bg-accent px-4 py-2 font-medium text-bg disabled:opacity-50"
          onClick={send}
          disabled={busy}
        >
          Envoyer
        </button>
      </div>
    </main>
  );
}
