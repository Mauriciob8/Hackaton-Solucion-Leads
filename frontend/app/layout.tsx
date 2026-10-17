import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Motor de Leads — Intent-Based Admin Dashboard",
  description:
    "Plataforma inteligente de prospección: detección basada en dolor, micro-sondeos RAG y control atómico de Unit Economics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#f8f9fc] text-slate-800">
        {children}
        {/* Widget embebido del agente de texto de Dapta */}
        <Script
          src="https://widget-v2.dapta.ai/agent.min.js?agentId=a2f51962-1754-4ff4-a5d3-0082625607cc"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
