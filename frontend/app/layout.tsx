import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentID Dashboard",
  description: "Identity infrastructure for AI agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
