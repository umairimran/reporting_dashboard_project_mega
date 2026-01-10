import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";

export const metadata: Metadata = {
  title: "Gold Standard - Analytics Dashboard",
  description:
    "Paid Media Analytics for CTV, Facebook, and Vibe platforms",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased bg-white text-slate-900">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
