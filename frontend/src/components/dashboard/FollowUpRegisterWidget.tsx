import React from "react";
import type { Commitment } from "@/lib/api";

interface FollowUpRegisterWidgetProps {
  commitments: Commitment[];
}

export default function FollowUpRegisterWidget({ commitments }: FollowUpRegisterWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">history_toggle_off</span>
        Follow-up Register
      </h2>

      {commitments.length === 0 ? (
        <p className="font-label-md text-label-md text-on-surface-variant">Nothing due soon.</p>
      ) : (
        <div className="space-y-3">
          {commitments.map((c) => (
            <div key={c.id} className="flex justify-between items-start gap-3 py-2 border-b border-slate-100 last:border-0">
              <div>
                <p className="font-label-md text-label-md font-medium text-on-surface">{c.description}</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">
                  {c.owner || "Unassigned"}{c.department ? ` · ${c.department}` : ""}
                </p>
              </div>
              {c.deadline && (
                <span className="font-label-sm text-label-sm text-on-surface-variant whitespace-nowrap">
                  {new Date(c.deadline).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
