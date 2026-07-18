import { Heart } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import type { MotivationMessage } from "@/types/api";

export function MotivationBanner({ message }: { message: MotivationMessage }) {
  return (
    <Card className="border-primary/40">
      <CardContent className="flex items-start gap-3 p-5">
        <Heart className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
        <div>
          <p className="text-sm font-medium">{message.headline}</p>
          <p className="text-sm text-muted-foreground">{message.body}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Suggested for today: <span className="font-medium">{message.suggested_minutes} min</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
