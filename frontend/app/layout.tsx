import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { MarriottHeader } from "@/components/chrome/MarriottHeader";
import { MarriottFooter } from "@/components/chrome/MarriottFooter";
import { AuthBootstrapper } from "@/components/auth/AuthBootstrapper";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Marriott Bonvoy | Find Your Stay",
  description:
    "Book hotels, resorts, and homes worldwide with Marriott Bonvoy. Personalized eco ratings, arrival briefs, and pet-friendly travel — additive features layered onto the Marriott experience.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} h-full`}>
      <body className="min-h-full flex flex-col bg-white text-[var(--color-foreground)]">
        <AuthBootstrapper />
        <MarriottHeader />
        <main className="flex-1">{children}</main>
        <MarriottFooter />
      </body>
    </html>
  );
}
