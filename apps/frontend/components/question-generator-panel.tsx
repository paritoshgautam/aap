"use client";

import { useEffect, useMemo, useState } from "react";
import { WandSparkles } from "lucide-react";
import { apiBaseUrl, type Subject, type Topic } from "@/lib/api";
import { clearAdminSession, getAdminToken } from "@/lib/auth";

type QuestionType = "mcq" | "numeric" | "open_ended";

type QuestionGeneratorPanelProps = {
  subjects: Subject[];
  topics: Topic[];
};

export function QuestionGeneratorPanel({ subjects, topics }: QuestionGeneratorPanelProps) {
  const [token, setToken] = useState<string | null>(null);
  const [selectedSubjectId, setSelectedSubjectId] = useState(subjects[0]?.id ?? "");
  const [selectedTopicId, setSelectedTopicId] = useState("");
  const [questionType, setQuestionType] = useState<QuestionType>("mcq");
  const [count, setCount] = useState(5);
  const [difficultyTarget, setDifficultyTarget] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const filteredTopics = useMemo(() => {
    if (!selectedSubjectId) return topics;
    return topics.filter((topic) => topic.ib_metadata?.subject_id === selectedSubjectId);
  }, [selectedSubjectId, topics]);

  useEffect(() => {
    setToken(getAdminToken());
  }, []);

  useEffect(() => {
    setSelectedTopicId((current) => {
      if (filteredTopics.some((topic) => topic.id === current)) return current;
      return filteredTopics[0]?.id ?? "";
    });
  }, [filteredTopics]);

  async function generateQuestions() {
    if (!token) {
      setMessage("Admin sign-in is required before generating questions.");
      return;
    }
    if (!selectedTopicId) {
      setMessage("Select a mapped topic first.");
      return;
    }

    setIsGenerating(true);
    setMessage(null);
    const response = await fetch(`${apiBaseUrl}/questions/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        topic_id: selectedTopicId,
        question_type: questionType,
        count,
        difficulty_target: difficultyTarget
      })
    });
    const payload = await response.json();
    setIsGenerating(false);

    if (response.status === 401) {
      clearAdminSession();
      setToken(null);
      setMessage("Your admin session expired. Sign in again, then retry generation.");
      return;
    }

    if (!response.ok) {
      setMessage(formatApiError(payload.detail));
      return;
    }

    setMessage(
      `Created ${payload.created.length} draft question${payload.created.length === 1 ? "" : "s"}; rejected ${payload.rejected.length}. Refresh to see the latest list.`
    );
  }

  return (
    <section className="mb-5 rounded-md border border-zinc-200 bg-white p-5">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-base font-semibold">Generate questions</h2>
          <p className="mt-1 text-sm text-zinc-500">Creates draft questions from mapped source chunks.</p>
        </div>
        <button
          type="button"
          onClick={generateQuestions}
          disabled={isGenerating || !selectedTopicId}
          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
        >
          <WandSparkles className="h-4 w-4" />
          {isGenerating ? "Generating..." : "Generate"}
        </button>
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <label className="text-sm font-medium">
          Subject
          <select
            className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
            value={selectedSubjectId}
            onChange={(event) => setSelectedSubjectId(event.target.value)}
          >
            <option value="">All subjects</option>
            {subjects.map((subject) => (
              <option key={subject.id} value={subject.id}>
                {subject.name}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium xl:col-span-2">
          Topic
          <select
            className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
            value={selectedTopicId}
            onChange={(event) => setSelectedTopicId(event.target.value)}
          >
            {filteredTopics.length === 0 ? (
              <option value="">No mapped topics</option>
            ) : (
              filteredTopics.map((topic) => (
                <option key={topic.id} value={topic.id}>
                  {topic.title}
                </option>
              ))
            )}
          </select>
        </label>
        <label className="text-sm font-medium">
          Type
          <select
            className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
            value={questionType}
            onChange={(event) => setQuestionType(event.target.value as QuestionType)}
          >
            <option value="mcq">MCQ</option>
            <option value="numeric">Numeric</option>
            <option value="open_ended">Open-ended</option>
          </select>
        </label>
        <label className="text-sm font-medium">
          Count
          <input
            className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
            type="number"
            min={1}
            max={10}
            value={count}
            onChange={(event) => setCount(Number(event.target.value))}
          />
        </label>
        <label className="text-sm font-medium">
          Difficulty
          <input
            className="mt-2 block w-full rounded-md border border-zinc-300 p-2"
            type="number"
            min={-4}
            max={4}
            step={0.5}
            value={difficultyTarget}
            onChange={(event) => setDifficultyTarget(Number(event.target.value))}
          />
        </label>
      </div>
      {message && <p className="mt-4 text-sm text-cobalt">{message}</p>}
    </section>
  );
}

function formatApiError(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) {
          return String(item.msg);
        }
        return "Request validation failed.";
      })
      .join(" ");
  }
  return "Question generation failed.";
}
