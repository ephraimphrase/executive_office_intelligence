import React from "react";
import type { WaitingTask } from "@/lib/api";

interface WaitingForWidgetProps {
  waitingForMe: WaitingTask[];
  waitingForOthers: WaitingTask[];
}

function TaskRow({ task }: { task: WaitingTask }) {
  return (
    <div className="flex justify-between items-center gap-3 py-2 border-b border-slate-100 last:border-0">
      <p className="font-label-md text-label-md font-medium text-on-surface truncate">{task.title}</p>
      {task.due_date && (
        <span className="font-label-sm text-label-sm text-on-surface-variant whitespace-nowrap">
          {new Date(task.due_date).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
        </span>
      )}
    </div>
  );
}

export default function WaitingForWidget({ waitingForMe, waitingForOthers }: WaitingForWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">hourglass_empty</span>
        Waiting On
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div>
          <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-2">
            Waiting For Me ({waitingForMe.length})
          </h3>
          {waitingForMe.length === 0 ? (
            <p className="font-label-sm text-label-sm text-on-surface-variant">Nothing pending.</p>
          ) : (
            waitingForMe.map((t) => <TaskRow key={t.id} task={t} />)
          )}
        </div>
        <div>
          <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-2">
            Waiting For Others ({waitingForOthers.length})
          </h3>
          {waitingForOthers.length === 0 ? (
            <p className="font-label-sm text-label-sm text-on-surface-variant">Nothing pending.</p>
          ) : (
            waitingForOthers.map((t) => <TaskRow key={t.id} task={t} />)
          )}
        </div>
      </div>
    </section>
  );
}
