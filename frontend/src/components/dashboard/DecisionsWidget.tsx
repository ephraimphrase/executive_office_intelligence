import React from "react";

export interface DecisionItem {
  id: string;
  title: string;
  description: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "DEFERRED";
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  dueDate: string | null;
}

interface DecisionsWidgetProps {
  decisions: DecisionItem[];
  title?: string;
}

export default function DecisionsWidget({ decisions, title = "Pending Decisions" }: DecisionsWidgetProps) {
  return (
    <section className="glass-card rounded-xl overflow-hidden">
      <div className="p-6 pb-4 border-b border-slate-100 bg-slate-50/50">
        <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2">
          <span className="material-symbols-outlined text-[24px]">
            assignment_turned_in
          </span>
          {title}
        </h2>
      </div>

      <div className="w-full overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr>
              <th className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider py-3 px-6 bg-slate-50 border-b border-slate-200">
                Decision Item
              </th>
              <th className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider py-3 px-6 bg-slate-50 border-b border-slate-200">
                Status
              </th>
              <th className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider py-3 px-6 bg-slate-50 border-b border-slate-200 text-right">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {decisions.map((decision) => (
              <tr key={decision.id} className="hover:bg-slate-50 transition-colors group">
                <td className="py-4 px-6">
                  <p className="font-label-md text-label-md font-semibold text-primary mb-1">
                    {decision.title}
                  </p>
                  <p className="font-label-sm text-label-sm text-on-surface-variant">
                    {decision.description}
                  </p>
                  {decision.dueDate && (
                    <p className="font-label-sm text-label-sm text-on-surface-variant mt-2 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">
                        event
                      </span>{" "}
                      Due: {decision.dueDate}
                    </p>
                  )}
                </td>
                <td className="py-4 px-6 align-top">
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-primary-fixed text-on-primary-fixed-variant border border-primary-fixed-dim/50">
                    {decision.status}
                  </span>
                </td>
                <td className="py-4 px-6 align-top text-right">
                  <button className="opacity-0 group-hover:opacity-100 font-label-md text-label-md text-primary bg-white border border-slate-200 px-3 py-1.5 rounded hover:bg-slate-50 transition-all shadow-sm">
                    Review
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
