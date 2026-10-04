import Link from "next/link";
import { ShieldCheck, FileCheck2, UploadCloud, ArrowRight } from "lucide-react";

export default function Home() {
  const cards = [
    { icon: UploadCloud, title: "Private upload", body: "Short-lived presigned uploads go directly to a private S3-compatible bucket. File size and content type are checked." },
    { icon: ShieldCheck, title: "Advisory classification", body: "Local rules flag common patterns. Optional OpenAI analysis runs on the backend and may send a short text sample to OpenAI." },
    { icon: FileCheck2, title: "Signed deletion record", body: "A worker requests object deletion, checks that the key is absent, and signs a JSON and PDF record with RSA-PSS." }
  ];
  return <div className="pb-20">
    <section className="border-b border-slate-800 bg-[radial-gradient(ellipse_at_top,rgba(16,185,129,.15),transparent_60%)] px-6 py-24 text-center md:py-32">
      <div className="mx-auto max-w-5xl"><div className="mb-7 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-xs font-mono uppercase tracking-widest text-emerald-300"><ShieldCheck className="h-4 w-4"/> SecureWipe Cloud</div>
        <h1 className="text-5xl font-extrabold tracking-tight md:text-7xl">Secure Data Sanitization.<br/><span className="text-emerald-300">Verified. Auditable.</span></h1>
        <p className="mx-auto mt-7 max-w-3xl text-lg leading-relaxed text-slate-400">Classify supported text files, queue private object deletion, and produce a signed record with a public verification page. Cloud deletion cannot prove that data has been physically overwritten on provider media.</p>
        <div className="mt-10 flex flex-wrap justify-center gap-4"><Link href="/register" className="flex items-center gap-2 rounded-xl bg-emerald-400 px-7 py-4 font-bold text-slate-950">Create account <ArrowRight className="h-4 w-4"/></Link><Link href="/verify" className="rounded-xl border border-slate-700 bg-slate-900 px-7 py-4 font-semibold">Verify a certificate</Link></div>
      </div>
    </section>
    <section className="mx-auto grid max-w-6xl gap-5 px-6 py-16 md:grid-cols-3">{cards.map(({icon: Icon,title,body})=><article key={title} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-7"><Icon className="mb-5 h-7 w-7 text-emerald-300"/><h2 className="text-xl font-bold">{title}</h2><p className="mt-3 text-sm leading-relaxed text-slate-400">{body}</p></article>)}</section>
    <p className="mx-auto max-w-4xl px-6 text-center text-xs leading-relaxed text-slate-500">This workflow deletes an uploaded cloud object. It does not sanitize the user&apos;s original device, bypass provider backups or versioning, or establish regulatory compliance. Do not upload files unless your organization permits this processing.</p>
  </div>;
}
