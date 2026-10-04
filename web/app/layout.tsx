import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";

const appUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(appUrl),
  title: "SecureWipe | Secure Data Sanitization. Verified. Auditable.",
  description:
    "Classify supported text uploads, request private cloud object deletion, and verify signed audit records. Cloud deletion does not prove physical media overwrite.",
  keywords: [
    "SecureWipe",
    "Data destruction",
    "Secure wiping",
    "E-waste sanitization",
    "Certificate verification",
    "Cryptographic audit",
  ],
  authors: [{ name: "SecureWipe Security Team" }],
  openGraph: {
    title: "SecureWipe | Secure Data Destruction Platform",
    description: "Advisory classification and signed cloud object deletion records.",
    url: appUrl,
    siteName: "SecureWipe",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SecureWipe | Secure Data Sanitization. Verified. Auditable.",
    description: "Secure data sanitization. Verified. Auditable.",
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col bg-slate-950 text-slate-100 antialiased selection:bg-emerald-500 selection:text-white">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
