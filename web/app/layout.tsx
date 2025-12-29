import type { Metadata } from "next";
import "./globals.css";
import "katex/dist/katex.min.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Rocket Design Studio",
  description: "Advanced Rocket Engine Design Tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen flex">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}

