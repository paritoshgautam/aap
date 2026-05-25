import { PageHeader } from "@/components/page-header";

export default function ExamPage() {
  return (
    <>
      <PageHeader eyebrow="Adaptive simulator" title="Chemistry practice exam">
        <div className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm font-semibold">
          52:00
        </div>
      </PageHeader>
      <section className="rounded-md border border-zinc-200 bg-white p-5">
        <div className="mb-5 flex items-center justify-between text-sm text-zinc-500">
          <span>Question 1 of 32</span>
          <span>Medium difficulty</span>
        </div>
        <h2 className="max-w-3xl text-xl font-semibold">
          Which statement best explains why increasing temperature changes the equilibrium
          constant for an exothermic reaction?
        </h2>
        <div className="mt-6 grid gap-3">
          {["Forward rate increases only", "Reverse reaction is favored", "Catalyst activity rises", "Volume decreases"].map(
            (choice) => (
              <button
                key={choice}
                className="min-h-12 rounded-md border border-zinc-200 px-4 text-left hover:border-cobalt hover:bg-panel"
              >
                {choice}
              </button>
            )
          )}
        </div>
      </section>
    </>
  );
}
