import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Chat With PDF",
  description: "Upload PDF files and chat with semantic retrieval."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
