import type { Metadata } from "next";
import { Sidebar } from "@/components/sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Adaptive Assessment",
  description: "IB Chemistry adaptive assessment platform"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen lg:grid lg:grid-cols-[248px_1fr]">
          <Sidebar />
          <main className="px-5 py-5 lg:px-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
