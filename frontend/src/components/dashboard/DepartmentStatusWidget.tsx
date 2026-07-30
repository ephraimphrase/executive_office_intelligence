import React from "react";
import type { DepartmentTaskReport } from "@/lib/api";

interface DepartmentStatusWidgetProps {
  report: DepartmentTaskReport;
}

export default function DepartmentStatusWidget({ report }: DepartmentStatusWidgetProps) {
  const departments = Object.entries(report);

  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">domain</span>
        Department Status
      </h2>

      {departments.length === 0 ? (
        <p className="font-label-md text-label-md text-on-surface-variant">No department activity yet.</p>
      ) : (
        <div className="space-y-4">
          {departments.map(([dept, stats]) => {
            const pct = stats.total ? Math.round((stats.completed / stats.total) * 100) : 0;
            return (
              <div key={dept}>
                <div className="flex justify-between items-baseline mb-1">
                  <span className="font-label-md text-label-md font-medium text-on-surface">{dept}</span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant">
                    {stats.completed}/{stats.total} done
                    {stats.overdue > 0 ? ` · ${stats.overdue} overdue` : ""}
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${pct}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
