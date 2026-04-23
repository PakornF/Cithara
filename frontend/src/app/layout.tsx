import type { Metadata } from "next";
import { Libre_Baskerville, Source_Sans_3 } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/Providers";
import { AuthNav } from "@/components/AuthNav";

const headingFont = Libre_Baskerville({
  weight: ["400", "700"],
  variable: "--font-heading",
  subsets: ["latin"],
});

const bodyFont = Source_Sans_3({
  variable: "--font-body",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Cithara – AI Song Generation",
  description: "Create and share AI-generated songs with Cithara",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${headingFont.variable} ${bodyFont.variable} h-full antialiased`}
    >
      <body className="min-h-screen flex flex-col bg-stone-950 text-stone-100 font-sans">
        <Providers>
          <AuthNav />
          <main className="flex-1">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
