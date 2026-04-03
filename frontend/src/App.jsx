import { useState, useEffect } from 'react'
import { RefreshCw, ExternalLink } from 'lucide-react'

// GitHub Repository URL (User holds this repository)
const GITHUB_REPO_URL = "https://github.com/K5618/stock-dashboard/actions"

function App() {
  const [status, setStatus] = useState("Loading...")
  const [indices, setIndices] = useState([])
  const [sectors, setSectors] = useState([])
  const [topStocks, setTopStocks] = useState({})
  
  const fetchData = async () => {
    try {
      // In production (Github Pages), this fetches relative from public directory
      const res = await fetch('./data.json?v=' + new Date().getTime())
      const data = await res.json()
      
      setStatus(data.status.last_updated)
      setIndices(data.indices.data || [])
      setSectors(data.sectors.data || [])
      setTopStocks(data.top_stocks.data || {})
    } catch(e) {
      console.error(e)
      setStatus("Error loading data. Run Action to generate data.json")
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
      <div className={`flex items-center space-x-1 ${color} font-medium`}>
        <span>{formatChange(val)}{isPct ? '%' : ''}</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-12">
      {/* Header Bar */}
      <div className="bg-cardLight border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col sm:flex-row justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold tracking-tight text-textDark">Market Overview</h1>
            <span className="text-sm font-medium text-textMuted bg-gray-100 px-3 py-1 rounded-full">
              Updated: {status}
            </span>
          </div>
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 sm:mt-0 flex items-center space-x-2 bg-primary hover:bg-blue-700 text-white px-5 py-2 rounded-lg transition-colors font-semibold text-sm shadow-sm hover:shadow-md"
          >
            <RefreshCw size={16} />
            <span>Update Data</span>
            <ExternalLink size={14} className="opacity-70" />
          </a>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 space-y-12 mt-8">
        
        {/* Section: Global Indices */}
        <section>
          <h2 className="text-xl font-bold text-textDark mb-4">Indices</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {indices.map(idx => (
              <div key={idx.symbol} className="bg-cardLight rounded-lg p-4 border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all cursor-default">
                <div className="flex justify-between items-start mb-2">
                  <div className="overflow-hidden w-full">
                    <h3 className="font-bold text-textDark text-sm sm:text-base truncate" title={idx.name}>{idx.name}</h3>
                    <p className="text-xs text-textMuted font-mono truncate">{idx.symbol}</p>
                  </div>
                </div>
                <div className="mt-3">
                  <p className="text-xl font-semibold text-textDark tracking-tight">{formatPrice(idx.close_price)}</p>
                  <div className="flex space-x-3 mt-1 text-sm bg-gray-50/50 p-1.5 rounded">
                    <ValueCell item={idx} />
                    <ValueCell item={idx} isPct />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Section: Sectors */}
        <section>
          <h2 className="text-xl font-bold text-textDark mb-4">Sectors (US)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {sectors.map(sec => (
              <div key={sec.symbol} className="bg-cardLight rounded-lg p-4 border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all">
                <h3 className="font-bold text-gray-800 text-sm truncate" title={sec.name}>{sec.name}</h3>
                <p className="text-xs text-textMuted font-mono mb-2">{sec.symbol}</p>
                <p className="text-lg font-medium text-textDark mb-1">{formatPrice(sec.close_price)}</p>
                <div className="flex justify-between text-sm">
                  <ValueCell item={sec} isPct />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Section: Top Stocks */}
        <section>
          <h2 className="text-xl font-bold text-textDark mb-4">Sector Leaders</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {Object.entries(topStocks).map(([sector, data]) => (
              <div key={sector} className="bg-cardLight rounded-lg border border-gray-200 overflow-hidden shadow-sm">
                <div className="bg-gray-50 px-5 py-3 border-b border-gray-200 flex justify-between items-center">
                  <h3 className="font-bold text-textDark">{sector}</h3>
                </div>
                <div className="p-0">
                  {/* Market Cap Leaders */}
                  <div className="px-5 py-3 bg-white">
                    <h4 className="text-xs font-semibold text-textMuted uppercase tracking-wider mb-2">Largest by Market Cap</h4>
                    <ul className="divide-y divide-gray-100">
                      {data.top_market_cap.map(stock => (
                        <li key={stock.symbol} className="py-2.5 flex justify-between items-center hover:bg-gray-50 -mx-2 px-2 rounded transition-colors group">
                          <div className="flex items-center space-x-3 overflow-hidden mr-2">
                            <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center border border-gray-200 text-primary font-bold text-xs shrink-0 group-hover:bg-blue-50 group-hover:border-blue-200 transition-colors">
                              {stock.symbol.slice(0, 3)}
                            </div>
                            <div className="truncate pr-2 max-w-[150px] sm:max-w-[200px]">
                              <p className="font-bold text-sm text-textDark truncate leading-tight">{stock.symbol}</p>
                              <p className="text-xs text-textMuted truncate leading-tight" title={stock.name}>{stock.name}</p>
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <p className="text-sm font-medium text-textDark">{formatPrice(stock.close_price)}</p>
                            <div className="text-xs flex justify-end"><ValueCell item={stock} isPct /></div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Top Gainers Divider */}
                  <div className="h-px bg-gray-100 mx-5 w-auto"></div>

                  {/* Top Gainers */}
                  <div className="px-5 py-3 bg-white">
                    <h4 className="text-xs font-semibold text-textMuted uppercase tracking-wider mb-2">Top Gainers</h4>
                    <ul className="divide-y divide-gray-100">
                      {data.top_gainers.map(stock => (
                        <li key={stock.symbol} className="py-2.5 flex justify-between items-center hover:bg-gray-50 -mx-2 px-2 rounded transition-colors group">
                          <div className="flex items-center space-x-3 overflow-hidden mr-2">
                            <div className="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center border border-green-100 text-up font-bold text-xs shrink-0 group-hover:bg-green-100 transition-colors">
                              {stock.symbol.slice(0, 3)}
                            </div>
                            <div className="truncate pr-2 max-w-[150px] sm:max-w-[200px]">
                              <p className="font-bold text-sm text-textDark truncate leading-tight">{stock.symbol}</p>
                              <p className="text-xs text-textMuted truncate leading-tight" title={stock.name}>{stock.name}</p>
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <p className="text-sm font-medium text-textDark">{formatPrice(stock.close_price)}</p>
                            <div className="text-xs flex justify-end"><ValueCell item={stock} isPct /></div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>

                </div>
              </div>
            ))}
          </div>
          {Object.keys(topStocks).length === 0 && (
            <div className="text-center py-20 bg-cardLight border border-gray-200 rounded-lg">
              <p className="text-textMuted">Data not yet synchronized. Please trigger an update.</p>
            </div>
          )}
        </section>

      </div>
    </div>
  )
}

export default App
