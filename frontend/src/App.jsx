import { useState, useEffect } from 'react'
import { supabase } from './lib/supabase'

function App() {
  const [isAuth, setIsAuth] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [authError, setAuthError] = useState('')

  const [status, setStatus] = useState("Loading...")
  const [indices, setIndices] = useState({ US: [], Europe: [], Asia: [] })
  
  // Data sets
  const [sectors, setSectors] = useState([])
  const [topStocks, setTopStocks] = useState({})
  const [screener, setScreener] = useState(null)
  const [commodities, setCommodities] = useState(null)
  
  // Interaction States
  const [selectedSector, setSelectedSector] = useState(null)
  
  // Sorting States
  const [sortSectors, setSortSectors] = useState({ key: 'change_pct', direction: 'desc' })
  const [sortStocks, setSortStocks] = useState({ key: 'market_cap', direction: 'desc' })

  // Screener States
  const [screenerTab, setScreenerTab] = useState('upward') // 'upward' | 'downward'
  const [activeFilter, setActiveFilter] = useState('gain_3') // default for upward

  // Main Top Nav Tabs
  const [mainTab, setMainTab] = useState('us_stocks') // 'us_stocks' | 'commodities'

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
      const { data: snapshots, error } = await supabase
        .from('market_snapshots')
        .select('data')
        .order('created_at', { ascending: false })
        .limit(1)

      if (error) throw error
      if (!snapshots || snapshots.length === 0) throw new Error("No data found")
      
      const data = snapshots[0].data
      
      setStatus(data.status.last_updated)
      setIndices(data.indices?.data || { US: [], Europe: [], Asia: [] })
      setSectors(data.sectors?.data || [])
      setTopStocks(data.top_stocks?.data || {})
      setScreener(data.screener || null)
      setCommodities(data.commodities || null)
      
      if (data.sectors?.data?.length > 0) {
        setSelectedSector(data.sectors.data[0].name)
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
  
  const ValueCell = ({ item, isPct = false }) => {
    const val = isPct ? item.change_pct : item.change_pt
    const isUp = val >= 0
    const color = isUp ? "text-up" : "text-down"
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

  const MarketCard = ({ item }) => (
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
          <ValueCell item={item} />
          <ValueCell item={item} isPct />
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
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1 text-xs text-textMuted bg-bgLight px-3 py-1.5 rounded-sm border border-borderLight font-mono">
              <span className="inline-block w-2 h-2 rounded-full bg-up animate-pulse mr-1"></span>
              LIVE DATA <span className="mx-2">|</span> {status}
            </div>
            <button onClick={() => setIsAuth(false)} className="text-sm text-textMuted hover:text-textMain underline ml-4">登出 Logout</button>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-[1600px] mx-auto px-4 lg:px-8 py-8 w-full space-y-10">
        
        {mainTab === 'us_stocks' && (
          <>
            <section>
              <div className="flex justify-between items-end mb-4 border-b border-borderLight pb-2">
                <h2 className="text-xl font-bold text-textMain">Major Indices</h2>
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
                <h2 className="text-xl font-bold text-textMain">Sectors Performance & Top Components</h2>
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
                <h2 className="text-xl font-bold text-textMain">US Top 1200 Quant Screener</h2>
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
                    <h2 className="text-2xl font-bold text-[#131722]">{marketBlock}</h2>
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

      </main>
    </div>
  )
}

export default App
