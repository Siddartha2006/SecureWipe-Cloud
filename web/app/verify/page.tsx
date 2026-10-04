"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileCheck, Search, QrCode } from "lucide-react";

export default function VerifyIndexPage() {
  const [certId, setCertId] = useState("");
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = certId.trim().toUpperCase();
    if (trimmed) {
      router.push(`/verify/${trimmed}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
      <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center mb-6">
        <FileCheck className="w-8 h-8" />
      </div>

      <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
        Certificate Verification
      </h1>
      <p className="text-slate-400 text-base max-w-xl mx-auto mb-10">
        Enter a SecureWipe certificate ID to inspect its signed record. Verification is cryptographic; it does not establish physical media overwrite.
      </p>

      {/* Input Form */}
      <form onSubmit={handleSearch} className="max-w-md mx-auto mb-10 flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={certId}
            onChange={(e) => setCertId(e.target.value)}
            placeholder="e.g. SW-20261004-A1B2C3D4E5"
            maxLength={32}
            className="w-full px-4 py-3.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 font-mono text-sm focus:outline-none focus:border-emerald-500 uppercase"
            required
          />
        </div>
        <button
          type="submit"
          className="px-6 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition flex items-center gap-2"
        >
          <Search className="w-4 h-4" /> Verify
        </button>
      </form>

      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 text-left max-w-lg mx-auto text-xs text-slate-400">
        <div className="flex items-center gap-2 text-slate-200 font-semibold mb-2">
          <QrCode className="w-4 h-4 text-emerald-400" /> Automated Verification
        </div>
        <p>
          Public verification displays the signed metadata and signature result. Do not treat it as proof of physical media sanitization.
        </p>
      </div>
    </div>
  );
}
