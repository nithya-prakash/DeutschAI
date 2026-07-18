"use client";

import * as React from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogStudySession } from "@/hooks/use-dashboard";

const schema = z.object({
  duration_minutes: z.coerce.number().min(1).max(600),
  note: z.string().max(500).optional(),
});
type FormValues = z.infer<typeof schema>;

export function LogSessionForm() {
  const { mutate, isPending, isSuccess } = useLogStudySession();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { duration_minutes: 45, note: "" },
  });

  const onSubmit = (values: FormValues) => {
    mutate(
      { duration_minutes: values.duration_minutes, note: values.note || undefined },
      { onSuccess: () => reset({ duration_minutes: 45, note: "" }) }
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-wrap items-end gap-4">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="duration_minutes">Minutes studied</Label>
        <Input
          id="duration_minutes"
          type="number"
          className="w-24"
          {...register("duration_minutes")}
        />
        {errors.duration_minutes && (
          <p className="text-xs text-destructive">{errors.duration_minutes.message}</p>
        )}
      </div>

      <div className="flex min-w-[220px] flex-1 flex-col gap-1.5">
        <Label htmlFor="note">Note (optional)</Label>
        <Input id="note" placeholder="e.g. reviewed Akkusativ" {...register("note")} />
      </div>

      <Button type="submit" disabled={isPending}>
        {isPending ? "Logging…" : "Log today"}
      </Button>

      {isSuccess && (
        <p className="basis-full text-sm text-primary" role="status">
          Session logged — nice work!
        </p>
      )}
    </form>
  );
}
