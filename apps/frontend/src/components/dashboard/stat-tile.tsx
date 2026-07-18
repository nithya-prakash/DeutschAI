import { Card, CardContent } from "@/components/ui/card";

interface StatTileProps {
  label: string;
  value: React.ReactNode;
  note?: string;
}

export function StatTile({ label, value, note }: StatTileProps) {
  return (
    <Card>
      <CardContent className="p-5">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        <p className="mt-1.5 text-3xl font-semibold leading-none">{value}</p>
        {note && <p className="mt-1.5 text-sm text-muted-foreground">{note}</p>}
      </CardContent>
    </Card>
  );
}
