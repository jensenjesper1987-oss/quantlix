import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/nav";

export const metadata: Metadata = {
  title: "Quantlix — Deploy AI models in seconds",
  description:
    "The simplest way to run AI workloads without cloud complexity. Developer-first, EU-hosted, predictable pricing.",
  icons: {
    icon: "/icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen font-sans antialiased">
        <Nav />
        {children}
      </body>
    </html>
  );
}
