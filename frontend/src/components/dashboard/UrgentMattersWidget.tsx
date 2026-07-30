import React from "react";

export interface UrgentMatter {
  id: string;
  label: string;
  category: "Email" | "Task" | "Risk";
}

interface UrgentMattersWidgetProps {
  matters: UrgentMatter[];
}

const categoryIcon: Record<UrgentMatter["category"], string> = {
  Email: "mark_email_unread",
  Task: "task_alt",
  Risk: "warning",
};

export default function UrgentMattersWidget({ matters }: UrgentMattersWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6 border-t-4 border-t-error">
      <h2 className="font-headline-md text-headline-md text-error flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">emergency_home</span>
        Urgent Matters
      </h2>

      {matters.length === 0 ? (
        <p className="font-label-md text-label-md text-on-surface-variant">Nothing urgent right now.</p>
      ) : (
        <div className="space-y-3">
          {matters.map((m) => (
            <div key={`${m.category}-${m.id}`} className="flex items-center gap-3 p-3 bg-error-container/40 rounded-lg">
              <span className="material-symbols-outlined text-[18px] text-error shrink-0">
                {categoryIcon[m.category]}
              </span>
              <p className="font-label-md text-label-md text-on-surface truncate">{m.label}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
