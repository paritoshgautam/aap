import Link from "next/link";
import { BarChart3, ClipboardCheck, FlaskConical, Gauge, Library, LogIn, Upload } from "lucide-react";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/exam", label: "Exam", icon: ClipboardCheck },
  { href: "/review", label: "Review", icon: Library },
  { href: "/topics", label: "Topics", icon: BarChart3 },
  { href: "/upload", label: "Knowledge", icon: Upload },
  { href: "/login", label: "Admin Login", icon: LogIn },
  { href: "/admin/questions", label: "Questions", icon: FlaskConical }
] as const;

export function Sidebar() {
  return (
    <aside className="border-b border-zinc-200 bg-white px-4 py-4 lg:min-h-screen lg:border-b-0 lg:border-r">
      <div className="mb-5 flex items-center gap-2 text-lg font-semibold">
        <FlaskConical className="h-5 w-5 text-coral" />
        IB Chemistry
      </div>
      <nav className="grid grid-cols-2 gap-2 lg:grid-cols-1">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <Link
              key={link.href}
              href={link.href}
              className="flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-medium text-zinc-700 hover:bg-panel"
            >
              <Icon className="h-4 w-4" />
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
