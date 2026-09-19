import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import { Layers3, LocateFixed, Maximize2, Minus, Plus, Search, SlidersHorizontal } from 'lucide-react'
import type { Target } from '../types'
import { API_URL } from '../api'

const center: [number, number] = [80.95, 20.55]

const ZONE_RADIUS_KM = 5
const ZONE_SHAPE = [[1, 0], [0.72, 0.68], [0.08, 1], [-0.78, 0.62], [-1, -0.1], [-0.58, -0.82], [0.14, -1], [0.86, -0.58]]

function createDemoProspectivity(targets: Target[]) {
  return {
    type: 'FeatureCollection' as const,
    features: targets.map(target => {
      const radiusLatitude = ZONE_RADIUS_KM / 111
      const radiusLongitude = radiusLatitude / Math.cos(target.latitude * Math.PI / 180)
      const coordinates = ZONE_SHAPE.map(([x, y]) => [target.longitude + x * radiusLongitude, target.latitude + y * radiusLatitude])
      coordinates.push(coordinates[0])
      return {
        type: 'Feature' as const,
        properties: {id:`MNG-ZONE-${String(target.id).padStart(3, '0')}`, target_id:target.code, mineral:'manganese', classification:target.classification, probability:target.manganese_probability, zone:target.zone, model_status:'demo'},
        geometry: {type: 'Polygon' as const, coordinates: [coordinates]},
      }
    }),
  }
}

function getProspectivityColor(classification: string) {
  return ({VERY_HIGH:'#991b1b', HIGH:'#dc2626', MEDIUM:'#d97706', LOW:'#64748b', VERY_LOW:'#cbd5e1'} as Record<string, string>)[classification] || '#94a3b8'
}

