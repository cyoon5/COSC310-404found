"use client";

import "./globals.css";
import NavBar from "@/components/NavBar";
import { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <NavBar />
        <main className="main-container">{children}</main>
      </body>
    </html>
  );
}
