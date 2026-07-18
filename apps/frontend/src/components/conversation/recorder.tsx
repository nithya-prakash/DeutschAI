"use client";

import * as React from "react";
import { Mic, Square } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface RecorderProps {
  onRecorded: (audio: Blob) => void;
  disabled?: boolean;
}

export function Recorder({ onRecorded, disabled }: RecorderProps) {
  const [isRecording, setIsRecording] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const chunksRef = React.useRef<Blob[]>([]);

  const startRecording = async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        stream.getTracks().forEach((track) => track.stop());
        onRecorded(blob);
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch {
      setError("Couldn't access the microphone — check your browser permissions.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <Button
        type="button"
        size="lg"
        variant={isRecording ? "destructive" : "default"}
        disabled={disabled}
        onClick={isRecording ? stopRecording : startRecording}
        className={cn("h-16 w-16 rounded-full p-0", isRecording && "animate-pulse")}
      >
        {isRecording ? <Square className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
      </Button>
      <p className="text-xs text-muted-foreground">
        {isRecording ? "Recording — tap to stop" : "Tap to speak"}
      </p>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
