import { CheckCircle2, XCircle } from "lucide-react";

import type { SystemHealth } from "@/types/api";
import { cn } from "@/lib/utils";

function StatusDot({ ok }: { ok: boolean }) {
  const Icon = ok ? CheckCircle2 : XCircle;
  return (
    <Icon className={cn("h-4 w-4", ok ? "text-primary" : "text-destructive")} />
  );
}

export function SystemHealthPanel({ health }: { health: SystemHealth }) {
  const configured = [
    { name: "ANTHROPIC_API_KEY", ok: health.anthropic_configured },
    { name: "SENTRY_DSN", ok: health.sentry_configured },
    { name: "OTEL_EXPORTER_OTLP_ENDPOINT", ok: health.otel_configured },
    { name: "Whisper model cached", ok: health.whisper_model_cached },
    { name: "Piper model cached", ok: health.piper_model_cached },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <p className="mb-2 text-sm font-medium text-muted-foreground">Services</p>
        <ul className="flex flex-col gap-2">
          {health.services.map((s) => (
            <li
              key={s.name}
              className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
            >
              <span className="capitalize">{s.name}</span>
              <StatusDot ok={s.reachable} />
            </li>
          ))}
        </ul>
      </div>
      <div>
        <p className="mb-2 text-sm font-medium text-muted-foreground">Configuration</p>
        <ul className="flex flex-col gap-2">
          {configured.map((c) => (
            <li
              key={c.name}
              className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
            >
              <span>{c.name}</span>
              <StatusDot ok={c.ok} />
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
