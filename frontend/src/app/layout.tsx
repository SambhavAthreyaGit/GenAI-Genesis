import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "GenAI Genesis | PCB Workspace",
  description: "AI-powered PCB and schematic generation from natural language",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
        <Script
          src="https://kicanvas.org/kicanvas/kicanvas.js"
          type="module"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
