import Link from "next/link";
import { ShieldAlert, Code2, ExternalLink } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950 text-slate-400 text-xs">
      {/* Permanent Deletion Caution Strip */}
      <div className="bg-amber-950/30 border-b border-amber-900/30 py-3 px-4">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 text-amber-400 font-mono text-[11px] text-center">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>Cloud object deletion is not proof of physical media overwrite or erasure from provider backups and replicas.</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <span className="font-bold tracking-tight text-white text-base">SecureWipe</span>
            <p className="mt-2 text-slate-400 max-w-sm text-sm">
              An open-source project with a cloud workflow for advisory classification, private object deletion, and signed records.
            </p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-3">Platform</h4>
            <ul className="space-y-2">
              <li><Link href="/download" className="hover:text-emerald-400 transition">Windows Client</Link></li>
              <li><Link href="/verify" className="hover:text-emerald-400 transition">Certificate Verifier</Link></li>
              <li><Link href="/docs" className="hover:text-emerald-400 transition">Technical Docs</Link></li>
              <li><Link href="/security" className="hover:text-emerald-400 transition">Security & Data Handling</Link></li>
              <li><Link href="/about" className="hover:text-emerald-400 transition">About</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-3">Resources</h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/Siddartha2006/SecureWipe"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-emerald-400 transition inline-flex items-center gap-1"
                >
                  <Code2 className="w-3.5 h-3.5" /> GitHub Repository <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/Siddartha2006/SecureWipe/releases"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-emerald-400 transition inline-flex items-center gap-1"
                >
                  GitHub Releases <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800/60 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} SecureWipe. Open Source under MIT License.</p>
          <p className="text-slate-500">Signed cloud object deletion records.</p>
        </div>
      </div>
    </footer>
  );
}
