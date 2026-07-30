import React from "react";

export interface InsightItem {
  type: "RISK" | "OPPORTUNITY" | "SUMMARY";
  title: string;
  description: string;
}

interface InsightsWidgetProps {
  insight: InsightItem | null;
}

export default function InsightsWidget({ insight }: InsightsWidgetProps) {
  if (!insight) return null;

  const isRisk = insight.type === "RISK";

  return (
    <section className="glass-card rounded-xl p-6 bg-gradient-to-br from-surface to-secondary-fixed/10 border-t-4 border-t-primary">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-outlined text-primary text-[24px]">
          psychology
        </span>
        <h2 className="font-headline-md text-headline-md text-primary">
          Strategic Insight
        </h2>
      </div>

      <div className="bg-white rounded-lg p-5 border border-slate-100 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-bl-full -mr-4 -mt-4"></div>
        <h3
          className={`font-label-md text-label-md font-bold mb-2 flex items-center gap-1 relative z-10 ${
            isRisk ? "text-error" : "text-primary"
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">
            {isRisk ? "warning" : "lightbulb"}
          </span>{" "}
          {insight.title}
        </h3>
        <p className="font-body-md text-body-md text-on-surface relative z-10">
          {insight.description}
        </p>

        <div className="mt-6 flex justify-end relative z-10">
          <button className="font-label-md text-label-md text-primary flex items-center gap-1 hover:underline">
            View Analysis{" "}
            <span className="material-symbols-outlined text-[16px]">
              arrow_forward
            </span>
          </button>
        </div>
      </div>
    </section>
  );
}
