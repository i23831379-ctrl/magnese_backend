import { ArrowUpRight, Map, Target, Database, Activity, CheckCircle2 } from 'lucide-react'
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import StatCard from '../components/StatCard'
import type { Target as TargetType } from '../types'
import type { ModelStatus } from '../types'

export default function Dashboard({ targets, highCount, modelStatus, onExplore }: { targets: TargetType[]; highCount: number; modelStatus: ModelStatus | null; onExplore: () => void }) {
  const data = [{name:'High', value: targets.filter(t=>t.zone==='HIGH').length},{name:'Medium',value:targets.filter(t=>t.zone==='MEDIUM').length},{name:'Low',value:targets.filter(t=>t.zone==='LOW').length}]
  const averageProbability = targets.length ? Math.round(targets.reduce((sum, target) => sum + target.manganese_probability, 0) / targets.length * 100) : 0
  return <div className="space-y-6">
    <section className="rounded-2xl bg-[#111b2e] p-6 text-white shadow-sm lg:p-8">
      <div className="max-w-3xl">
        <div className="mb-3 flex items-center gap-2 text-xs font-medium uppercase tracking-[.16em] text-cyan-300"><Activity size={14}/> Exploration workspace</div>
        <h1 className="text-2xl font-semibold tracking-tight lg:text-3xl">Manganese prospectivity, from evidence to field targets.</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">Fuse satellite, geological and terrain evidence, review model-ranked areas, and send the strongest targets to field validation.</p>
        <button onClick={onExplore} className="mt-6 inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 hover:bg-slate-100">Open GIS Explorer <ArrowUpRight size={16}/></button>
      </div>
    </section>

    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Manganese targets" value={targets.length} note="Demo exploration targets" icon={Target}/>
      <StatCard label="High Mn prospectivity" value={highCount} note="Requires field validation" icon={Map}/>
      <StatCard label="Average Mn prospectivity" value={`${averageProbability}%`} note="Model screening score" icon={Activity}/>
      <StatCard label="Data layers" value="08" note="Satellite, geology & terrain" icon={Database}/>
      <StatCard label="Model status" value={(modelStatus?.status || 'demo').toUpperCase()} note={modelStatus?.message || 'Manganese demo model'} icon={CheckCircle2}/>
    </div>

    <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between"><div><h2 className="font-semibold text-slate-900">Prospectivity distribution</h2><p className="mt-1 text-xs text-slate-500">Current demo target ranking</p></div><span className="text-xs text-slate-400">n = {targets.length}</span></div>
        <div className="mt-5 h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={data}><XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize:12}}/><YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{fontSize:12}}/><Tooltip cursor={{fill:'#f1f5f9'}}/><Bar dataKey="value" radius={[6,6,0,0]} /></BarChart></ResponsiveContainer></div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold text-slate-900">Top targets</h2>
        <p className="mt-1 text-xs text-slate-500">Highest model-estimated priority</p>
        <div className="mt-4 space-y-2">
          {targets.slice().sort((a,b)=>b.score-a.score).slice(0,5).map(t => <div key={t.id} className="flex items-center justify-between rounded-lg border border-slate-100 p-3">
            <div><div className="text-sm font-medium text-slate-800">{t.code} · {t.name}</div><div className="mt-0.5 text-xs text-slate-500">{t.geology}</div></div>
            <div className="text-right"><div className="text-sm font-semibold text-slate-900">{t.score}</div><div className="text-[10px] uppercase text-slate-400">score</div></div>
          </div>)}
        </div>
      </section>
    </div>
  </div>
}
