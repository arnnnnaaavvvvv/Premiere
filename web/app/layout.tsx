import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Premiere | Automated MNC-Style Product Launch Video Generator",
  description: "Turn any live URL and GitHub repo into a high-octane 1080p product launch video.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#050505] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
