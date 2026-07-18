import type { Metadata } from "next";

import { Providers } from "@/components/layout/providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "DeutschAI — Learn German, Personalized",
  description: "An AI-powered adaptive platform for learning German from A1 to C1.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
