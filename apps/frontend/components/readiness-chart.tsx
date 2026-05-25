"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const data = [
  { week: "W1", readiness: 52 },
  { week: "W2", readiness: 57 },
  { week: "W3", readiness: 61 },
  { week: "W4", readiness: 68 },
  { week: "W5", readiness: 72 }
];

export function ReadinessChart() {
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ left: 0, right: 16, top: 16, bottom: 8 }}>
          <XAxis dataKey="week" tickLine={false} />
          <YAxis domain={[0, 100]} tickLine={false} />
          <Tooltip />
          <Line type="monotone" dataKey="readiness" stroke="#305f9f" strokeWidth={3} dot />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
