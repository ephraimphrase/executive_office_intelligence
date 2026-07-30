import React from "react";

export type CalendarViewMode = "week" | "month" | "committee";

interface CalendarViewSwitcherProps {
  view: CalendarViewMode;
  onChange: (view: CalendarViewMode) => void;
}

const OPTIONS: { value: CalendarViewMode; label: string }[] = [
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
  { value: "committee", label: "Committee" },
];

export default function CalendarViewSwitcher({ view, onChange }: CalendarViewSwitcherProps) {
  return (
    <div className="flex bg-surface-container rounded-lg p-1 mr-4">
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-4 py-1.5 text-label-md rounded-md transition-colors ${
            view === opt.value
              ? "bg-white shadow-sm font-semibold text-primary"
              : "text-on-surface-variant hover:text-primary"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
