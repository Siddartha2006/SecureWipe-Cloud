import Link from "next/link";
import { BookOpen, UploadCloud, BrainCircuit, FileCheck2 } from "lucide-react";

const steps = [
  { icon: UploadCloud, title: "Upload", body: "After sign-in, select a UTF-8 .txt, .csv, or .json file up to 25 MiB. A short-lived, size-limited S3 form policy sends it directly to private storage." },
  { icon: BrainCircuit, title: "Classify", body: "Rule-based checks inspect common text patterns. If the operator configures OpenAI, up to 12 KiB of text is sent to it for advisory classification. Review the returned categories as fallible guidance." },
  { icon: FileCheck2, title: "Delete and certify", body: "A queued worker hashes the input, requests object deletion, and checks that storage reports the key missing. It signs metadata and creates downloadable JSON/PDF records." }
];

export default function DocsPage() {
  return <main className="mx-auto max-w-5xl px-6 py-16"><div className="mb-10"><BookOpen className="mb-4 h-8 w-8 text-emerald-300"/><h1 className="text-4xl font-bold">SecureWipe documentation</h1><p className="mt-4 max-w-3xl text-slate-400">A practical guide to the cloud workflow and what its evidence means.</p></div><section className="grid gap-5 md:grid-cols-3">{steps.map(({icon:Icon,title,body})=><article key={title} className="rounded-2xl border border-slate-800 bg-slate-900 p-6"><Icon className="mb-4 h-6 w-6 text-emerald-300"/><h2 className="text-xl font-semibold">{title}</h2><p className="mt-3 text-sm leading-relaxed text-slate-400">{body}</p></article>)}</section><section className="mt-8 rounded-2xl border border-amber-900/60 bg-amber-950/20 p-6"><h2 className="font-semibold text-amber-200">Evidence limitation</h2><p className="mt-2 text-sm leading-relaxed text-slate-300">An object-not-found result is not proof that cloud replicas, provider backups, snapshots, or physical storage media were erased. This service does not overwrite the user&apos;s local disk and does not claim a compliance certification.</p></section><div className="mt-7 flex gap-5 text-sm"><Link className="text-emerald-300 underline" href="/security">Security details</Link><Link className="text-emerald-300 underline" href="/upload">Start an upload</Link></div></main>;
}