export default function Explorer({ targets }: { targets: Target[] }) {
  const demoProspectivity = createDemoProspectivity(targets)
  const mapNode = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)
  const domMarkers = useRef<maplibregl.Marker[]>([])
  const zoneDataRef = useRef(demoProspectivity)
  const [zoneOverlays, setZoneOverlays] = useState<{id:string;classification:string;probability:number;points:string}[]>([])
  const [mapServiceOnline, setMapServiceOnline] = useState(true)
  const [showTargets, setShowTargets] = useState(true)
  const [showProspectivity, setShowProspectivity] = useState(true)
  const [query, setQuery] = useState('')
  const [classificationFilter, setClassificationFilter] = useState('ALL')
  const [priorityFilter, setPriorityFilter] = useState('ALL')

  useEffect(() => {
    if (!mapNode.current || map.current) return
    try {
      const m = new maplibregl.Map({
        container: mapNode.current,
        center,
        zoom: 5.2,
        attributionControl: {} as any,
        style: {
          version: 8,
          sources: {
            osm: {
              type: 'raster',
              tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '© OpenStreetMap contributors'
            },
            prospectivity: {type:'geojson', data:demoProspectivity},
            targets: {type:'geojson', data:{type:'FeatureCollection',features:targets.map(t => ({type:'Feature',properties:t,geometry:{type:'Point',coordinates:[t.longitude,t.latitude]}}))}}
          },
          layers: [
            {id:'osm', type:'raster', source:'osm'},
            {id:'prospectivity-fill',type:'fill',source:'prospectivity',paint:{'fill-color':['match',['get','zone'],'HIGH','#dc2626','MEDIUM','#d97706','LOW','#64748b','#94a3b8'],'fill-opacity':0.42}},
            {id:'prospectivity-outline',type:'line',source:'prospectivity',paint:{'line-color':['match',['get','zone'],'HIGH','#991b1b','MEDIUM','#a16207','LOW','#334155','#64748b'],'line-width':2.5}},
            {id:'target-points',type:'circle',source:'targets',paint:{'circle-radius':['interpolate',['linear'],['zoom'],4,5,8,8],'circle-color':['match',['get','classification'],'VERY_HIGH','#991b1b','HIGH','#dc2626','MEDIUM','#d97706','LOW','#64748b','VERY_LOW','#cbd5e1','#64748b'],'circle-stroke-color':'#fff','circle-stroke-width':1.5}}
          ]
        }
      })
      m.addControl(new maplibregl.NavigationControl({showCompass:true}), 'bottom-right')
      m.on('error', (e) => console.error('Map error:', e))
      let layersInitialized = false
      const initializeLayers = async () => {
        if (layersInitialized) return
        layersInitialized = true
        try {
          const prospectivityResponse = await fetch(`${API_URL}/manganese/prospectivity`)
          if (!prospectivityResponse.ok) throw new Error(`Prospectivity request failed: ${prospectivityResponse.status}`)
          const prospectivityData = await prospectivityResponse.json()
          const source = m.getSource('prospectivity') as maplibregl.GeoJSONSource
          source.setData(prospectivityData)
          zoneDataRef.current = prospectivityData
          updateZoneOverlays()
          setMapServiceOnline(true)
        } catch (error) {
          console.error('Prospectivity layer error:', error)
          setMapServiceOnline(false)
        }
        domMarkers.current = targets.map(target => {
          const color = target.zone === 'HIGH' ? '#dc2626' : target.zone === 'MEDIUM' ? '#d97706' : '#64748b'
          const popup = `<div style="padding:14px;min-width:240px"><div style="font-size:11px;color:#64748b">MANGANESE TARGET · ${target.code}</div><div style="font-weight:700;margin:3px 0 8px">${target.name}</div><div>Mn prospectivity: <strong>${Math.round(target.manganese_probability * 100)}%</strong></div><div>Confidence: <strong>${target.confidence}%</strong></div><div style="margin-top:6px">Classification: ${target.classification.replace('_',' ')}</div><div>Priority: ${target.priority}</div><div style="margin-top:6px;font-size:12px;color:#64748b">${target.latitude.toFixed(5)}° N, ${target.longitude.toFixed(5)}° E</div><div style="margin-top:8px;font-size:11px;color:#92400e"><strong>DEMO MODEL</strong> · Field validation required</div></div>`
          return new maplibregl.Marker({color}).setLngLat([target.longitude, target.latitude]).setPopup(new maplibregl.Popup({offset: 18}).setHTML(popup)).addTo(m)
        })
        domMarkers.current.forEach((marker, index) => {
          const target = targets[index]
          const matchesClassification = classificationFilter === 'ALL' || target.classification === classificationFilter
          const matchesPriority = priorityFilter === 'ALL' || target.priority === priorityFilter
          marker.getElement().style.display = showTargets && matchesClassification && matchesPriority ? '' : 'none'
        })
        m.on('click','target-points', (e: any) => {
          const f = e.features?.[0]
          if (!f || !f.geometry || f.geometry.type !== 'Point') return
          const p = f.properties as any
          const coordinates = (f.geometry as any).coordinates as [number, number]
          const factors = Array.isArray(p.factors) ? p.factors.join(' · ') : 'Not available'
          new maplibregl.Popup({offset:12}).setLngLat(coordinates).setHTML(`<div style="padding:14px;min-width:250px"><div style="font-size:11px;color:#64748b">MANGANESE TARGET · ${p.code}</div><div style="font-weight:700;margin:3px 0 8px">${p.name}</div><div style="display:flex;justify-content:space-between"><span>Mn prospectivity</span><strong>${p.manganese_probability ? `${Math.round(p.manganese_probability * 100)}%` : `${p.score}/100`}</strong></div><div style="margin-top:6px;font-size:12px;color:#64748b">${p.geology}</div><div style="margin-top:8px;font-size:12px"><strong>Exact location</strong><br/>${coordinates[1].toFixed(5)}° N, ${coordinates[0].toFixed(5)}° E</div><div style="margin-top:8px;font-size:12px"><strong>Evidence variations</strong><br/>${factors}</div><div style="margin-top:8px;font-size:11px;color:#92400e"><strong>DEMO MODEL</strong> · Screening output, not deposit confirmation</div></div>`).addTo(m)
        })
        m.on('mouseenter','target-points',()=>m.getCanvas().style.cursor='pointer')
        m.on('mouseleave','target-points',()=>m.getCanvas().style.cursor='')
        m.fitBounds([[79, 18], [87, 23]], {padding: 24, duration: 0})
      }
      const updateZoneOverlays = () => {
        setZoneOverlays(zoneDataRef.current.features.map(feature => ({
          id: (feature.properties as {id?: string; zone_id?: string}).id || (feature.properties as {id?: string; zone_id?: string}).zone_id || 'MNG-ZONE-UNKNOWN',
          classification: feature.properties.classification,
          probability: feature.properties.probability,
          points: feature.geometry.coordinates[0].map(coordinate => {
            const point = m.project(coordinate as [number, number])
            return `${point.x},${point.y}`
          }).join(' '),
        })))
      }
      m.on('load', initializeLayers)
      m.on('style.load', initializeLayers)
      m.once('idle', initializeLayers)
      m.on('move', updateZoneOverlays)
      m.on('resize', updateZoneOverlays)
      window.setTimeout(updateZoneOverlays, 100)
      map.current = m
      return () => { domMarkers.current.forEach(marker => marker.remove()); domMarkers.current = []; m.off('move', updateZoneOverlays); m.off('resize', updateZoneOverlays); setZoneOverlays([]); m.remove(); map.current = null }
    } catch (err) {
      console.error('Map initialization error:', err)
    }
  }, [targets])

  useEffect(() => {
    const m = map.current
    if (!m) return
    domMarkers.current.forEach((marker, index) => {
      const target = targets[index]
      const matchesClassification = classificationFilter === 'ALL' || target.classification === classificationFilter
      const matchesPriority = priorityFilter === 'ALL' || target.priority === priorityFilter
      marker.getElement().style.display = showTargets && matchesClassification && matchesPriority ? '' : 'none'
    })
    const applyFilters = () => {
      if (!m.isStyleLoaded()) return
      if (m.getLayer('target-points')) m.setLayoutProperty('target-points','visibility',showTargets?'visible':'none')
      if (m.getLayer('target-points')) {
      const filters: maplibregl.FilterSpecification[] = []
      if (classificationFilter !== 'ALL') filters.push(['==', ['get', 'classification'], classificationFilter] as maplibregl.FilterSpecification)
      if (priorityFilter !== 'ALL') filters.push(['==', ['get', 'priority'], priorityFilter] as maplibregl.FilterSpecification)
      m.setFilter('target-points', filters.length === 0 ? null : filters.length === 1 ? filters[0] : ['all', ...filters] as maplibregl.FilterSpecification)
      }
      if (m.getLayer('prospectivity-fill')) m.setLayoutProperty('prospectivity-fill','visibility',showProspectivity?'visible':'none')
      if (m.getLayer('prospectivity-outline')) m.setLayoutProperty('prospectivity-outline','visibility',showProspectivity?'visible':'none')
    }
    if (!m.isStyleLoaded()) {
      m.once('load', applyFilters)
      return () => { m.off('load', applyFilters) }
    }
    applyFilters()
  }, [showTargets, showProspectivity, classificationFilter, priorityFilter])

  const zoom = (amount:number) => map.current?.zoomTo((map.current.getZoom() + amount), {duration:250})
  const locate = () => map.current?.flyTo({center, zoom:6, duration:900})

  const search = () => {
    const t = targets.find(x => x.code.toLowerCase() === query.trim().toLowerCase() || x.name.toLowerCase().includes(query.trim().toLowerCase()))
    if (t) map.current?.flyTo({center:[t.longitude,t.latitude],zoom:9,duration:900})
  }

  return <div className="space-y-4">
    <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
      <div><h1 className="text-xl font-semibold text-slate-900">Manganese Prospectivity Map</h1><p className="mt-1 text-sm text-slate-500">Explore manganese prospectivity zones and ranked field targets.</p></div>
    <div className={`flex items-center gap-2 text-xs ${mapServiceOnline ? 'text-slate-500' : 'text-amber-700'}`}><span className={`h-2 w-2 rounded-full ${mapServiceOnline ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>{mapServiceOnline ? 'Map service online' : 'Map service unavailable · demo zones'}</div>
    </div>

    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 p-3">
        <div className="flex min-w-[220px] flex-1 items-center gap-2 rounded-lg border border-slate-200 px-3 py-2">
          <Search size={16} className="text-slate-400"/><input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>e.key==='Enter'&&search()} placeholder="Search target code or name" className="w-full bg-transparent text-sm outline-none"/>
        </div>
        <button onClick={search} className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white">Search</button>
        <button onClick={locate} className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-50" title="Reset map"><LocateFixed size={17}/></button>
        <div className="flex items-center gap-2 rounded-lg border border-slate-200 px-2 py-1.5 text-xs text-slate-600"><SlidersHorizontal size={15}/><select value={classificationFilter} onChange={e=>setClassificationFilter(e.target.value)} className="bg-transparent outline-none"><option value="ALL">All prospectivity</option><option value="VERY_HIGH">Very high</option><option value="HIGH">High</option><option value="MEDIUM">Medium</option><option value="LOW">Low</option><option value="VERY_LOW">Very low</option></select></div>
        <select aria-label="Target priority" value={priorityFilter} onChange={e=>setPriorityFilter(e.target.value)} className="rounded-lg border border-slate-200 px-2 py-2 text-xs text-slate-600 outline-none"><option value="ALL">All priorities</option><option value="P1">P1 targets</option><option value="P2">P2 targets</option><option value="P3">P3 targets</option></select>
      </div>
      <div className="relative h-[540px]">
        <div ref={mapNode} className="absolute inset-0" style={{ width: '100%', height: '100%', minHeight: '540px' }}>
          <svg className="pointer-events-none absolute inset-0 z-[1] h-full w-full" aria-label="Manganese prospectivity zones">
            {showProspectivity && zoneOverlays.filter(zone => classificationFilter === 'ALL' || zone.classification === classificationFilter).map(zone => <polygon key={zone.id} points={zone.points} fill={getProspectivityColor(zone.classification)} fillOpacity="0.45" stroke={getProspectivityColor(zone.classification)} strokeOpacity="0.8" strokeWidth="2" vectorEffect="non-scaling-stroke" pointerEvents="auto" onClick={() => map.current && new maplibregl.Popup({offset:12}).setLngLat(map.current.unproject(zone.points.split(' ')[0].split(',').map(Number) as [number, number])).setHTML(`<strong>MANGANESE PROSPECTIVITY</strong><br/>Zone: ${zone.id}<br/>Classification: ${zone.classification.replace('_',' ')}<br/>Mn Prospectivity: ${Math.round(zone.probability * 100)}%<br/><br/><small>DEMO DATA · Screening result only. Field validation required.</small>`).addTo(map.current)}><title>{zone.id} · {zone.classification}</title></polygon>)}
          </svg>
        </div>
        <div className="absolute left-4 top-4 w-40 rounded-xl border border-slate-200 bg-white/95 p-2 shadow-lg backdrop-blur sm:w-56 sm:p-3">
          <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-600"><Layers3 size={15}/> Layers</div>
          <label className="flex cursor-pointer items-center justify-between py-1.5 text-sm"><span>Prospectivity zones</span><input type="checkbox" checked={showProspectivity} onChange={e=>setShowProspectivity(e.target.checked)}/></label>
          <label className="flex cursor-pointer items-center justify-between py-1.5 text-sm"><span>Priority targets</span><input type="checkbox" checked={showTargets} onChange={e=>setShowTargets(e.target.checked)}/></label>
          <div className="mt-3 border-t border-slate-100 pt-3 text-[11px] text-slate-500"><div className="mb-1 font-medium text-slate-700">Manganese prospectivity</div><div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-sm bg-[#991b1b]"/>Very high</div><div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-sm bg-[#c2410c]"/>High</div><div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-sm bg-[#ca8a04]"/>Medium</div><div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-sm bg-[#64748b]"/>Low</div><div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-sm bg-[#cbd5e1]"/>Very low</div></div>
        </div>
        <div className="absolute bottom-4 right-4 flex flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg">
          <button onClick={()=>zoom(1)} className="p-2.5 hover:bg-slate-50"><Plus size={17}/></button><div className="h-px bg-slate-200"/><button onClick={()=>zoom(-1)} className="p-2.5 hover:bg-slate-50"><Minus size={17}/></button>
        </div>
        <div className="absolute bottom-4 left-4 rounded-md bg-white/90 px-2 py-1 text-[10px] text-slate-500 shadow">Demo AOI · Central & eastern India</div>
      </div>
    </div>
    <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-xs leading-5 text-amber-800">Interpretation note: prospectivity colors represent model-estimated exploration priority, not confirmed manganese reserves. Field geology, assays and drilling are required for validation.</div>
  </div>
}
