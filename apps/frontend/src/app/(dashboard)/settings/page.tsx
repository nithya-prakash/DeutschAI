"use client";

import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold">Settings</h1>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Choose how DeutschAI looks on this device.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-2">
          {(["light", "dark", "system"] as const).map((option) => (
            <Button
              key={option}
              variant={theme === option ? "default" : "outline"}
              size="sm"
              onClick={() => setTheme(option)}
              className="capitalize"
            >
              {option}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card className="max-w-lg border-dashed">
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>
            The Motivation Agent&apos;s encouragement currently appears as an in-app banner on
            your dashboard after a study gap. Push/email reminders aren&apos;t implemented yet —
            nothing to configure here.
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
}
