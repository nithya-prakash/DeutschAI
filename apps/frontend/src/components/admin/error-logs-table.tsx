import type { ErrorLogEntryRead } from "@/types/api";

export function ErrorLogsTable({ entries }: { entries: ErrorLogEntryRead[] }) {
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">No errors logged — nice.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-border text-xs uppercase tracking-wide text-muted-foreground">
            <th className="py-2 pr-4 font-medium">When</th>
            <th className="py-2 pr-4 font-medium">Request</th>
            <th className="py-2 pr-4 font-medium">Exception</th>
            <th className="py-2 pr-4 font-medium">Message</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.id} className="border-b border-border last:border-0 align-top">
              <td className="whitespace-nowrap py-2 pr-4">
                {new Date(e.created_at).toLocaleString()}
              </td>
              <td className="py-2 pr-4">
                {e.method} {e.path}
              </td>
              <td className="py-2 pr-4">{e.exception_type}</td>
              <td className="max-w-xs truncate py-2 pr-4" title={e.message}>
                {e.message}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
