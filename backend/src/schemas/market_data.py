# src/schemas/market_data.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class StockBasic(BaseModel):
    symbol: str
    name: str
    date: str
    close_price: float = Field(default=0.0)
    change_pct: Optional[float] = Field(default=None)

class IndiceData(StockBasic):
    change_pt: Optional[float] = Field(default=0.0)
    volume: Optional[float] = Field(default=0.0)

class SectorETFData(StockBasic):
    change_pt: Optional[float] = Field(default=0.0)

class CommodityData(StockBasic):
    change_pt: Optional[float] = Field(default=0.0)
    exchange: Optional[str] = Field(default="CME/ICE")

class ScreenerStock(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = Field(default="Unknown")
    industry: Optional[str] = Field(default="Unknown")
    close_price: Optional[float] = Field(default=0.0)
    change_pct: Optional[float] = Field(default=None)
    volume: Optional[float] = Field(default=0.0)
    market_cap: Optional[float] = Field(default=0.0)
    pe_ratio: Optional[float] = Field(default=None)
    date: str

class TopStock(BaseModel):
    symbol: str
    name: str
    sector: str
    date: str
    close_price: float = Field(default=0.0)
    change_pt: Optional[float] = Field(default=0.0)
    change_pct: Optional[float] = Field(default=None)
    volume: float = Field(default=0.0)
    market_cap: float = Field(default=0.0)

class InstitutionalChip(BaseModel):
    entity: str
    twse_net: float = Field(default=0.0)
    tpex_net: float = Field(default=0.0)

class FuturesChip(BaseModel):
    entity: str
    net_contracts: int = Field(default=0)
    oi_contracts: int = Field(default=0)

class MarginChip(BaseModel):
    market: str
    margin_change: float = Field(default=0.0)
    margin_bal: float = Field(default=0.0)
    short_change: float = Field(default=0.0)
    short_bal: float = Field(default=0.0)
    lend_change: float = Field(default=0.0)
    lend_bal: float = Field(default=0.0)

class MarketSnapshot(BaseModel):
    status: Dict[str, Any]
    indices: Dict[str, Any]
    sectors: Dict[str, Any]
    top_stocks: Dict[str, Any]
    screener: Dict[str, Any]
    commodities: Optional[Dict[str, Any]] = None
    chips: Optional[Dict[str, Any]] = None
    sectors_data: Optional[Dict[str, Any]] = None
