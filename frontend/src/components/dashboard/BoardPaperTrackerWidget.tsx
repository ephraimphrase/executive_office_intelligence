import React from "react";
import type { Document } from "@/lib/api";

interface BoardPaperTrackerWidgetProps {
  papers: Document[];
}

export default function BoardPaperTrackerWidget({ papers }: BoardPaperTrackerWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">gavel</span>
        Board Paper Tracker
      </h2>

      {papers.length === 0 ? (
        <p className="font-label-md text-label-md text-on-surface-variant">No board papers on file.</p>
      ) : (
        <div className="space-y-3">
          {papers.map((doc) => (
            <div key={doc.id} className="flex justify-between items-center gap-3 py-2 border-b border-slate-100 last:border-0">
              <div className="flex items-center gap-2 min-w-0">
                <span className="material-symbols-outlined text-[18px] text-on-surface-variant shrink-0">
                  description
                </span>
                <p className="font-label-md text-label-md font-medium text-on-surface truncate">{doc.title}</p>
              </div>
              <span className="font-label-sm text-label-sm text-on-surface-variant whitespace-nowrap">
                {new Date(doc.last_modified).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
