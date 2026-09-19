import { Download, FileText, ShieldCheck } from 'lucide-react'
import type { Target } from '../types'
export default function Reports({targets}:{targets:Target[]}) {
  return <div className="space-y-5"><div><h1 className="text-xl font-semibold text-slate-900">Reports</h1><p className="mt-1 text-sm text-slate-500">Generate concise exploration outputs for technical review.</p></div>
  <div className="grid gap-4 md:grid-cols-2"><Report title="Prospectivity summary" desc={`Summary of ${targets.length} ranked demo targets and model-estimated zones.`} onDownload={()=>downloadCsv('manganese-prospectivity-summary.csv', summaryRows(targets))}/><Report title="Field validation sheet" desc="Coordinates, scores, confidence and suggested review factors." onDownload={()=>downloadCsv('manganese-field-validation-sheet.csv', validationRows(targets))}/></div>
  <div className="rounded-xl border border-amber-200 bg-amber-50 p-5"><div className="flex items-center gap-2 font-semibold text-amber-900"><ShieldCheck size={18}/> Validation requirement</div><p className="mt-2 text-sm leading-6 text-amber-800">Reports clearly separate model output from geological confirmation. No target should be treated as a proven reserve without field evidence, laboratory assays and appropriate drilling.</p></div>
  </div>
}
function Report({title,desc,onDownload}:{title:string,desc:string,onDownload:()=>void}){return <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-start justify-between"><div className="rounded-lg bg-slate-100 p-2.5"><FileText size={19}/></div><button onClick={onDownload} className="rounded-lg border border-slate-200 p-2 hover:bg-slate-50" title={`Download ${title}`}><Download size={17}/></button></div><h2 className="mt-5 font-semibold">{title}</h2><p className="mt-1 text-sm leading-6 text-slate-500">{desc}</p></div>}

type CsvRow = Record<string, string | number>

function summaryRows(targets: Target[]): CsvRow[] {
  return targets.map(target => ({
    mineral: target.mineral,
    target_id: target.code,
    name: target.name,
    latitude: target.latitude,
    longitude: target.longitude,
    manganese_probability: target.manganese_probability,
    classification: target.classification,
    priority: target.priority,
    model_status: target.model_status,
  }))
}

function validationRows(targets: Target[]): CsvRow[] {
  return targets.map(target => ({
    target_id: target.code,
    name: target.name,
    latitude: target.latitude,
    longitude: target.longitude,
    manganese_probability: target.manganese_probability,
    confidence: target.confidence,
    classification: target.classification,
    priority: target.priority,
    geology: target.geology,
    evidence_variations: target.factors.join(' | '),
    status: target.status,
    recommended_next_action: 'Field validation recommended before drilling',
  }))
}

function downloadCsv(filename: string, rows: CsvRow[]) {
  if (rows.length === 0) return
  const headers = Object.keys(rows[0])
  const escape = (value: string | number) => `"${String(value).replaceAll('"', '""')}"`
  const csv = [headers.join(','), ...rows.map(row => headers.map(header => escape(row[header])).join(','))].join('\n')
  const link = document.createElement('a')
  link.href = URL.createObjectURL(new Blob([csv], {type: 'text/csv;charset=utf-8'}))
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}
