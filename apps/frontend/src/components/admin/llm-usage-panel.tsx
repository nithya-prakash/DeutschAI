import type { LLMUsageSummary } from "@/types/api";

export function LLMUsagePanel({ usage }: { usage: LLMUsageSummary }) {
  if (usage.by_agent.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No LLM calls recorded yet — this fills in once ANTHROPIC_API_KEY is set and the Tutor or
        Conversation agents are actually used.
      </p>
    );
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-border text-xs uppercase tracking-wide text-muted-foreground">
            <th className="py-2 pr-4 font-medium">Agent</th>
            <th className="py-2 pr-4 font-medium">Calls</th>
            <th className="py-2 pr-4 font-medium">Input tokens</th>
            <th className="py-2 pr-4 font-medium">Output tokens</th>
          </tr>
        </thead>
        <tbody>
          {usage.by_agent.map((a) => (
            <tr key={a.agent_name} className="border-b border-border last:border-0">
              <td className="py-2 pr-4 capitalize">{a.agent_name}</td>
              <td className="py-2 pr-4">{a.call_count}</td>
              <td className="py-2 pr-4">{a.input_tokens.toLocaleString()}</td>
              <td className="py-2 pr-4">{a.output_tokens.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
