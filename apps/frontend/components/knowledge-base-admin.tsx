"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { RefreshCw, Upload } from "lucide-react";
import { apiBaseUrl } from "@/lib/api";

type Subject = {
  id: string;
  code: string;
  name: string;
  curriculum: string;
};

type Topic = {
  id: string;
  code: string;
  title: string;
};

type Source = {
  id: string;
  subject_id: string | null;
  filename: string;
  status: string;
  version: number;
  metadata_json: Record<string, unknown>;
};

export function KnowledgeBaseAdmin() {
  const [token, setToken] = useState<string | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState("");
  const [selectedTopicId, setSelectedTopicId] = useState("");
  const [level, setLevel] = useState("HL");
  const [message, setMessage] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [subjectName, setSubjectName] = useState("Chemistry");
  const [subjectCode, setSubjectCode] = useState("chemistry");
  const [topicTitle, setTopicTitle] = useState("");
  const [topicCode, setTopicCode] = useState("");

  const subjectNames = useMemo(
    () => Object.fromEntries(subjects.map((subject) => [subject.id, subject.name])),
    [subjects]
  );

  useEffect(() => {
    const storedToken = localStorage.getItem("adaptive_admin_token");
    setToken(storedToken);
  }, []);

  useEffect(() => {
    void refresh();
  }, [token]);

  async function refresh() {
    const [subjectResponse, topicResponse] = await Promise.all([
      fetch(`${apiBaseUrl}/curriculum/subjects`, { cache: "no-store" }),
      fetch(`${apiBaseUrl}/curriculum/topics`, { cache: "no-store" })
    ]);
    if (subjectResponse.ok) {
      const nextSubjects = await subjectResponse.json();
      setSubjects(nextSubjects);
      setSelectedSubjectId((current) => current || nextSubjects[0]?.id || "");
    }
    if (topicResponse.ok) {
      const nextTopics = await topicResponse.json();
      setTopics(nextTopics);
      setSelectedTopicId((current) => current || nextTopics[0]?.id || "");
    }
    if (token) {
      const sourceResponse = await fetch(`${apiBaseUrl}/ingestion/sources`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store"
      });
      if (sourceResponse.ok) {
        setSources(await sourceResponse.json());
      }
    }
  }

  async function createSubject() {
    if (!token) return;
    setIsBusy(true);
    setMessage(null);
    const response = await fetch(`${apiBaseUrl}/curriculum/subjects`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        code: subjectCode,
        name: subjectName,
        curriculum: "IB"
      })
    });
    setIsBusy(false);
    setMessage(response.ok ? "Subject created." : "Could not create subject.");
    await refresh();
  }

  async function createTopic() {
    if (!token) return;
    setIsBusy(true);
    setMessage(null);
    const response = await fetch(`${apiBaseUrl}/curriculum/topics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        code: topicCode,
        title: topicTitle,
        ib_metadata: { subject_id: selectedSubjectId }
      })
    });
    setIsBusy(false);
    setMessage(response.ok ? "Topic created." : "Could not create topic.");
    await refresh();
  }

  async function uploadKnowledgeBase(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    const form = event.currentTarget;
    const formData = new FormData(form);
    const files = formData.getAll("files").filter((file): file is File => file instanceof File && Boolean(file.name));
    if (files.length === 0) {
      setMessage("Choose at least one source file first.");
      return;
    }

    const body = new FormData();
    files.forEach((file) => body.append("files", file));
    if (selectedSubjectId) body.append("subject_id", selectedSubjectId);
    if (selectedTopicId) body.append("topic_id", selectedTopicId);
    body.append("curriculum", "IB");
    body.append("level", level);
    body.append("chunk_size", String(formData.get("chunk_size") || 1200));
    body.append("chunk_overlap", String(formData.get("chunk_overlap") || 160));

    setIsBusy(true);
    setMessage(null);
    const response = await fetch(`${apiBaseUrl}/ingestion/sources`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body
    });
    const payload = await response.json();
    setIsBusy(false);
    if (!response.ok) {
      setMessage(payload.detail ?? "Upload failed.");
      return;
    }
    form.reset();
    const uploaded = payload.results?.length ?? 0;
    const chunks = payload.results?.reduce(
      (total: number, result: { chunks_created: number }) => total + result.chunks_created,
      0
    );
    setMessage(`Uploaded ${uploaded} file${uploaded === 1 ? "" : "s"}; created ${chunks ?? 0} chunks.`);
    await refresh();
  }

  async function mapKnowledgeBase() {
    if (!token) return;
    setIsBusy(true);
    setMessage(null);
    const response = await fetch(`${apiBaseUrl}/knowledge-base/map`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        subject_id: selectedSubjectId || undefined
      })
    });
    const payload = await response.json();
    setIsBusy(false);
    if (!response.ok) {
      setMessage(payload.detail ?? "Mapping failed.");
      return;
    }
    setMessage(
      `Mapped ${payload.chunks_mapped} chunks and created ${payload.topics_created} topics.`
    );
    await refresh();
  }

  if (!token) {
    return (
      <section className="rounded-md border border-zinc-200 bg-white p-5">
        <p className="text-sm text-zinc-600">Admin sign-in is required to manage knowledge bases.</p>
        <Link
          href="/login"
          className="mt-4 inline-flex rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white"
        >
          Sign in
        </Link>
      </section>
    );
  }

  return (
    <section className="grid gap-5 xl:grid-cols-[360px_1fr]">
      <div className="grid gap-5">
        <div className="rounded-md border border-zinc-200 bg-white p-5">
          <h2 className="text-base font-semibold">Subjects</h2>
          <div className="mt-4 grid gap-3">
            <input
              className="rounded-md border border-zinc-300 p-2 text-sm"
              value={subjectName}
              onChange={(event) => setSubjectName(event.target.value)}
              placeholder="Subject name"
            />
            <input
              className="rounded-md border border-zinc-300 p-2 text-sm"
              value={subjectCode}
              onChange={(event) => setSubjectCode(event.target.value)}
              placeholder="subject-code"
            />
            <button
              type="button"
              onClick={createSubject}
              disabled={isBusy}
              className="rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
            >
              Add subject
            </button>
          </div>
        </div>
        <div className="rounded-md border border-zinc-200 bg-white p-5">
          <h2 className="text-base font-semibold">Topics</h2>
          <div className="mt-4 grid gap-3">
            <select
              className="rounded-md border border-zinc-300 p-2 text-sm"
              value={selectedSubjectId}
              onChange={(event) => setSelectedSubjectId(event.target.value)}
            >
              <option value="">No subject</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.name}
                </option>
              ))}
            </select>
            <input
              className="rounded-md border border-zinc-300 p-2 text-sm"
              value={topicTitle}
              onChange={(event) => setTopicTitle(event.target.value)}
              placeholder="Topic title"
            />
            <input
              className="rounded-md border border-zinc-300 p-2 text-sm"
              value={topicCode}
              onChange={(event) => setTopicCode(event.target.value)}
              placeholder="topic-code"
            />
            <button
              type="button"
              onClick={createTopic}
              disabled={isBusy}
              className="rounded-md border border-zinc-300 px-4 py-2 text-sm font-semibold disabled:opacity-60"
            >
              Add topic
            </button>
          </div>
        </div>
      </div>
      <div className="grid gap-5">
        <form onSubmit={uploadKnowledgeBase} className="rounded-md border border-zinc-200 bg-white p-5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-base font-semibold">Upload KB source</h2>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={mapKnowledgeBase}
                disabled={isBusy}
                className="rounded-md border border-zinc-300 px-3 text-sm font-semibold disabled:opacity-60"
              >
                Map topics
              </button>
              <button
                type="button"
                onClick={() => void refresh()}
                className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-zinc-300"
                title="Refresh"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <label className="text-sm font-medium">
              Subject
              <select
                className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
                value={selectedSubjectId}
                onChange={(event) => setSelectedSubjectId(event.target.value)}
              >
                <option value="">No subject</option>
                {subjects.map((subject) => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm font-medium">
              Topic
              <select
                className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
                value={selectedTopicId}
                onChange={(event) => setSelectedTopicId(event.target.value)}
              >
                <option value="">Auto-detect</option>
                {topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.title}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm font-medium">
              Level
              <select
                className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
                value={level}
                onChange={(event) => setLevel(event.target.value)}
              >
                <option value="HL">HL</option>
                <option value="SL">SL</option>
                <option value="SL/HL">SL/HL</option>
              </select>
            </label>
            <label className="text-sm font-medium md:col-span-2">
              Source documents
              <input
                name="files"
                type="file"
                accept=".pdf,.docx,.txt,.md"
                multiple
                className="mt-2 block w-full rounded-md border border-zinc-300 p-3 text-sm"
              />
            </label>
            <label className="text-sm font-medium">
              Chunk size
              <input
                name="chunk_size"
                className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
                defaultValue={1200}
              />
            </label>
            <label className="text-sm font-medium">
              Overlap
              <input
                name="chunk_overlap"
                className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
                defaultValue={160}
              />
            </label>
          </div>
          {message && <p className="mt-4 text-sm text-cobalt">{message}</p>}
          <button
            className="mt-5 inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
            disabled={isBusy}
          >
            <Upload className="h-4 w-4" />
            Upload source
          </button>
        </form>
        <div className="rounded-md border border-zinc-200 bg-white">
          <div className="border-b border-zinc-100 px-5 py-4">
            <h2 className="text-base font-semibold">Ingested sources</h2>
          </div>
          <div className="divide-y divide-zinc-100">
            {sources.length === 0 ? (
              <p className="px-5 py-6 text-sm text-zinc-500">No knowledge base sources yet.</p>
            ) : (
              sources.map((source) => (
                <article key={source.id} className="px-5 py-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold">{source.filename}</p>
                      <p className="mt-1 text-xs text-zinc-500">
                        {source.subject_id ? subjectNames[source.subject_id] : "No subject"} ·{" "}
                        {String(source.metadata_json.source_type ?? "source")} · v{source.version}
                      </p>
                    </div>
                    <span className="rounded-md border border-zinc-200 px-2 py-1 text-xs font-semibold uppercase">
                      {source.status}
                    </span>
                  </div>
                </article>
              ))
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
