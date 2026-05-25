import { PageHeader } from "@/components/page-header";

export default function ReviewPage() {
  return (
    <>
      <PageHeader eyebrow="Mistake review" title="Recent attempts" />
      <div className="grid gap-3">
        {["Le Chatelier's principle", "Bond enthalpy calculations", "Oxidation state rules"].map(
          (topic) => (
            <article key={topic} className="rounded-md border border-zinc-200 bg-white p-4">
              <h2 className="font-semibold">{topic}</h2>
              <p className="mt-2 text-sm text-zinc-600">
                Review evidence, source references, and rubric feedback will appear here.
              </p>
            </article>
          )
        )}
      </div>
    </>
  );
}
