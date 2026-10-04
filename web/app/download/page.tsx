import { Download, AlertTriangle, CheckCircle2, Terminal } from "lucide-react";

export default function DownloadPage() {
  const downloadUrl =
    process.env.NEXT_PUBLIC_WINDOWS_DOWNLOAD_URL ||
    "https://github.com/Siddartha2006/SecureWipe/releases/latest";

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono uppercase mb-4">
          Windows Portable Executable
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          Download SecureWipe for Windows
        </h1>
        <p className="mt-4 text-slate-400 text-base">
          Optional legacy desktop utility, separate from the browser-based cloud workflow.
        </p>
      </div>

      {/* Main Download Card */}
      <div className="p-8 sm:p-10 rounded-3xl bg-slate-900 border border-slate-800 text-center max-w-2xl mx-auto mb-12 shadow-xl">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center mb-6">
          <Download className="w-8 h-8" />
        </div>

        <h2 className="text-2xl font-bold text-white mb-2">SecureWipe Portable (x64)</h2>
        <p className="text-xs text-slate-400 font-mono mb-6">
          Release target: Windows 10 / 11 (64-bit) • Single Binary (.exe)
        </p>

        <a
          href={downloadUrl}
          className="inline-flex items-center justify-center gap-2.5 w-full sm:w-auto px-10 py-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-base transition shadow-lg shadow-emerald-500/25"
        >
          <Download className="w-5 h-5" /> Download SecureWipePortable.exe
        </a>

        {/* Warning Callout */}
        <div className="mt-8 p-4 rounded-xl bg-amber-950/40 border border-amber-900/60 text-amber-300 text-left text-xs flex gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <strong className="block text-amber-200 mb-1">Destructive Action Warning:</strong>
            Wiping is destructive. Actual recovery depends on the storage device and filesystem; keep backups of anything you may need.
            Ensure you have complete backups of any data you do not intend to destroy permanently.
          </div>
        </div>
      </div>

      {/* Setup Instructions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Execution Instructions
          </h3>
          <ol className="space-y-3 text-xs text-slate-300 list-decimal list-inside leading-relaxed font-mono">
            <li>Download <code className="text-emerald-400">SecureWipePortable.exe</code> to your machine.</li>
            <li>Launch the executable (accept Windows SmartScreen prompt if requested).</li>
            <li>Optionally provide your <code className="text-emerald-400">OPENAI_API_KEY</code> environment variable if using AI detection.</li>
            <li>Click <strong>Choose Directory</strong> or select individual target files.</li>
            <li>Configure passes (1-35) and wipe pattern (Zero, Random, DoD 5220.22-M).</li>
            <li>Confirm the prompt and initiate the wipe process.</li>
            <li>Download your digitally signed PDF and JSON verification certificate.</li>
          </ol>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-cyan-400" /> Building From Source
          </h3>
          <p className="text-xs text-slate-400 mb-4 leading-relaxed">
            If you prefer running from Python source or compiling the executable yourself:
          </p>
          <pre className="p-4 rounded-xl bg-slate-950 text-slate-300 font-mono text-[11px] overflow-x-auto border border-slate-800/80 leading-relaxed">
{`git clone https://github.com/Siddartha2006/SecureWipe.git
cd SecureWipe
python -m venv venv
.\\venv\\Scripts\\activate
pip install -r requirements.txt pyinstaller
python main.py

# Or build standalone executable:
python build_portable.py`}
          </pre>
        </div>
      </div>
    </div>
  );
}
