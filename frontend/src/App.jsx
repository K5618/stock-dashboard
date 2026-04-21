import { useState, useEffect } from 'react'
import { supabase } from './lib/supabase'

function App() {
  const [isAuth, setIsAuth] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [authError, setAuthError] = useState('')

  const [status, setStatus] = useState("Loading...")
  const [warnings, setWarnings] = useState([])
  const [indices, setIndices] = useState({ US: [], Europe: [], Asia: [] })
  
  // Data sets
  const [sectors, setSectors] = useState([])
  const [topStocks, setTopStocks] = useState({})
  const [screener, setScreener] = useState(null)
  const [commodities, setCommodities] = useState(null)
  const [twData, setTwData] = useState(null)
  
  // Interaction States
  const [selectedSector, setSelectedSector] = useState(null)
  const [selectedTwSector, setSelectedTwSector] = useState(null)
  
  // Sorting States
  const [sortSectors, setSortSectors] = useState({ key: 'change_pct', direction: 'desc' })
  const [sortStocks, setSortStocks] = useState({ key: 'market_cap', direction: 'desc' })

  // Screener States
  const [screenerTab, setScreenerTab] = useState('upward') // 'upward' | 'downward'
  const [activeFilter, setActiveFilter] = useState('gain_3') // default for upward
  
  // TW Screener States
  const [twScreenerBucket, setTwScreenerBucket] = useState('TWSE') // 'TWSE' | 'TPEX' | 'Emerging'
  const [twScreenerTab, setTwScreenerTab] = useState('upward')
  const [activeTwFilter, setActiveTwFilter] = useState('gain_3')

  // Main Top Nav Tabs
  const [mainTab, setMainTab] = useState('us_stocks') // 'us_stocks' | 'commodities' | 'tw_stocks'
  
  // Specific TW Main Sub-tabs
  const [twMarketTab, setTwMarketTab] = useState('TWSE')

  const handleLogin = (e) => {
    e.preventDefault()
    if (username === 'K5618' && password === 'Kktest5618') {
      setIsAuth(true)
    } else {
      setAuthError('帳號或密碼錯誤 / Invalid credentials')
    }
  }

  const fetchData = async () => {
    try {
      let data = null;
      const baseUrl = import.meta.env.BASE_URL || '/';
      const fetchUrl = baseUrl.endsWith('/') ? baseUrl + 'data.json' : baseUrl + '/data.json';
      
      try {
        // local dev often prefers local fresh JSON over stale supabase
        const req = await fetch(fetchUrl);
        if (req.ok) {
          data = await req.json();
        } else {
          throw new Error("Local data.json not found");
        }
      } catch (localErr) {
        // Fallback to Supabase
        const { data: snapshots, error } = await supabase
          .from('market_snapshots')
          .select('data')
          .order('created_at', { ascending: false })
          .limit(1);

        if (error) throw error;
        if (!snapshots || snapshots.length === 0) throw new Error("No data found");
        data = snapshots[0].data;
      }
      
      setStatus(data.status.last_updated)
      setWarnings(data.status.warnings || [])
      setIndices(data.indices?.data || { US: [], Europe: [], Asia: [] })
      setSectors(data.sectors?.data || [])
      setTopStocks(data.top_stocks?.data || {})
      setScreener(data.screener || null)
      setCommodities(data.commodities || null)
      
      if (data.sectors?.data?.length > 0) {
        setSelectedSector(data.sectors.data[0].name)
      }

      // Fetch TW Data
      try {
        const { data: twSnaps, error: twError } = await supabase
          .from('tw_market_snapshots')
          .select('data')
          .order('created_at', { ascending: false })
          .limit(1)
        if (!twError && twSnaps && twSnaps.length > 0) {
          setTwData(twSnaps[0].data)
          if (twSnaps[0].data.sectors_data?.TWSE?.length > 0 && !selectedTwSector) setSelectedTwSector(twSnaps[0].data.sectors_data.TWSE[0].name)
        } else {
          throw new Error("Fallback TW")
        }
      } catch (e) {
        // Fallback to local JSON if not in Supabase
        const baseUrl = import.meta.env.BASE_URL || '/';
        const fetchUrl = baseUrl.endsWith('/') ? baseUrl + 'tw_data.json' : baseUrl + '/tw_data.json';
        const req = await fetch(fetchUrl)
        if (req.ok) {
          const tdata = await req.json()
          setTwData(tdata)
          if (tdata.sectors_data?.TWSE?.length > 0 && !selectedTwSector) setSelectedTwSector(tdata.sectors_data.TWSE[0].name)
        }
      }

    } catch(e) {
      console.error(e)
      setStatus("Error loading data.")
    }
  }

  useEffect(() => {
    if (isAuth) {
      fetchData()
    }
  }, [isAuth])

  const formatPrice = (val) => val != null ? val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "-"
  const formatChange = (val) => val != null ? `${val >= 0 ? '+' : ''}${val.toFixed(2)}` : "-"
  const formatLargeNum = (num) => {
    if (!num) return "-"
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T'
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B'
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M'
    return num.toLocaleString()
  }
  
  const ValueCell = ({ item, isPct = false, isTaiwan = false }) => {
    const val = isPct ? item.change_pct : item.change_pt
    const isUp = val >= 0
    let color = isUp ? "text-up" : "text-down"
    if (isTaiwan) {
      color = isUp ? "text-tw-up" : "text-tw-down"
    }
    return (
      <span className={`${color} font-medium`}>
        {formatChange(val)}{isPct ? '%' : ''}
      </span>
    )
  }

  // --- Sorting Logic ---
  const handleSortSectors = (key) => {
    let direction = 'desc'
    if (sortSectors.key === key && sortSectors.direction === 'desc') {
      direction = 'asc'
    }
    setSortSectors({ key, direction })
  }

  const handleSortStocks = (key) => {
    let direction = 'desc'
    if (sortStocks.key === key && sortStocks.direction === 'desc') {
      direction = 'asc'
    }
    setSortStocks({ key, direction })
  }

  const sortedSectors = [...sectors].sort((a, b) => {
    if (a[sortSectors.key] < b[sortSectors.key]) return sortSectors.direction === 'asc' ? -1 : 1
    if (a[sortSectors.key] > b[sortSectors.key]) return sortSectors.direction === 'asc' ? 1 : -1
    return 0
  })

  // Top 10 Stocks computation
  const activeStocks = selectedSector && topStocks[selectedSector] ? topStocks[selectedSector].top_market_cap : []
  const sortedStocks = [...activeStocks].sort((a, b) => {
    if (a[sortStocks.key] < b[sortStocks.key]) return sortStocks.direction === 'asc' ? -1 : 1
    if (a[sortStocks.key] > b[sortStocks.key]) return sortStocks.direction === 'asc' ? 1 : -1
    return 0
  })

  // --- Screener Grouping Logic ---
  const getActiveScreenerList = () => {
    if (!screener) return []
    const filterMap = {
      'gain_3': screener.block1?.gain_3, 'gain_5': screener.block1?.gain_5, 'gain_10': screener.block1?.gain_10,
      'h_30': screener.block2?.h_30, 'h_90': screener.block2?.h_90, 'h_180': screener.block2?.h_180, 'h_all': screener.block2?.h_all,
      'loss_3': screener.block3?.loss_3, 'loss_5': screener.block3?.loss_5, 'loss_10': screener.block3?.loss_10,
      'l_30': screener.block4?.l_30, 'l_90': screener.block4?.l_90, 'l_180': screener.block4?.l_180, 'l_all': screener.block4?.l_all
    }
    return filterMap[activeFilter] || []
  }

  const groupedScreenerData = () => {
    const list = getActiveScreenerList()
    const groups = {}
    list.forEach(item => {
      const sec = item.sector || "Unknown Sector"
      const ind = item.industry || "Unknown Industry"
      if (!groups[sec]) groups[sec] = {}
      if (!groups[sec][ind]) groups[sec][ind] = []
      groups[sec][ind].push(item)
    })
    return groups
  }
  
  const currentGroups = groupedScreenerData()

  // --- TW Data Grouping Logic ---
  const activeTwSectors = (twData?.sectors_data?.[twMarketTab]) || []
  const sortedTwSectors = [...activeTwSectors].sort((a, b) => {
    if (a[sortSectors.key] < b[sortSectors.key]) return sortSectors.direction === 'asc' ? -1 : 1
    if (a[sortSectors.key] > b[sortSectors.key]) return sortSectors.direction === 'asc' ? 1 : -1
    return 0
  })

  const selectedTwSectorObj = activeTwSectors.find(s => s.name === selectedTwSector)
  const activeTwStocksList = selectedTwSectorObj ? selectedTwSectorObj.top_15 : []
  const sortedTwStocks = [...activeTwStocksList].sort((a, b) => {
    if (a[sortStocks.key] < b[sortStocks.key]) return sortStocks.direction === 'asc' ? -1 : 1
    if (a[sortStocks.key] > b[sortStocks.key]) return sortStocks.direction === 'asc' ? 1 : -1
    return 0
  })

  const getActiveTwScreenerList = () => {
    if (!twData?.screener) return []
    const bucket = twData.screener[twScreenerBucket]
    if (!bucket) return []
    const filterMap = {
      'gain_3': bucket.block1?.gain_3, 'gain_5': bucket.block1?.gain_5, 'gain_10': bucket.block1?.gain_10,
      'h_30': bucket.block2?.h_30, 'h_90': bucket.block2?.h_90, 'h_180': bucket.block2?.h_180, 'h_all': bucket.block2?.h_all,
      'loss_3': bucket.block3?.loss_3, 'loss_5': bucket.block3?.loss_5, 'loss_10': bucket.block3?.loss_10,
      'l_30': bucket.block4?.l_30, 'l_90': bucket.block4?.l_90, 'l_180': bucket.block4?.l_180, 'l_all': bucket.block4?.l_all
    }
    return filterMap[activeTwFilter] || []
  }

  const groupedTwScreenerData = () => {
    const list = getActiveTwScreenerList()
    const groups = {}
    list.forEach(item => {
      const sec = item.sector || "未知產業"
      const ind = item.industry || "未知次產業"
      if (!groups[sec]) groups[sec] = {}
      if (!groups[sec][ind]) groups[sec][ind] = []
      groups[sec][ind].push(item)
    })
    return groups
  }
  const currentTwGroups = groupedTwScreenerData()

  // Render Login overlay if not authenticated
  if (!isAuth) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex flex-col justify-center items-center px-4">
        <div className="max-w-md w-full bg-white p-8 border border-[#E0E3EB] rounded-lg shadow-sm">
          <div className="mb-6 text-center">
            <h1 className="text-2xl font-bold text-[#131722] mb-1">Stock Dashboard</h1>
            <p className="text-sm text-[#787b86]">Please sign in to view the market data.</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#131722] mb-1">Username / Account</label>
              <input 
                type="text" 
                className="w-full px-3 py-2 border border-[#E0E3EB] rounded outline-none focus:border-[#2962ff] transition-colors"
                value={username} onChange={e => setUsername(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#131722] mb-1">Password</label>
              <input 
                type="password" 
                className="w-full px-3 py-2 border border-[#E0E3EB] rounded outline-none focus:border-[#2962ff] transition-colors"
                value={password} onChange={e => setPassword(e.target.value)} required />
            </div>
            {authError && <p className="text-[#f23645] text-sm font-medium text-center">{authError}</p>}
            <button type="submit" className="w-full bg-[#2962ff] hover:bg-[#1e4ad8] text-white font-medium py-2 px-4 rounded transition-colors">
              Access System
            </button>
          </form>
        </div>
      </div>
    )
  }

  const MarketCard = ({ item, isTaiwan=false }) => (
    <div className="bg-cardLight p-4 flex flex-col justify-between border-r border-b border-borderLight cursor-default hover:bg-[#F8F9FA] transition-colors">
      <div className="flex justify-between items-start mb-3">
        <div className="overflow-hidden">
          <p className="text-xs text-textMuted font-mono uppercase tracking-wider truncate mb-1">{item.symbol}</p>
          <h3 className="text-sm font-semibold text-textMain truncate leading-tight" title={item.name}>{item.name}</h3>
        </div>
      </div>
      <div>
        <p className="text-lg font-bold text-textMain tracking-tight mb-1">{formatPrice(item.close_price)}</p>
        <div className="flex space-x-3 text-sm">
          <ValueCell item={item} isTaiwan={isTaiwan} />
          <ValueCell item={item} isPct isTaiwan={isTaiwan} />
        </div>
      </div>
    </div>
  );

  const SortableHeader = ({ label, sortKey, currentSort, onSort, align="left" }) => {
    let icon = "↕";
    if (currentSort.key === sortKey) {
      icon = currentSort.direction === 'asc' ? "↑" : "↓";
    }
    return (
      <div 
        className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider text-textMuted cursor-pointer hover:text-textMain select-none ${align === 'right' ? 'text-right' : ''}`}
        onClick={() => onSort(sortKey)}
      >
        {label} <span className="ml-1 opacity-50">{icon}</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-bgLight selection:bg-borderLight pb-12">
      {/* Top Navigation Bar */}
      <nav className="bg-cardLight border-b border-borderLight sticky top-0 z-10 shadow-sm">
        <div className="max-w-[1600px] mx-auto px-4 lg:px-8 py-3 flex justify-between items-center w-full">
          <div className="flex items-center space-x-6">
            <h1 className="text-xl font-bold tracking-tight text-textMain flex items-center">
              <span className="text-primary mr-2">●</span> Global Markets
            </h1>
            <div className="flex space-x-4 ml-8">
              <button 
                onClick={() => setMainTab('us_stocks')}
                className={`px-4 py-2 text-sm font-bold transition-colors uppercase tracking-wider rounded ${mainTab === 'us_stocks' ? 'bg-[#E3EBFF] text-[#2962ff]' : 'text-textMuted hover:text-textMain'}`}
              >
                U.S. Stocks
              </button>
              <button 
                onClick={() => setMainTab('commodities')}
                className={`px-4 py-2 text-sm font-bold transition-colors uppercase tracking-wider rounded ${mainTab === 'commodities' ? 'bg-[#E3EBFF] text-[#2962ff]' : 'text-textMuted hover:text-textMain'}`}
              >
                Commodities
              </button>
              <button 
                onClick={() => setMainTab('tw_stocks')}
                className={`px-4 py-2 text-sm font-bold transition-colors uppercase tracking-wider rounded ${mainTab === 'tw_stocks' ? 'bg-[#E3EBFF] text-[#2962ff]' : 'text-textMuted hover:text-textMain'}`}
              >
                TW Stocks
              </button>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className={`flex items-center space-x-1 text-xs text-textMuted px-3 py-1.5 rounded-sm border font-mono ${warnings.length > 0 ? 'bg-red-50 border-red-300 text-red-600' : 'bg-bgLight border-borderLight'}`}>
              <span className={`inline-block w-2 h-2 rounded-full animate-pulse mr-1 ${warnings.length > 0 ? 'bg-red-500' : 'bg-up'}`}></span>
              LIVE DATA <span className="mx-2">|</span> {status}
            </div>
            <button onClick={() => setIsAuth(false)} className="text-sm text-textMuted hover:text-textMain underline ml-4">登出 Logout</button>
          </div>
        </div>
        {warnings.length > 0 && (
          <div className="max-w-[1600px] mx-auto px-4 lg:px-8 pb-3">
            {warnings.map((w, i) => (
              <div key={i} className="text-xs font-semibold text-red-600 bg-red-100 border border-red-200 px-3 py-1.5 rounded inline-block mr-2">
                ⚠️ API 例外警告: {w}
              </div>
            ))}
          </div>
        )}
      </nav>

      {/* Main Content Area */}
      <main className="max-w-[1600px] mx-auto px-4 lg:px-8 py-8 w-full space-y-10">
        
        {mainTab === 'us_stocks' && (
          <>
            <section>
              <div className="flex justify-between items-end mb-4 border-b border-borderLight pb-2">
                <h2 className="text-xl font-bold text-textMain flex items-center">
                  Major Indices
                  <span className="text-sm font-normal text-textMuted ml-3 select-none">(Updated: {status})</span>
                </h2>
              </div>
              <div className="space-y-6">
                {['US', 'Europe', 'Asia'].map(region => (
                  <div key={region}>
                    <h3 className="text-sm font-semibold text-textMuted uppercase tracking-wider mb-2">{region} Markets</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 border-l border-t border-borderLight bg-bgLight overflow-hidden">
                      {(indices[region] || []).map(idx => (
                        <MarketCard key={idx.symbol} item={idx} />
                      ))}
                      {(indices[region] || []).length === 0 && <div className="p-4 text-xs text-textMuted border-b border-r border-borderLight">No data</div>}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <div className="flex justify-between items-end mb-4 border-b border-borderLight pb-2">
                <h2 className="text-xl font-bold text-textMain flex items-center">
                  Sectors Performance & Top Components
                  <span className="text-sm font-normal text-textMuted ml-3 select-none">(Updated: {status})</span>
                </h2>
              </div>
              
              <div className="flex flex-col lg:flex-row gap-6 items-start">
                <div className="w-full lg:w-[400px] flex-shrink-0 bg-cardLight border border-borderLight shadow-sm">
                  <div className="px-4 py-3 border-b border-borderLight bg-[#F8F9FA]">
                    <h3 className="font-semibold text-textMain text-sm uppercase tracking-wider">US Sectors (ETFs)</h3>
                  </div>
                  <div className="grid grid-cols-12 bg-bgLight border-b border-borderLight">
                    <div className="col-span-6"><SortableHeader label="Sector" sortKey="name" currentSort={sortSectors} onSort={handleSortSectors} /></div>
                    <div className="col-span-3"><SortableHeader label="Price" sortKey="close_price" currentSort={sortSectors} onSort={handleSortSectors} align="right" /></div>
                    <div className="col-span-3"><SortableHeader label="Chg %" sortKey="change_pct" currentSort={sortSectors} onSort={handleSortSectors} align="right" /></div>
                  </div>
                  <div className="divide-y divide-borderLight max-h-[800px] overflow-y-auto">
                    {sortedSectors.map(sec => (
                      <div 
                        key={sec.symbol} 
                        onClick={() => setSelectedSector(sec.name)}
                        className={`grid grid-cols-12 gap-2 px-4 py-3 items-center cursor-pointer transition-colors text-sm
                          ${selectedSector === sec.name ? 'bg-[#E3EBFF] border-l-4 border-l-[#2962ff]' : 'hover:bg-[#F8F9FA] border-l-4 border-l-transparent'}`}
                      >
                        <div className="col-span-6 flex flex-col justify-center overflow-hidden">
                          <span className="font-bold text-textMain truncate">{sec.symbol}</span>
                          <span className="text-xs text-textMuted truncate" title={sec.name}>{sec.name}</span>
                        </div>
                        <div className="col-span-3 text-right font-medium text-textMain tabular-nums">
                          {formatPrice(sec.close_price)}
                        </div>
                        <div className="col-span-3 text-right tabular-nums">
                          <ValueCell item={sec} isPct />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex-1 w-full bg-cardLight border border-borderLight shadow-sm overflow-x-auto">
                  <div className="px-4 py-3 border-b border-borderLight bg-[#F8F9FA] flex justify-between items-center min-w-[700px]">
                    <h3 className="font-semibold text-textMain text-sm uppercase tracking-wider">
                      Top 10 Stocks: <span className="text-primary">{selectedSector || 'Select a Sector'}</span>
                    </h3>
                  </div>
                  
                  <div className="grid grid-cols-12 min-w-[700px] bg-bgLight border-b border-borderLight">
                    <div className="col-span-3"><SortableHeader label="Symbol/Name" sortKey="symbol" currentSort={sortStocks} onSort={handleSortStocks} /></div>
                    <div className="col-span-2"><SortableHeader label="Close" sortKey="close_price" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                    <div className="col-span-2"><SortableHeader label="Chg %" sortKey="change_pct" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                    <div className="col-span-2"><SortableHeader label="Volume" sortKey="volume" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                    <div className="col-span-3"><SortableHeader label="Mkt Cap" sortKey="market_cap" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                  </div>
                  
                  <div className="divide-y divide-borderLight min-w-[700px]">
                    {sortedStocks.length > 0 ? sortedStocks.map(stock => (
                      <div key={stock.symbol} className="grid grid-cols-12 gap-2 px-4 py-3 items-center hover:bg-[#F8F9FA] transition-colors cursor-default text-sm">
                        <div className="col-span-3 flex flex-col justify-center overflow-hidden">
                          <span className="font-bold text-textMain truncate">{stock.symbol}</span>
                          <span className="text-xs text-textMuted truncate" title={stock.name}>{stock.name}</span>
                        </div>
                        <div className="col-span-2 text-right font-medium text-textMain tabular-nums">
                          {formatPrice(stock.close_price)}
                        </div>
                        <div className="col-span-2 text-right tabular-nums">
                          <ValueCell item={stock} isPct />
                        </div>
                        <div className="col-span-2 text-right font-medium text-textMuted tabular-nums">
                          {formatLargeNum(stock.volume)}
                        </div>
                        <div className="col-span-3 text-right font-medium text-textMuted tabular-nums pr-2">
                           {formatLargeNum(stock.market_cap)}
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-24 text-textMuted">
                        {selectedSector ? 'Loading or no data available for this sector.' : 'Select a sector from the left to view components.'}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>

            <section>
              <div className="flex justify-between items-end mb-4 border-b border-borderLight pb-2 mt-8">
                <h2 className="text-xl font-bold text-textMain flex items-center">
                  US Top 1200 Quant Screener
                  <span className="text-sm font-normal text-textMuted ml-3 select-none">(Updated: {status})</span>
                </h2>
              </div>
              
              <div className="bg-cardLight border border-borderLight shadow-sm rounded overflow-hidden">
                <div className="flex border-b border-borderLight">
                  <button 
                    className={`flex-1 py-3 font-semibold text-sm transition-colors uppercase tracking-wider
                    ${screenerTab === 'upward' ? 'bg-[#F8F9FA] text-up border-b-2 border-b-up' : 'text-textMuted hover:text-textMain'}`}
                    onClick={() => { setScreenerTab('upward'); setActiveFilter('gain_3') }}
                  >
                    Upward Trends (Gains & Highs)
                  </button>
                  <button 
                    className={`flex-1 py-3 font-semibold text-sm transition-colors uppercase tracking-wider
                    ${screenerTab === 'downward' ? 'bg-[#F8F9FA] text-down border-b-2 border-b-down' : 'text-textMuted hover:text-textMain'}`}
                    onClick={() => { setScreenerTab('downward'); setActiveFilter('loss_3') }}
                  >
                    Downward Trends (Losses & Lows)
                  </button>
                </div>

                <div className="p-4 bg-[#F8F9FA] border-b border-borderLight flex flex-wrap gap-2">
                  {screenerTab === 'upward' ? (
                    <>
                      <span className="text-xs font-bold text-textMuted mr-2 my-auto">GAIN (Block 1):</span>
                      {['gain_3| > 3%', 'gain_5| > 5%', 'gain_10| > 10%'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold transition ${activeFilter === k ? 'bg-primary text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                      <span className="text-xs font-bold text-textMuted ml-6 mr-2 my-auto">HIGHS (Block 2):</span>
                      {['h_30|30-Day High', 'h_90|90-Day High', 'h_180|180-Day High', 'h_all|All-Time High'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold transition ${activeFilter === k ? 'bg-primary text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                    </>
                  ) : (
                    <>
                      <span className="text-xs font-bold text-textMuted mr-2 my-auto">LOSS (Block 3):</span>
                      {['loss_3| < -3%', 'loss_5| < -5%', 'loss_10| < -10%'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold transition ${activeFilter === k ? 'bg-primary text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                      <span className="text-xs font-bold text-textMuted ml-6 mr-2 my-auto">LOWS (Block 4):</span>
                      {['l_30|30-Day Low', 'l_90|90-Day Low', 'l_180|180-Day Low', 'l_all|All-Time Low'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold transition ${activeFilter === k ? 'bg-primary text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                    </>
                  )}
                </div>

                <div className="p-4 bg-white min-h-[400px]">
                  {Object.keys(currentGroups).length === 0 ? (
                    <div className="text-center py-20 text-textMuted">
                      No stocks match this criteria in the current session.
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {Object.entries(currentGroups).map(([sectorName, industriesObj]) => (
                        <div key={sectorName} className="border border-borderLight rounded-lg overflow-hidden shadow-sm">
                          <div className="bg-[#131722] px-4 py-2 text-white font-bold tracking-wide uppercase text-sm">
                            {sectorName}
                          </div>
                          
                          {Object.entries(industriesObj).map(([industryName, stocksArr]) => (
                            <div key={industryName} className="border-t border-borderLight first:border-0">
                              <div className="bg-[#F8F9FA] px-4 py-1.5 border-b border-borderLight">
                                <span className="text-xs font-semibold text-textMuted uppercase tracking-wider">{industryName}</span>
                                <span className="ml-2 text-xs font-bold text-textMain bg-white px-2 py-0.5 rounded border border-borderLight">{stocksArr.length}</span>
                              </div>
                              
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                  <thead className="text-xs uppercase text-textMuted bg-white border-b border-borderLight">
                                    <tr>
                                      <th className="px-4 py-2 font-semibold">Date</th>
                                      <th className="px-4 py-2 font-semibold">Symbol</th>
                                      <th className="px-4 py-2 font-semibold">Name</th>
                                      <th className="px-4 py-2 font-semibold text-right">Close</th>
                                      <th className="px-4 py-2 font-semibold text-right">Change %</th>
                                      <th className="px-4 py-2 font-semibold text-right">Volume</th>
                                      <th className="px-4 py-2 font-semibold text-right">Mkt Cap</th>
                                      <th className="px-4 py-2 font-semibold text-right">P/E (TTM)</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-borderLight">
                                    {stocksArr.sort((a,b) => b.market_cap - a.market_cap).map(stock => (
                                      <tr key={stock.symbol} className="hover:bg-[#F8F9FA] transition-colors">
                                        <td className="px-4 py-2 text-textMuted whitespace-nowrap">{stock.date}</td>
                                        <td className="px-4 py-2 font-bold text-textMain">{stock.symbol}</td>
                                        <td className="px-4 py-2 text-textMuted truncate max-w-[200px]" title={stock.name}>{stock.name}</td>
                                        <td className="px-4 py-2 text-right font-medium text-textMain tabular-nums">{formatPrice(stock.close_price)}</td>
                                        <td className="px-4 py-2 text-right tabular-nums"><ValueCell item={stock} isPct /></td>
                                        <td className="px-4 py-2 text-right text-textMuted tabular-nums">{formatLargeNum(stock.volume)}</td>
                                        <td className="px-4 py-2 text-right text-textMuted tabular-nums">{formatLargeNum(stock.market_cap)}</td>
                                        <td className="px-4 py-2 text-right text-textMuted tabular-nums">{stock.pe_ratio ? stock.pe_ratio.toFixed(2) : '-'}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </section>
          </>
        )}

        {/* --- COMMODITIES TAB CONTENT --- */}
        {mainTab === 'commodities' && (
          <div className="space-y-12">
            
            {commodities ? (
              Object.entries(commodities).map(([marketBlock, subCategories]) => (
                <section key={marketBlock}>
                  <div className="flex justify-between items-end mb-6 border-b border-borderLight pb-2 mt-4">
                    <h2 className="text-2xl font-bold text-[#131722] flex items-center">
                      {marketBlock}
                      <span className="text-sm font-normal text-textMuted ml-3 select-none">(Updated: {status})</span>
                    </h2>
                    <span className="text-xs text-textMuted">* Some futures quotes may be delayed.</span>
                  </div>

                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    {Object.entries(subCategories).map(([subCatName, items]) => {
                      if (items.length === 0) return null; // hide empty categories
                      return (
                        <div key={subCatName} className="bg-cardLight border border-borderLight rounded-lg shadow-sm overflow-hidden flex flex-col">
                          <div className="bg-[#131722] px-4 py-2 text-white font-bold tracking-wide uppercase text-sm flex justify-between items-center">
                            <span>{subCatName}</span>
                            <span className="text-xs font-normal text-gray-400 bg-gray-800 px-2 py-0.5 rounded">{items.length} Contracts</span>
                          </div>
                          <div className="overflow-x-auto flex-1">
                            <table className="w-full text-sm text-left">
                              <thead className="text-xs uppercase text-textMuted bg-[#F8F9FA] border-b border-borderLight">
                                <tr>
                                  <th className="px-4 py-2 font-semibold">Date</th>
                                  <th className="px-4 py-2 font-semibold">Name</th>
                                  <th className="px-4 py-2 font-semibold">Symbol</th>
                                  <th className="px-4 py-2 font-semibold text-right">Close</th>
                                  <th className="px-4 py-2 font-semibold text-right">Change %</th>
                                  <th className="px-4 py-2 font-semibold text-right">Exchange</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-borderLight">
                                {items.map(item => (
                                  <tr key={item.symbol} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-4 py-3 text-textMuted whitespace-nowrap">{item.date}</td>
                                    <td className="px-4 py-3 font-semibold text-textMain truncate leading-tight max-w-[150px]" title={item.name}>{item.name}</td>
                                    <td className="px-4 py-3 font-mono text-xs text-textMuted">{item.symbol}</td>
                                    <td className="px-4 py-3 text-right font-bold text-textMain tabular-nums">{formatPrice(item.close_price)}</td>
                                    <td className="px-4 py-3 text-right tabular-nums"><ValueCell item={item} isPct /></td>
                                    <td className="px-4 py-3 text-right text-xs text-textMuted">{item.exchange}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </section>
              ))
            ) : (
              <div className="text-center py-24 text-textMuted">Loading Commodities...</div>
            )}
            
          </div>
        )}

        {/* --- TW STOCKS TAB CONTENT --- */}
        {mainTab === 'tw_stocks' && twData && (
          <div className="space-y-12">
            <section>
              <div className="flex justify-between items-end mb-4 border-b border-borderLight pb-2 mt-4">
                <h2 className="text-xl font-bold text-textMain font-sans">台股指數與籌碼</h2>
              </div>
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-textMuted uppercase tracking-wider mb-2 font-sans">大盤指數</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 border-l border-t border-borderLight bg-bgLight overflow-hidden">
                    {(twData.indices?.data || []).map(idx => (
                      <MarketCard key={idx.symbol} item={idx} isTaiwan={true} />
                    ))}
                    {(twData.indices?.data || []).length === 0 && <div className="p-4 text-xs text-textMuted border-b border-r border-borderLight font-sans">無資料</div>}
                  </div>
                </div>

                <div className="flex flex-col gap-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Institutional Net */}
                    <div className="col-span-1 bg-cardLight border border-borderLight rounded shadow-sm overflow-hidden flex flex-col">
                      <div className="bg-[#131722] px-4 py-2 text-white font-bold tracking-wide text-sm font-sans">三大法人買賣超</div>
                      <div className="overflow-x-auto flex-1">
                        <table className="w-full text-sm text-left">
                          <thead className="text-xs text-textMuted bg-[#F8F9FA] border-b border-borderLight font-sans">
                            <tr><th className="px-4 py-2 font-semibold font-sans">單位</th><th className="px-4 py-2 font-semibold text-right font-sans">加權買賣超(元)</th><th className="px-4 py-2 font-semibold text-right font-sans">櫃買買賣超(元)</th></tr>
                          </thead>
                          <tbody className="divide-y divide-borderLight">
                            {(twData.chips?.institutional || []).map(chip => (
                              <tr key={chip.entity} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-2 font-bold text-textMain font-sans">{chip.entity}</td>
                                <td className="px-4 py-2 text-right font-medium tabular-nums"><span className={chip.twse_net >= 0 ? 'text-textMain' : 'text-red-600'}>{chip.twse_net > 0 ? '+' : ''}{chip.twse_net.toLocaleString()}</span></td>
                                <td className="px-4 py-2 text-right font-medium tabular-nums"><span className={chip.tpex_net >= 0 ? 'text-textMain' : 'text-red-600'}>{chip.tpex_net > 0 ? '+' : ''}{chip.tpex_net.toLocaleString()}</span></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                    {/* Futures Net */}
                    <div className="col-span-1 bg-cardLight border border-borderLight rounded shadow-sm overflow-hidden flex flex-col">
                      <div className="bg-[#131722] px-4 py-2 text-white font-bold tracking-wide text-sm font-sans">臺股期貨(大台)</div>
                      <div className="overflow-x-auto flex-1">
                        <table className="w-full text-sm text-left">
                          <thead className="text-xs text-textMuted bg-[#F8F9FA] border-b border-borderLight font-sans">
                            <tr><th className="px-4 py-2 font-semibold font-sans">單位</th><th className="px-4 py-2 font-semibold text-right font-sans">多空淨額口數</th><th className="px-4 py-2 font-semibold text-right font-sans">未平倉餘額(OI)</th></tr>
                          </thead>
                          <tbody className="divide-y divide-borderLight">
                            {(twData.chips?.futures || []).map(chip => (
                              <tr key={chip.entity} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-2 font-bold text-textMain font-sans">{chip.entity}</td>
                                <td className="px-4 py-2 text-right font-medium tabular-nums"><span className={chip.net_contracts >= 0 ? 'text-textMain' : 'text-red-600'}>{chip.net_contracts > 0 ? '+' : ''}{chip.net_contracts.toLocaleString()}</span></td>
                                <td className="px-4 py-2 text-right font-medium tabular-nums"><span className={chip.oi_contracts >= 0 ? 'text-textMain' : 'text-red-600'}>{chip.oi_contracts > 0 ? '+' : ''}{chip.oi_contracts.toLocaleString()}</span></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                  {/* Margin Net */}
                  <div className="bg-cardLight border border-borderLight rounded shadow-sm overflow-hidden flex flex-col">
                    <div className="bg-[#131722] px-4 py-2 text-white font-bold tracking-wide text-sm font-sans">融資融券與借券</div>
                    <div className="overflow-x-auto flex-1">
                      <table className="w-full text-sm text-left">
                        <thead className="text-xs text-textMuted bg-[#F8F9FA] border-b border-borderLight font-sans whitespace-nowrap">
                          <tr>
                            <th className="px-4 py-2 font-semibold font-sans">市場</th>
                            <th className="px-4 py-2 font-semibold text-right font-sans">融資增減(億)</th>
                            <th className="px-4 py-2 font-semibold text-right font-sans">融資餘額(億)</th>
                            <th className="px-4 py-2 font-semibold text-right font-sans">融券增減(萬張)</th>
                            <th className="px-4 py-2 font-semibold text-right font-sans">融券餘額(萬張)</th>
                            <th className="px-4 py-2 font-semibold text-right font-sans">借券增減(萬張)</th>
                            <th className="px-4 py-2 font-semibold text-right font-sans">借券餘額(萬張)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-borderLight">
                          {(twData.chips?.margin || []).map(chip => (
                            <tr key={chip.market} className="hover:bg-gray-50 transition-colors">
                              <td className="px-4 py-2 font-bold text-textMain font-sans whitespace-nowrap">{chip.market}</td>
                              <td className="px-4 py-2 text-right font-medium tabular-nums"><span className={chip.margin_change >= 0 ? 'text-textMain' : 'text-red-600'}>{chip.margin_change > 0 ? '+' : ''}{(chip.margin_change/100000).toFixed(2)}</span></td>
                              <td className="px-4 py-2 text-right font-medium tabular-nums"><span className="text-textMain">{(chip.margin_bal/100000).toFixed(2)}</span></td>
                              <td className="px-4 py-2 text-right font-medium tabular-nums"><span className={chip.short_change >= 0 ? 'text-textMain' : 'text-red-600'}>{chip.short_change > 0 ? '+' : ''}{(chip.short_change/10000).toFixed(2)}</span></td>
                              <td className="px-4 py-2 text-right font-medium tabular-nums"><span className="text-textMain">{(chip.short_bal/10000).toFixed(2)}</span></td>
                              <td className="px-4 py-2 text-right font-medium tabular-nums"><span className={chip.lend_change >= 0 ? 'text-textMain' : 'text-red-600'}>{chip.lend_change > 0 ? '+' : ''}{(chip.lend_change/10000).toFixed(2)}</span></td>
                              <td className="px-4 py-2 text-right font-medium tabular-nums"><span className="text-textMain">{(chip.lend_bal/10000).toFixed(2)}</span></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section>
              <div className="flex flex-col lg:flex-row justify-between items-end mb-4 border-b border-borderLight pb-2">
                <h2 className="text-xl font-bold text-textMain font-sans">類股與主要個股</h2>
                <div className="flex gap-2">
                    <button onClick={() => {setTwMarketTab('TWSE'); setSelectedTwSector(twData?.sectors_data?.TWSE?.[0]?.name)}} className={`px-4 py-1.5 font-sans font-bold text-sm rounded ${twMarketTab === 'TWSE' ? 'bg-[#2962ff] text-white' : 'bg-cardLight text-textMuted border border-borderLight hover:bg-gray-50'}`}>上市 (TWSE)</button>
                    <button onClick={() => {setTwMarketTab('TPEx'); setSelectedTwSector(twData?.sectors_data?.TPEx?.[0]?.name)}} className={`px-4 py-1.5 font-sans font-bold text-sm rounded ${twMarketTab === 'TPEx' ? 'bg-[#2962ff] text-white' : 'bg-cardLight text-textMuted border border-borderLight hover:bg-gray-50'}`}>上櫃 (TPEx)</button>
                </div>
              </div>
              
              <div className="flex flex-col lg:flex-row gap-6 items-start">
                <div className="w-full lg:w-[480px] flex-shrink-0 bg-cardLight border border-borderLight shadow-sm rounded">
                  <div className="px-4 py-3 border-b border-borderLight bg-[#F8F9FA]">
                    <h3 className="font-semibold text-textMain text-sm uppercase tracking-wider font-sans">代表性類股</h3>
                  </div>
                  <div className="grid grid-cols-12 bg-bgLight border-b border-borderLight pr-4">
                    <div className="col-span-3"><SortableHeader label="類別名稱" sortKey="name" currentSort={sortSectors} onSort={handleSortSectors} /></div>
                    <div className="col-span-3"><SortableHeader label="漲跌幅" sortKey="change_pct" currentSort={sortSectors} onSort={handleSortSectors} align="right" /></div>
                    <div className="col-span-3"><SortableHeader label="成交金額(億)" sortKey="volume" currentSort={sortSectors} onSort={handleSortSectors} align="right" /></div>
                    <div className="col-span-3"><SortableHeader label="比重" sortKey="vol_ratio" currentSort={sortSectors} onSort={handleSortSectors} align="right" /></div>
                  </div>
                  <div className="divide-y divide-borderLight max-h-[800px] overflow-y-auto">
                    {sortedTwSectors.map(sec => (
                      <div 
                        key={sec.name} 
                        onClick={() => setSelectedTwSector(sec.name)}
                        className={`grid grid-cols-12 gap-2 px-4 py-3 items-center cursor-pointer transition-colors text-sm
                          ${selectedTwSector === sec.name ? 'bg-[#E3EBFF] border-l-4 border-l-[#2962ff]' : 'hover:bg-[#F8F9FA] border-l-4 border-l-transparent'}`}
                      >
                        <div className="col-span-3 flex flex-col justify-center overflow-hidden">
                          <span className="font-bold text-textMain font-sans truncate" title={sec.name}>{sec.name}</span>
                        </div>
                        <div className="col-span-3 text-right tabular-nums">
                          <ValueCell item={sec} isPct isTaiwan />
                        </div>
                        <div className="col-span-3 text-right font-medium text-textMain tabular-nums truncate text-xs lg:text-sm">
                          {sec.volume.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                        <div className="col-span-3 text-right font-medium text-textMuted tabular-nums text-xs lg:text-sm">
                          {(sec.vol_ratio * 100).toFixed(2)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex-1 w-full bg-cardLight border border-borderLight shadow-sm overflow-x-auto rounded">
                  <div className="px-4 py-3 border-b border-borderLight bg-[#F8F9FA] flex justify-between items-center min-w-[700px]">
                    <h3 className="font-semibold text-textMain text-sm tracking-wider font-sans">
                      排行前 15 大成分股: <span className="text-primary">{selectedTwSector || '請選擇類股'}</span>
                    </h3>
                  </div>
                  
                  <div className="grid grid-cols-12 min-w-[700px] bg-bgLight border-b border-borderLight">
                    <div className="col-span-3"><SortableHeader label="股票" sortKey="symbol" currentSort={sortStocks} onSort={handleSortStocks} /></div>
                    <div className="col-span-2"><SortableHeader label="日期" sortKey="date" currentSort={sortStocks} onSort={handleSortStocks} /></div>
                    <div className="col-span-2"><SortableHeader label="收盤價" sortKey="close_price" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                    <div className="col-span-2"><SortableHeader label="漲跌幅 %" sortKey="change_pct" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                    <div className="col-span-1"><SortableHeader label="成交量(張)" sortKey="volume" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                    <div className="col-span-2"><SortableHeader label="市值(億)" sortKey="market_cap" currentSort={sortStocks} onSort={handleSortStocks} align="right" /></div>
                  </div>
                  
                  <div className="divide-y divide-borderLight min-w-[700px]">
                    {sortedTwStocks.length > 0 ? sortedTwStocks.map(stock => (
                      <div key={stock.symbol} className="grid grid-cols-12 gap-2 px-4 py-3 items-center hover:bg-[#F8F9FA] transition-colors cursor-default text-sm">
                        <div className="col-span-3 flex flex-col justify-center overflow-hidden">
                          <span className="font-bold text-textMain truncate">{stock.name}</span>
                          <span className="text-xs text-textMuted truncate">{stock.symbol}</span>
                        </div>
                        <div className="col-span-2 font-medium text-textMuted tabular-nums">
                          {stock.date}
                        </div>
                        <div className="col-span-2 text-right font-medium text-textMain tabular-nums">
                          {formatPrice(stock.close_price)}
                        </div>
                        <div className="col-span-2 text-right tabular-nums">
                          <ValueCell item={stock} isPct isTaiwan />
                        </div>
                        <div className="col-span-1 text-right font-medium text-textMuted tabular-nums">
                          {stock.volume.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                        </div>
                        <div className="col-span-2 text-right font-medium text-textMuted tabular-nums pr-2">
                           {stock.market_cap.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-24 text-textMuted font-sans">
                        {selectedTwSector ? '此類別無個股資料。' : '請由左側點選類股組合。'}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>

            <section>
              <div className="flex justify-between items-end mb-4 border-b border-borderLight pb-2 mt-8">
                <h2 className="text-xl font-bold text-textMain font-sans">台股強弱勢篩選 (Screener)</h2>
              </div>
              
              <div className="bg-cardLight border border-borderLight shadow-sm rounded overflow-hidden">
                <div className="flex border-b border-borderLight bg-[#F8F9FA] overflow-x-auto">
                  <button 
                    className={`px-8 py-3 font-semibold text-sm transition-colors tracking-wider font-sans
                    ${twScreenerBucket === 'TWSE' ? 'bg-white text-primary border-t-2 border-t-primary border-x border-x-borderLight border-b-0 -mb-[1px]' : 'text-textMuted hover:text-textMain border-b border-b-borderLight'}`}
                    onClick={() => { setTwScreenerBucket('TWSE'); setActiveTwFilter(twScreenerTab === 'upward' ? 'gain_3' : 'loss_3') }}
                  >
                    加權指數 (TWSE)
                  </button>
                  <button 
                    className={`px-8 py-3 font-semibold text-sm transition-colors tracking-wider font-sans
                    ${twScreenerBucket === 'TPEX' ? 'bg-white text-primary border-t-2 border-t-primary border-x border-x-borderLight border-b-0 -mb-[1px]' : 'text-textMuted hover:text-textMain border-b border-b-borderLight'}`}
                    onClick={() => { setTwScreenerBucket('TPEX'); setActiveTwFilter(twScreenerTab === 'upward' ? 'gain_3' : 'loss_3') }}
                  >
                    櫃買指數 (TPEx)
                  </button>
                  <button 
                    className={`px-8 py-3 font-semibold text-sm transition-colors tracking-wider font-sans
                    ${twScreenerBucket === 'Emerging' ? 'bg-white text-primary border-t-2 border-t-primary border-x border-x-borderLight border-b-0 -mb-[1px]' : 'text-textMuted hover:text-textMain border-b border-b-borderLight'}`}
                    onClick={() => { setTwScreenerBucket('Emerging'); setActiveTwFilter(twScreenerTab === 'upward' ? 'gain_3' : 'loss_3') }}
                  >
                    興櫃 (Emerging)
                  </button>
                </div>

                <div className="flex border-b border-borderLight">
                  <button 
                    className={`flex-1 py-2 font-semibold text-sm transition-colors tracking-wider font-sans
                    ${twScreenerTab === 'upward' ? 'bg-[#F8F9FA] text-tw-up border-b-2 border-b-tw-up' : 'text-textMuted hover:text-textMain'}`}
                    onClick={() => { setTwScreenerTab('upward'); setActiveTwFilter('gain_3') }}
                  >
                    上漲組別 (漲幅與創新高)
                  </button>
                  <button 
                    className={`flex-1 py-2 font-semibold text-sm transition-colors tracking-wider font-sans
                    ${twScreenerTab === 'downward' ? 'bg-[#F8F9FA] text-tw-down border-b-2 border-b-tw-down' : 'text-textMuted hover:text-textMain'}`}
                    onClick={() => { setTwScreenerTab('downward'); setActiveTwFilter('loss_3') }}
                  >
                    下跌組別 (跌幅與創新低)
                  </button>
                </div>

                <div className="p-4 bg-[#F8F9FA] border-b border-borderLight flex flex-wrap gap-2">
                  {twScreenerTab === 'upward' ? (
                    <>
                      <span className="text-xs font-bold text-textMuted mr-2 my-auto font-sans">漲幅 (Block 1):</span>
                      {['gain_3|> 3%', 'gain_5|> 5%', 'gain_10|漲停 (>9.5%)'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveTwFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold font-sans transition ${activeTwFilter === k ? 'bg-tw-up text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                      <span className="text-xs font-bold text-textMuted ml-6 mr-2 my-auto font-sans">新高 (Block 2):</span>
                      {['h_30|創30日新高', 'h_90|創90日新高', 'h_180|創180日新高', 'h_all|創歷史新高'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveTwFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold font-sans transition ${activeTwFilter === k ? 'bg-primary text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                    </>
                  ) : (
                    <>
                      <span className="text-xs font-bold text-textMuted mr-2 my-auto font-sans">跌幅 (Block 3):</span>
                      {['loss_3|< -3%', 'loss_5|< -5%', 'loss_10|跌停 (< -9.5%)'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveTwFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold font-sans transition ${activeTwFilter === k ? 'bg-tw-down text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                      <span className="text-xs font-bold text-textMuted ml-6 mr-2 my-auto font-sans">新低 (Block 4):</span>
                      {['l_30|創30日新低', 'l_90|創90日新低', 'l_180|創180日新低', 'l_all|創歷史新低'].map(f => {
                        const [k, lbl] = f.split('|');
                        return <button key={k} onClick={() => setActiveTwFilter(k)} className={`px-3 py-1.5 rounded text-xs font-semibold font-sans transition ${activeTwFilter === k ? 'bg-primary text-white' : 'bg-white border border-borderLight text-textMain hover:bg-gray-100'}`}>{lbl}</button>
                      })}
                    </>
                  )}
                </div>

                <div className="p-4 bg-white min-h-[400px]">
                  {Object.keys(currentTwGroups).length === 0 ? (
                    <div className="text-center py-20 text-textMuted font-sans">
                      當前條件無符合股票資料，或是尚未收到更新資料。
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {Object.entries(currentTwGroups).map(([sectorName, industriesObj]) => (
                        <div key={sectorName} className="border border-borderLight rounded-lg overflow-hidden shadow-sm">
                          <div className="bg-[#131722] px-4 py-2 text-white font-bold tracking-wide text-sm font-sans">
                            {sectorName}
                          </div>
                          
                          {Object.entries(industriesObj).map(([industryName, stocksArr]) => (
                            <div key={industryName} className="border-t border-borderLight first:border-0">
                              <div className="bg-[#F8F9FA] px-4 py-1.5 border-b border-borderLight">
                                <span className="text-xs font-semibold text-textMuted font-sans">{industryName}</span>
                                <span className="ml-2 text-xs font-bold text-textMain bg-white px-2 py-0.5 rounded border border-borderLight">{stocksArr.length}</span>
                              </div>
                              
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                  <thead className="text-xs text-textMuted bg-white border-b border-borderLight font-sans">
                                    <tr>
                                      <th className="px-4 py-2 font-semibold">日期</th>
                                      <th className="px-4 py-2 font-semibold">代號</th>
                                      <th className="px-4 py-2 font-semibold">名稱</th>
                                      <th className="px-4 py-2 font-semibold text-right">收盤價</th>
                                      <th className="px-4 py-2 font-semibold text-right">漲跌幅</th>
                                      <th className="px-4 py-2 font-semibold text-right">成交量</th>
                                      <th className="px-4 py-2 font-semibold text-right">市值</th>
                                      <th className="px-4 py-2 font-semibold text-right">本益比(TTM)</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-borderLight">
                                    {stocksArr.sort((a,b) => b.market_cap - a.market_cap).map(stock => (
                                      <tr key={stock.symbol} className="hover:bg-[#F8F9FA] transition-colors">
                                        <td className="px-4 py-2 text-textMuted whitespace-nowrap">{stock.date}</td>
                                        <td className="px-4 py-2 font-bold text-textMain">{stock.symbol.split(':')[1] || stock.symbol}</td>
                                        <td className="px-4 py-2 text-textMuted truncate max-w-[200px]" title={stock.name}>{stock.name}</td>
                                        <td className="px-4 py-2 text-right font-medium text-textMain tabular-nums">{formatPrice(stock.close_price)}</td>
                                        <td className="px-4 py-2 text-right tabular-nums"><ValueCell item={stock} isPct isTaiwan /></td>
                                        <td className="px-4 py-2 text-right text-textMuted tabular-nums">{formatLargeNum(stock.volume)}</td>
                                        <td className="px-4 py-2 text-right text-textMuted tabular-nums">{formatLargeNum(stock.market_cap)}</td>
                                        <td className="px-4 py-2 text-right text-textMuted tabular-nums">{stock.pe_ratio ? stock.pe_ratio.toFixed(2) : '-'}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </section>
          </div>
        )}

      </main>
    </div>
  )
}

export default App
