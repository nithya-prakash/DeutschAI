"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAddWord } from "@/hooks/use-vocabulary";

export function AddWordForm() {
  const { mutate, isPending } = useAddWord();
  const [german, setGerman] = React.useState("");
  const [english, setEnglish] = React.useState("");
  const [example, setExample] = React.useState("");

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!german.trim() || !english.trim()) return;
    mutate(
      { german: german.trim(), english: english.trim(), example_sentence: example.trim() || undefined },
      {
        onSuccess: () => {
          setGerman("");
          setEnglish("");
          setExample("");
        },
      }
    );
  };

  return (
    <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
      <div className="flex min-w-[140px] flex-col gap-1.5">
        <Label htmlFor="german">German</Label>
        <Input id="german" value={german} onChange={(e) => setGerman(e.target.value)} placeholder="das Haus" />
      </div>
      <div className="flex min-w-[140px] flex-col gap-1.5">
        <Label htmlFor="english">English</Label>
        <Input id="english" value={english} onChange={(e) => setEnglish(e.target.value)} placeholder="the house" />
      </div>
      <div className="flex min-w-[220px] flex-1 flex-col gap-1.5">
        <Label htmlFor="example">Example sentence (optional)</Label>
        <Input
          id="example"
          value={example}
          onChange={(e) => setExample(e.target.value)}
          placeholder="Das Haus ist groß."
        />
      </div>
      <Button type="submit" disabled={isPending}>
        {isPending ? "Adding…" : "Add word"}
      </Button>
    </form>
  );
}
