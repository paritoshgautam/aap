import { PageHeader } from "@/components/page-header";
import { QuestionGeneratorPanel } from "@/components/question-generator-panel";
import { getQuestions, getSubjects, getTopics } from "@/lib/api";

const statuses = ["draft", "validating", "approved", "rejected"] as const;

export default async function QuestionAdminPage() {
  const [questions, subjects, topics] = await Promise.all([
    getQuestions(),
    getSubjects(),
    getTopics()
  ]);
  const counts = Object.fromEntries(
    statuses.map((status) => [status, questions.filter((question) => question.status === status).length])
  );

  return (
    <>
      <PageHeader eyebrow="Validation pipeline" title="Question review admin" />
      <QuestionGeneratorPanel subjects={subjects} topics={topics} />
      <section className="grid gap-4 xl:grid-cols-[280px_1fr]">
        <div className="rounded-md border border-zinc-200 bg-white p-5">
          <div className="grid gap-3">
            {statuses.map((status) => (
              <div key={status} className="flex items-center justify-between border-b border-zinc-100 py-3">
                <span className="font-medium capitalize">{status.replace("_", " ")}</span>
                <span className="text-sm text-zinc-500">{counts[status]} items</span>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-md border border-zinc-200 bg-white">
          <div className="border-b border-zinc-100 px-5 py-4">
            <h2 className="text-base font-semibold">Latest generated questions</h2>
          </div>
          <div className="divide-y divide-zinc-100">
            {questions.length === 0 ? (
              <p className="px-5 py-6 text-sm text-zinc-500">No generated questions yet.</p>
            ) : (
              questions.slice(0, 12).map((question) => (
                <article key={question.id} className="px-5 py-4">
                  <div className="mb-2 flex flex-wrap items-center gap-2 text-xs font-semibold uppercase text-zinc-500">
                    <span>{question.type}</span>
                    <span>{question.status}</span>
                    <span>difficulty {question.difficulty}</span>
                  </div>
                  <p className="text-sm font-medium leading-6">{question.stem}</p>
                </article>
              ))
            )}
          </div>
        </div>
      </section>
    </>
  );
}
