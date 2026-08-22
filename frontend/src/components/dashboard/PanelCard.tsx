import type { ReactNode } from "react";
import Link from "next/link";

interface PanelCardProps {
  title: string;
  linkHref?: string;
  linkLabel?: string;
  children: ReactNode;
  className?: string;
}

/** Bordered, monospace "brutalist" panel used across the redesigned dashboard. */
export function PanelCard({ title, linkHref, linkLabel, children, className = "" }: PanelCardProps) {
  return (
    <section className={`border border-black bg-white text-black ${className}`}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-black">
        <h2 className="text-xs font-bold uppercase tracking-wider">{title}</h2>
        {linkHref && (
          <Link href={linkHref} className="text-[10px] uppercase tracking-wide underline hover:no-underline">
            {linkLabel ?? "View all"}
          </Link>
        )}
      </div>
      <div className="p-4 space-y-3 font-mono text-sm">{children}</div>
    </section>
  );
}
