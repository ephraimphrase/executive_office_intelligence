import React from "react";

export default function WelcomeHeader() {
  return (
    <section className="mb-10 animate-[fadeIn_0.5s_ease-out]">
      <p className="font-label-md text-label-md text-on-surface-variant mb-2">
        Wednesday, October 25, 2023
      </p>
      <h1 className="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg text-primary mb-4">
        Good Morning, Sarah
      </h1>
      <div className="inline-flex items-start md:items-center gap-3 bg-secondary-fixed/50 px-4 py-3 rounded-lg border border-secondary-fixed-dim/30">
        <span
          className="material-symbols-outlined text-primary mt-0.5 md:mt-0"
          style={{ fontVariationSettings: "'FILL' 1" }}
        >
          auto_awesome
        </span>
        <p className="font-body-md text-body-md text-on-surface">
          <strong className="font-semibold text-primary">AI Briefing:</strong> You
          have 5 meetings today and 2 critical decisions pending.
        </p>
      </div>
    </section>
  );
}
