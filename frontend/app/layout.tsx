import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BizuHub",
  description: "Recomendações de filmes, séries e livros com IA",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
