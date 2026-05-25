type PageHeaderProps = {
  title: string;
  eyebrow: string;
  children?: React.ReactNode;
};

export function PageHeader({ title, eyebrow, children }: PageHeaderProps) {
  return (
    <header className="mb-6 flex flex-col gap-3 border-b border-zinc-200 pb-5 md:flex-row md:items-end md:justify-between">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-cobalt">{eyebrow}</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">{title}</h1>
      </div>
      {children}
    </header>
  );
}
