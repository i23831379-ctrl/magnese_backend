import type { LucideIcon } from 'lucide-react'
export default function StatCard({ label, value, note, icon: Icon }: { label: string; value: string | number; note: string; icon: LucideIcon }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <div className="flex items-start justify-between">
      <div><div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div><div className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">{value}</div><div className="mt-1 text-xs text-slate-500">{note}</div></div>
      <div className="rounded-lg bg-slate-100 p-2.5 text-slate-600"><Icon size={19}/></div>
    </div>
  </div>
}
