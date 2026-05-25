export const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export type Question = {
  id: string;
  topic_id: string;
  type: "mcq" | "numeric" | "open_ended" | "diagram";
  status: "draft" | "validating" | "approved" | "rejected";
  stem: string;
  answer: Record<string, unknown>;
  blooms_level: string | null;
  difficulty: string;
  source_references: Record<string, unknown>[];
};

export type Subject = {
  id: string;
  code: string;
  name: string;
  curriculum: string;
};

export type Topic = {
  id: string;
  code: string;
  title: string;
  description: string | null;
  ib_metadata: Record<string, unknown>;
};

export async function getQuestions(): Promise<Question[]> {
  const response = await fetch(`${apiBaseUrl}/questions`, {
    cache: "no-store"
  });
  if (!response.ok) {
    return [];
  }
  return response.json();
}

export async function getSubjects(): Promise<Subject[]> {
  const response = await fetch(`${apiBaseUrl}/curriculum/subjects`, {
    cache: "no-store"
  });
  if (!response.ok) {
    return [];
  }
  return response.json();
}

export async function getTopics(): Promise<Topic[]> {
  const response = await fetch(`${apiBaseUrl}/curriculum/topics`, {
    cache: "no-store"
  });
  if (!response.ok) {
    return [];
  }
  return response.json();
}
