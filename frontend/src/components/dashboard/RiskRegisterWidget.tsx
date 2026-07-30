import React from "react";
import type { Risk } from "@/lib/api";

interface RiskRegisterWidgetProps {
  risks: Risk[];
}

const severityColor: Record<string, string> = {
  CRITICAL: "bg-error-container text-on-error-container border-error/20",
  HIGH: "bg-error-container text-on-error-container border-error/20",
  MEDIUM: "bg-secondary-container text-on-secondary-container border-secondary/20",
  LOW: "bg-surface-container text-on-surface-variant border-outline-variant",
};

export default function RiskRegisterWidget({ risks }: RiskRegisterWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">warning</span>
        Risk Register
      </h2>

      {risks.length === 0 ? (
        <p className="font-label-md text-label-md text-on-surface-variant">No open risks.</p>
      ) : (
        <div className="space-y-3">
          {risks.map((risk) => (
            <div
              key={risk.id}
              className="p-4 bg-white border border-slate-200 rounded-lg hover:border-primary transition-colors"
            >
              <div className="flex justify-between items-start gap-3 mb-1">
                <p className="font-label-md text-label-md font-semibold text-on-surface">
                  {risk.description}
                </p>
                <span
                  className={`shrink-0 inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${
                    severityColor[risk.severity] || severityColor.LOW
                  }`}
                >
                  {risk.severity}
                </span>
              </div>
              <p className="font-label-sm text-label-sm text-on-surface-variant">
                {risk.category || "General"}
                {risk.owner ? ` · Owner: ${risk.owner}` : ""}
              </p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
