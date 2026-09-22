import type { Metadata } from "next";
import "./style.css";
export const metadata: Metadata = { title: "frontdesk | Ridgeview", description: "Fictional clinic appointment logistics. No clinical data." };
export default function Layout({ children }: Readonly<{children: React.ReactNode}>) { return <html lang="en"><body>{children}</body></html>; }

