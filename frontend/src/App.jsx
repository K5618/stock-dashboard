import { useState, useEffect } from 'react'
import { RefreshCw, TrendingUp, TrendingDown, Clock, BarChart3, PieChart, ExternalLink } from 'lucide-react'

// GitHub Repository URL (User holds this repository)
const GITHUB_REPO_URL = "https://github.com/K5618/stock-dashboard.git"

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
    } catch (e) {
      console.error(e)
      setStatus("Error loading data / Data not generated yet")
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
    const Icon = isUp ? TrendingUp : TrendingDown
    return (
      <div className={`flex items-center space-x-1 ${color} font-semibold`}>
        <Icon size={16} />
        <span>{formatChange(val)}{isPct ? '%' : ''}</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center py-6 border-b border-slate-700">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            Global Stock Dashboard
          </h1>
          <p className="text-slate-400 mt-2 flex items-center space-x-2">
            <Clock size={16} />
            <span>Last Updated: {status}</span>
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex flex-col items-end">
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 px-6 py-3 rounded-xl transition-all duration-200 font-semibold text-slate-200"
          >
            <RefreshCw size={20} />
            <span>Trigger GitHub Actions Update</span>
            <ExternalLink size={16} className="ml-2 opacity-50" />
          </a>
          <p className="text-xs text-slate-500 mt-2">Data updates automatically 5:30 AM Daily</p>
        </div>
      </div>

      {/* Section 1: Global Indices */}
      <section>
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-500/20 rounded-lg"><BarChart3 size={24} className="text-blue-400" /></div>
          <h2 className="text-2xl font-bold">Global Indices</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {indices.map(idx => (
            <div key={idx.symbol} className="bg-cardDark rounded-xl p-5 border border-slate-700 hover:border-blue-500/50 transition-all shadow-lg hover:shadow-[0_0_20px_rgba(16,185,129,0.1)] relative overflow-hidden group">
              <div className={`absolute top-0 w-full h-1 left-0 ${idx.change_pct >= 0 ? "bg-up" : "bg-down"} group-hover:h-1.5 transition-all`}></div>
              <p className="text-sm text-slate-400 mb-1">{idx.symbol}</p>
              <h3 className="text-lg font-bold truncate mb-3">{idx.name}</h3>
              <p className="text-3xl font-light tracking-tight">{formatPrice(idx.close_price)}</p>
              <div className="flex justify-between items-center mt-4 text-sm bg-slate-800/50 p-2 rounded">
                <ValueCell item={idx} />
                <ValueCell item={idx} isPct />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Section 2: US Sectors */}
      <section>
        <div className="flex items-center space-x-3 mb-6 mt-12">
          <div className="p-2 bg-emerald-500/20 rounded-lg"><PieChart size={24} className="text-emerald-400" /></div>
          <h2 className="text-2xl font-bold">US Sector Performance (ETFs)</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {sectors.map(sec => (
            <div key={sec.symbol} className="bg-cardDark rounded-xl p-4 border border-slate-700 flex flex-col justify-between hover:bg-slate-800 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-md font-semibold text-slate-200">{sec.name}</h3>
                <span className="text-xs font-mono text-slate-500 bg-slate-800 px-2 py-1 rounded">{sec.symbol}</span>
              </div>
              <div className="flex justify-between items-end mt-2">
                <span className="text-xl font-medium">{formatPrice(sec.close_price)}</span>
                <ValueCell item={sec} isPct />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Section 3: Top Stocks by Sector */}
      <section>
        <h2 className="text-2xl font-bold mb-6 mt-12">Sector Highlights</h2>
        <div className="space-y-8">
          {Object.entries(topStocks).map(([sector, data]) => (
            <div key={sector} className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-xl font-bold mb-4 text-blue-300">{sector}</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Top Market Cap */}
                <div>
                  <h4 className="text-sm uppercase tracking-wider text-slate-400 mb-3 flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                    <span>Top by Market Cap</span>
                  </h4>
                  <div className="space-y-2">
                    {data.top_market_cap.map(stock => (
                      <div key={stock.symbol} className="bg-cardDark p-3 rounded-lg border border-slate-700/50 flex justify-between items-center hover:bg-slate-800 transition">
                        <div>
                          <p className="font-bold">{stock.symbol}</p>
                          <p className="text-xs text-slate-400">Cap: ${(stock.market_cap / 1e9).toFixed(1)}B</p>
                        </div>
                        <div className="text-right flex flex-col items-end">
                          <p className="font-mono">{formatPrice(stock.close_price)}</p>
                          <ValueCell item={stock} isPct />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Gainers */}
                <div>
                  <h4 className="text-sm uppercase tracking-wider text-slate-400 mb-3 flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Top Gainers</span>
                  </h4>
                  <div className="space-y-2">
                    {data.top_gainers.map(stock => (
                      <div key={stock.symbol} className="bg-cardDark p-3 rounded-lg border border-slate-700/50 flex justify-between items-center hover:bg-slate-800 transition">
                        <div>
                          <p className="font-bold">{stock.symbol}</p>
                          <p className="text-xs text-slate-400">Vol: {(stock.volume / 1e6).toFixed(1)}M</p>
                        </div>
                        <div className="text-right flex flex-col items-end">
                          <p className="font-mono">{formatPrice(stock.close_price)}</p>
                          <ValueCell item={stock} isPct />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {Object.keys(topStocks).length === 0 && (
            <p className="text-slate-500 text-center py-10 italic">No sector data available. Please generate data.json.</p>
          )}
        </div>
      </section>
    </div>
  )
}

export default App
