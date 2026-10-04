"use client";

import Link from "next/link";
import { useState } from "react";
import { ShieldCheck, Menu, X, FileCheck, BookOpen, Info, LayoutDashboard, UploadCloud } from "lucide-react";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 group-hover:border-emerald-500/40 transition">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold tracking-tight text-white text-base">SecureWipe</span>
            <span className="text-[10px] text-slate-400 tracking-wider uppercase font-mono">E-Waste Security</span>
          </div>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-7 text-sm font-medium text-slate-300">
          <Link href="/upload" className="hover:text-emerald-400 transition flex items-center gap-1.5">
            <UploadCloud className="w-4 h-4" /> Upload
          </Link>
          <Link href="/dashboard" className="hover:text-emerald-400 transition flex items-center gap-1.5"><LayoutDashboard className="w-4 h-4"/> Dashboard</Link>
          <Link href="/certificates" className="hover:text-emerald-400 transition">Certificates</Link>
          <Link href="/verify" className="hover:text-emerald-400 transition flex items-center gap-1.5">
            <FileCheck className="w-4 h-4" /> Verify
          </Link>
          <Link href="/docs" className="hover:text-emerald-400 transition flex items-center gap-1.5">
            <BookOpen className="w-4 h-4" /> Documentation
          </Link>
          <Link href="/about" className="hover:text-emerald-400 transition flex items-center gap-1.5">
            <Info className="w-4 h-4" /> About
          </Link>
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/login"
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition shadow-sm shadow-emerald-500/20"
          >
            Sign in
          </Link>
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-slate-400 hover:text-white focus:outline-none"
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Nav dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-800 bg-slate-900/95 px-4 pt-2 pb-6 space-y-3">
          <Link
            href="/upload"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2 py-2 text-slate-300 hover:text-emerald-400"
          >
            <UploadCloud className="w-4 h-4" /> Upload a file
          </Link>
          <Link
            href="/verify"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2 py-2 text-slate-300 hover:text-emerald-400"
          >
            <FileCheck className="w-4 h-4" /> Verify Certificate
          </Link>
          <Link
            href="/docs"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2 py-2 text-slate-300 hover:text-emerald-400"
          >
            <BookOpen className="w-4 h-4" /> Documentation
          </Link>
          <Link
            href="/about"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2 py-2 text-slate-300 hover:text-emerald-400"
          >
            <Info className="w-4 h-4" /> About SecureWipe
          </Link>
        </div>
      )}
    </header>
  );
}
