import { PageHeader } from "@/components/page-header";

const topics = [
  { name: "Stoichiometry", mastery: "82%", risk: "Low" },
  { name: "Atomic structure", mastery: "76%", risk: "Moderate" },
  { name: "Equilibrium", mastery: "48%", risk: "High" }
];

export default function TopicsPage() {
  return (
    <>
      <PageHeader eyebrow="Knowledge graph" title="Topic analytics" />
      <section className="overflow-hidden rounded-md border border-zinc-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="bg-panel text-zinc-600">
            <tr>
              <th className="px-4 py-3">Topic</th>
              <th className="px-4 py-3">Mastery</th>
              <th className="px-4 py-3">Risk</th>
            </tr>
          </thead>
          <tbody>
            {topics.map((topic) => (
              <tr key={topic.name} className="border-t border-zinc-100">
                <td className="px-4 py-3 font-medium">{topic.name}</td>
                <td className="px-4 py-3">{topic.mastery}</td>
                <td className="px-4 py-3">{topic.risk}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}
