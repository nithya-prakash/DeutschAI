"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCurrentUser, useUpdateProfile } from "@/hooks/use-user";

export default function ProfilePage() {
  const { data: user, isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const [fullName, setFullName] = React.useState("");

  React.useEffect(() => {
    if (user) setFullName(user.full_name);
  }, [user]);

  if (isLoading || !user) {
    return <p className="text-muted-foreground">Loading profile…</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold">Profile</h1>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>Personal details</CardTitle>
          <CardDescription>Your email is fixed; everything else can be updated.</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e) => {
              e.preventDefault();
              updateProfile.mutate({ full_name: fullName });
            }}
          >
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" value={user.email} disabled />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="full_name">Full name</Label>
              <Input id="full_name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label>CEFR level</Label>
              <Input value={user.cefr_level} disabled />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label>Learning</Label>
              <Input value={`German (target_language: ${user.target_language})`} disabled />
            </div>

            <Button type="submit" disabled={updateProfile.isPending} className="w-fit">
              {updateProfile.isPending ? "Saving…" : "Save changes"}
            </Button>
            {updateProfile.isSuccess && (
              <p className="text-sm text-primary">Profile updated.</p>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
