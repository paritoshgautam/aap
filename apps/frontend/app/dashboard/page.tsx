import { PageHeader } from "@/components/page-header";
import { ReadinessChart } from "@/components/readiness-chart";

export default function DashboardPage() {
  return (
    <>
      <PageHeader eyebrow="Student analytics" title="Readiness dashboard" />
      <section className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="rounded-md border border-zinc-200 bg-white p-5">
          <ReadinessChart />
        </div>
        <div className="rounded-md border border-zinc-200 bg-white p-5">
          <h2 className="text-base font-semibold">Current estimate</h2>
          <dl className="mt-5 grid gap-4">
            <div>
              <dt className="text-sm text-zinc-500">Readiness</dt>
              <dd className="text-3xl font-semibold text-moss">72%</dd>
            </div>
            <div>
              <dt className="text-sm text-zinc-500">Weakest topic</dt>
              <dd className="text-lg font-medium">Equilibrium</dd>
            </div>
            <div>
              <dt className="text-sm text-zinc-500">Next adaptive focus</dt>
              <dd className="text-lg font-medium">Energetics, medium difficulty</dd>
            </div>
          </dl>
        </div>
      </section>
    </>
  );
}
