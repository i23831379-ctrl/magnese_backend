import { useRef, useState } from 'react'
import { CheckCircle2, Clock3, Satellite, Upload, Waves } from 'lucide-react'
import { api } from '../api'
export default function Data() {
  const fileInput = useRef<HTMLInputElement>(null)
  const [uploadMessage, setUploadMessage] = useState('')
  const [uploadError, setUploadError] = useState('')
  const rows=[['Sentinel-2 multispectral','Satellite','Demo inventory · 12 scenes','Demo'],['Geological formations','Geology','Demo inventory · 1 layer','Demo'],['DEM terrain model','Terrain','Demo inventory · 30 m','Demo'],['Manganese training data','ML','No validated labelled dataset connected','Unavailable']]
  const handleTrainingUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    setUploadMessage('Validating manganese training CSV...')
    setUploadError('')
    try {
      const result = await api.uploadManganeseData(await file.text())
      setUploadMessage(`${result.record_count} manganese training records validated. Features: ${result.feature_columns.join(', ') || 'coordinates only'}.`)
    } catch (error) {
      setUploadMessage('')
      setUploadError(error instanceof Error ? error.message : 'Training CSV validation failed.')
    }
  }

  return <div className="space-y-5"><div><h1 className="text-xl font-semibold text-slate-900">Data & Processing</h1><p className="mt-1 text-sm text-slate-500">Inputs, derived features and processing jobs used by the manganese demo workspace.</p></div>
    <input ref={fileInput} type="file" accept=".csv,text/csv" onChange={handleTrainingUpload} className="hidden" />
    <div className="grid gap-4 md:grid-cols-3"><Action icon={Upload} title="Validate training CSV" text="Manganese-labelled CSV records" onClick={()=>fileInput.current?.click()}/><Action icon={Satellite} title="Satellite search" text="Sentinel-2 / Landsat scenes"/><Action icon={Waves} title="Terrain analysis" text="Elevation, slope and aspect"/></div>
    {(uploadMessage || uploadError) && <div className={`rounded-lg border px-4 py-3 text-sm ${uploadError?'border-red-200 bg-red-50 text-red-700':'border-cyan-200 bg-cyan-50 text-cyan-800'}`}>{uploadError || uploadMessage}</div>}
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm"><div className="border-b border-slate-200 p-5"><h2 className="font-semibold">Workspace datasets</h2></div><div className="divide-y divide-slate-100">{rows.map(r=><div key={r[0]} className="flex items-center justify-between p-4"><div><div className="text-sm font-medium">{r[0]}</div><div className="mt-0.5 text-xs text-slate-500">{r[1]} · {r[2]}</div></div><span className={`flex items-center gap-1 text-xs font-medium ${r[3]==='Demo'?'text-amber-700':'text-slate-500'}`}><CheckCircle2 size={14}/>{r[3]}</span></div>)}</div></div>
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-5"><h2 className="font-semibold text-amber-900">Manganese model data status</h2><p className="mt-2 text-sm leading-6 text-amber-800">No validated manganese-labelled training dataset is connected. Predictions and map rankings remain demo screening outputs until real labelled samples are supplied and independently evaluated.</p></div>
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center gap-2 font-semibold"><Clock3 size={17}/> Recent processing</div><div className="mt-4 flex items-center justify-between rounded-lg bg-slate-50 p-4 text-sm"><span>Feature extraction · Demo AOI</span><span className="text-xs text-emerald-700">Completed</span></div></div>
  </div>
}
function Action({icon:Icon,title,text,onClick}:{icon:any,title:string,text:string,onClick?:()=>void}){return <button onClick={onClick} className="rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm hover:border-slate-300"><Icon size={20} className="text-slate-700"/><div className="mt-4 font-semibold">{title}</div><div className="mt-1 text-xs text-slate-500">{text}</div></button>}
