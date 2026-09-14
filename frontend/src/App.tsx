import { useEffect, useMemo, useState } from 'react'
import 'maplibre-gl/dist/maplibre-gl.css'
import { BarChart3, Bell, ChevronRight, CircleHelp, Compass, Database, FileText, LayoutDashboard, LogOut, Menu, Mountain, Settings, ShieldCheck, Target, X } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Explorer from './pages/Explorer'
import Targets from './pages/Targets'
import Data from './pages/Data'
import Reports from './pages/Reports'
import SettingsPage from './pages/Settings'
import type { ModelStatus, Target as TargetType } from './types'
import { api } from './api'

type Page = 'dashboard' | 'explorer' | 'targets' | 'data' | 'reports' | 'settings'

const nav = [
  { id: 'dashboard' as Page, label: 'Overview', icon: LayoutDashboard },
  { id: 'explorer' as Page, label: 'GIS Explorer', icon: Compass },
  { id: 'targets' as Page, label: 'Priority Targets', icon: Target },
  { id: 'data' as Page, label: 'Data & Processing', icon: Database },
  { id: 'reports' as Page, label: 'Reports', icon: FileText },
]

export default function App() {
  const [page, setPage] = useState<Page>('dashboard')
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [targets, setTargets] = useState<TargetType[]>([])
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.targets(), api.manganeseModelStatus()])
      .then(([nextTargets, nextModelStatus]) => { setTargets(nextTargets); setModelStatus(nextModelStatus) })
      .catch(e => setError(e.message))
  }, [])

  const high = useMemo(() => targets.filter(t => t.zone === 'HIGH').length, [targets])

  const content = {
    dashboard: <Dashboard targets={targets} highCount={high} modelStatus={modelStatus} onExplore={() => setPage('explorer')} />,
    explorer: <Explorer targets={targets} />,
    targets: <Targets targets={targets} />,
    data: <Data />,
    reports: <Reports targets={targets} />,
    settings: <SettingsPage />,
  }[page]

  return (
    <div className="min-h-screen bg-[#f5f7fa] text-slate-800">
      <aside className={`fixed inset-y-0 left-0 z-40 hidden border-r border-slate-200 bg-[#0c1424] text-white transition-all lg:block ${collapsed ? 'w-[76px]' : 'w-[246px]'}`}>
        <Sidebar page={page} setPage={setPage} collapsed={collapsed} setCollapsed={setCollapsed} />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-slate-950/50" onClick={() => setMobileOpen(false)} />
          <aside className="relative h-full w-[270px] bg-[#0c1424] text-white">
            <Sidebar page={page} setPage={(p) => { setPage(p); setMobileOpen(false) }} collapsed={false} setCollapsed={() => {}} />
          </aside>
        </div>
      )}

      <main className={`min-h-screen transition-all ${collapsed ? 'lg:pl-[76px]' : 'lg:pl-[246px]'}`}>
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur lg:px-7">
          <div className="flex items-center gap-3">
            <button className="rounded-lg p-2 hover:bg-slate-100 lg:hidden" onClick={() => setMobileOpen(true)}><Menu size={21}/></button>
            <div>
              <div className="text-sm font-semibold text-slate-900">{page === 'explorer' ? 'GIS Explorer' : nav.find(n => n.id === page)?.label || 'Settings'}</div>
              <div className="hidden text-xs text-slate-500 sm:block">Manganese prospectivity workspace</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-[11px] font-medium text-amber-700 sm:inline-flex">DEMO DATA</span>
            <button className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"><Bell size={19}/></button>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-xs font-semibold text-white">HV</div>
          </div>
        </header>

        {error && (
          <div className="mx-4 mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 lg:mx-7">
            Backend is not reachable. Start FastAPI on port 8000. The UI can still be inspected, but live target data will be unavailable.
          </div>
        )}
        <div className="p-4 lg:p-7">{content}</div>
      </main>
    </div>
  )
}

function Sidebar({ page, setPage, collapsed, setCollapsed }: { page: Page; setPage: (p: Page) => void; collapsed: boolean; setCollapsed: (v: boolean) => void }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center gap-3 border-b border-white/10 px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-300"><Mountain size={20}/></div>
        {!collapsed && <div><div className="text-sm font-bold tracking-wide">MANGANEX AI</div><div className="text-[10px] uppercase tracking-[.18em] text-slate-400">Exploration Intelligence</div></div>}
      </div>
      <div className="px-3 py-5">
        {!collapsed && <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">Workspace</div>}
        {nav.map(item => {
          const Icon = item.icon
          const active = page === item.id
          return <button key={item.id} onClick={() => setPage(item.id)} title={item.label} className={`mb-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${active ? 'bg-white/10 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-slate-100'}`}>
            <Icon size={18}/>{!collapsed && <span>{item.label}</span>}{!collapsed && active && <ChevronRight size={15} className="ml-auto text-slate-500"/>}
          </button>
        })}
      </div>
      <div className="mt-auto space-y-1 border-t border-white/10 p-3">
        <button onClick={() => setPage('settings')} className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"><Settings size={18}/>{!collapsed && 'Settings'}</button>
        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"><CircleHelp size={18}/>{!collapsed && 'Help & documentation'}</button>
        {!collapsed && <div className="mt-3 rounded-lg bg-white/5 p-3 text-xs text-slate-400"><div className="mb-1 flex items-center gap-2 text-slate-300"><ShieldCheck size={14}/> Decision support</div>AI scores are estimates and require field validation.</div>}
        <button onClick={() => setCollapsed(!collapsed)} className="hidden w-full items-center justify-center rounded-lg py-2 text-slate-500 hover:bg-white/5 lg:flex"><Menu size={18}/></button>
      </div>
    </div>
  )
}
