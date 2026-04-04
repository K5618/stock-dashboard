import { useState, useEffect } from 'react'
import { RefreshCw, ExternalLink } from 'lucide-react'
import { supabase } from './lib/supabase'

function App() {
  const [status, setStatus] = useState("Loading...")
  const [indices, setIndices] = useState([])
  const [sectors, setSectors] = useState([])
  const [topStocks, setTopStocks] = useState({})
  
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
      setIndices(data.indices.data || [])
      setSectors(data.sectors.data || [])
      setTopStocks(data.top_stocks.data || {})
    } catch(e) {
      console.error(e)
      setStatus("Error loading data. Data may not be generated yet.")
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const formatPrice = (val) => val != null ? val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "-"
  const formatChange = (val) => val != null ? `${val >= 0 ? '+' : ''}${val.toFixed(2)}` : "-"
  
  const ValueCell = ({ item, isPct = false }) => {
    const val = isPct ? item.change_pct : item.change_pt
    const isUp = val >= 0
    const color = isUp ? "text-up" : "text-down"
    return (
      <span className={`${color} font-medium tracking-tight`}>
        {formatChange(val)}{isPct ? '%' : ''}
      </span>
    )
  }

  // TradingView Style Summary Card Component
  const MarketCard = ({ item }) => (
    <div className="bg-cardDark p-4 flex flex-col justify-between hover:bg-[#2a2e39] transition-colors border-r border-b border-borderDark cursor-default">
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

  return (
    <div className="min-h-screen bg-bgDark selection:bg-borderDark">
      {/* Sleek Top Navigation Bar */}
      <nav className="bg-cardDark border-b border-borderDark sticky top-0 z-10">
        <div className="max-w-screen-2xl mx-auto px-4 lg:px-8 py-3 flex flex-col sm:flex-row justify-between items-center w-full">
          <div className="flex items-center space-x-6">
            <h1 className="text-xl font-bold tracking-tight text-textMain flex items-center">
              <span className="text-primary mr-2">●</span> US Markets
            </h1>
            <div className="hidden sm:flex space-x-4 text-sm font-medium text-textMuted">
              <span className="hover:text-textMain cursor-pointer transition-colors">Indices</span>
              <span className="hover:text-textMain cursor-pointer transition-colors">Sectors</span>
              <span className="hover:text-textMain cursor-pointer transition-colors">Leaders</span>
            </div>
          </div>
          <div className="mt-2 sm:mt-0 flex items-center space-x-3">
            <div className="flex items-center space-x-1 text-xs text-textMuted bg-bgDark px-3 py-1.5 rounded-sm border border-borderDark">
              <span className="inline-block w-2 h-2 rounded-full bg-up animate-pulse mr-1"></span>
              Live <span className="mx-2">|</span> {status}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area - Strictly Centered and Restrained */}
      <main className="max-w-screen-2xl mx-auto px-4 lg:px-8 py-8 w-full space-y-10">
        
        {/* Section: Global Indices */}
        <section>
          <div className="flex justify-between items-end mb-4 border-b border-borderDark pb-2">
            <h2 className="text-lg font-semibold text-textMain">Major Indices</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 border-l border-t border-borderDark rounded-sm overflow-hidden bg-bgDark">
            {indices.map(idx => (
              <MarketCard key={idx.symbol} item={idx} />
            ))}
          </div>
        </section>

        {/* Section: Sectors */}
        <section>
          <div className="flex justify-between items-end mb-4 border-b border-borderDark pb-2">
            <h2 className="text-lg font-semibold text-textMain">Sectors Performance</h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 border-l border-t border-borderDark rounded-sm overflow-hidden bg-bgDark">
            {sectors.map(sec => (
              <MarketCard key={sec.symbol} item={sec} />
            ))}
          </div>
        </section>

        {/* Section: Top Stocks Data Tables */}
        <section>
          <div className="flex justify-between items-end mb-4 border-b border-borderDark pb-2">
            <h2 className="text-lg font-semibold text-textMain">Sector Leaders & Gainers</h2>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-6">
            {Object.entries(topStocks).map(([sector, data]) => (
              <div key={sector} className="bg-cardDark border border-borderDark rounded-sm overflow-hidden flex flex-col shadow-lg">
                <div className="px-4 py-3 border-b border-borderDark flex items-center justify-between bg-[#1a1e27]">
                  <h3 className="font-semibold text-textMain text-sm uppercase tracking-wider">{sector}</h3>
                </div>
                
                <div className="flex-1">
                  {/* Table Header */}
                  <div className="grid grid-cols-12 gap-2 px-4 py-2 text-xs font-medium text-textMuted border-b border-borderDark bg-[#1e222d]">
                    <div className="col-span-6">Symbol</div>
                    <div className="col-span-3 text-right">Last</div>
                    <div className="col-span-3 text-right">Chg%</div>
                  </div>
                  
                  {/* Market Cap Leaders */}
                  <div className="divide-y divide-borderDark">
                    <div className="px-4 py-1 bg-[#1a1e27] text-xs font-semibold text-primary">Largest by Market Cap</div>
                    {data.top_market_cap.map(stock => (
                      <div key={stock.symbol} className="grid grid-cols-12 gap-2 px-4 py-2.5 items-center hover:bg-[#2a2e39] transition-colors cursor-default text-sm">
                        <div className="col-span-6 flex flex-col justify-center overflow-hidden">
                          <span className="font-bold text-textMain truncate">{stock.symbol}</span>
                          <span className="text-xs text-textMuted truncate">{stock.name}</span>
                        </div>
                        <div className="col-span-3 text-right font-medium text-textMain tabular-nums">
                          {formatPrice(stock.close_price)}
                        </div>
                        <div className="col-span-3 text-right tabular-nums">
                          <ValueCell item={stock} isPct />
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Top Gainers Divider */}
                  <div className="divide-y divide-borderDark border-t border-borderDark">
                    <div className="px-4 py-1 bg-[#1a1e27] text-xs font-semibold text-up">Top Gainers</div>
                    {data.top_gainers.map(stock => (
                      <div key={stock.symbol} className="grid grid-cols-12 gap-2 px-4 py-2.5 items-center hover:bg-[#2a2e39] transition-colors cursor-default text-sm">
                        <div className="col-span-6 flex flex-col justify-center overflow-hidden">
                          <span className="font-bold text-textMain truncate">{stock.symbol}</span>
                          <span className="text-xs text-textMuted truncate">{stock.name}</span>
                        </div>
                        <div className="col-span-3 text-right font-medium text-textMain tabular-nums">
                          {formatPrice(stock.close_price)}
                        </div>
                        <div className="col-span-3 text-right tabular-nums">
                          <ValueCell item={stock} isPct />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {Object.keys(topStocks).length === 0 && (
            <div className="text-center py-24 bg-cardDark border border-borderDark rounded-sm text-textMuted">
              Market data is currently unavailable.
            </div>
          )}
        </section>

      </main>
    </div>
  )
}

export default App
