import React from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: string;
  iconBgColor?: string;
  iconTextColor?: string;
  valueColor?: string;
  trend?: string;
  hasAlertBackground?: boolean;
}

export default function MetricCard({
  title,
  value,
  icon,
  iconBgColor = "bg-surface-container",
  iconTextColor = "text-primary group-hover:bg-primary group-hover:text-white",
  valueColor = "text-primary",
  trend,
  hasAlertBackground = false,
}: MetricCardProps) {
  return (
    <div className="glass-card rounded-xl p-card-padding flex flex-col hover:bg-slate-50/50 transition-colors cursor-pointer group relative overflow-hidden">
      {hasAlertBackground && (
        <div className="absolute top-0 right-0 w-16 h-16 bg-error/5 rounded-bl-full -mr-4 -mt-4"></div>
      )}

      <div className="flex justify-between items-start mb-6 relative z-10">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${iconBgColor} ${iconTextColor}`}
        >
          <span className="material-symbols-outlined">{icon}</span>
        </div>
        {trend && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            {trend}
          </span>
        )}
      </div>

      <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-1 relative z-10">
        {title}
      </h3>
      <div className="flex items-baseline gap-3 relative z-10">
        <span className={`font-display-lg text-display-lg ${valueColor}`}>
          {value}
        </span>
      </div>
    </div>
  );
}
