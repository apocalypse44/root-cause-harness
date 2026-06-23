import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/lib/query-provider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Root Cause Harness",
  description: "AI-powered root cause investigation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <QueryProvider>
          <div className="min-h-screen bg-background">
            <header className="border-b">
              <div className="container mx-auto px-4 py-3 flex items-center gap-6">
                <h1 className="text-xl font-bold">Root Cause Harness</h1>
                <nav className="flex gap-4 text-sm">
                  <a href="/" className="hover:underline">Services</a>
                  <a href="/incidents" className="hover:underline">Incidents</a>
                </nav>
              </div>
            </header>
            <main className="container mx-auto px-4 py-6">{children}</main>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
