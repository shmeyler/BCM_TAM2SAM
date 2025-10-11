"""
SpyFu API Service for PPC Competitive Intelligence
Provides methods to retrieve competitor PPC data, keywords, and ad intelligence
"""

import os
import asyncio
import base64
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Data Models for SpyFu API Responses
class PPCKeyword(BaseModel):
    """PPC Keyword data from SpyFu API"""
    keyword: str
    monthly_searches: Optional[int] = 0
    cpc: Optional[float] = 0.0
    competition: Optional[str] = "Unknown"
    position: Optional[int] = None
    estimated_monthly_cost: Optional[float] = 0.0

class PPCCompetitor(BaseModel):
    """PPC Competitor data from SpyFu API"""
    domain: str
    overlapping_keywords: Optional[int] = 0
    estimated_monthly_spend: Optional[float] = 0.0
    shared_keywords_count: Optional[int] = 0

class AdHistoryEntry(BaseModel):
    """Ad History entry from SpyFu API"""
    ad_text: str
    keyword: str
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    position: Optional[int] = None

class DomainStats(BaseModel):
    """Domain statistics from SpyFu API"""
    domain: str
    organic_keywords: Optional[int] = 0
    paid_keywords: Optional[int] = 0
    estimated_monthly_organic_traffic: Optional[int] = 0
    estimated_monthly_paid_traffic: Optional[int] = 0
    estimated_monthly_ad_spend: Optional[float] = 0.0

class PPCIntelligenceReport(BaseModel):
    """Complete PPC Intelligence Report"""
    target_domain: str
    paid_keywords: List[PPCKeyword] = []
    top_competitors: List[PPCCompetitor] = []
    ad_history: List[AdHistoryEntry] = []
    domain_stats: Optional[DomainStats] = None
    confidence_level: str = "Medium"

class SpyFuService:
    """Service class for SpyFu API integration"""
    
    def __init__(self):
        self.api_key = os.environ.get('SPYFU_API_KEY')
        self.base_url = "https://www.spyfu.com/v3"
        
        if not self.api_key:
            logger.warning("SpyFu API key not found. PPC intelligence will be limited.")
            self.available = False
        else:
            self.available = True
            
        # SpyFu uses API key as query parameter, no auth header needed
        self.auth_header = {}
    
    async def get_ppc_keywords(self, domain: str, limit: int = 50) -> List[PPCKeyword]:
        """Get PPC keywords for a domain"""
        if not self.available:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/kombat_api/competing_ppc_keywords"
                params = {
                    "r": domain,  # SpyFu uses 'r' parameter for domain
                    "api_key": self.api_key
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers=self.auth_header
                )
                
                if response.status_code == 200:
                    data = response.json()
                    keywords = []
                    
                    for item in data.get('results', []):
                        keywords.append(PPCKeyword(
                            keyword=item.get('keyword', ''),
                            monthly_searches=item.get('monthly_searches', 0),
                            cpc=float(item.get('cpc', 0.0)),
                            competition=item.get('competition', 'Unknown'),
                            position=item.get('position'),
                            estimated_monthly_cost=float(item.get('estimated_cost', 0.0))
                        ))
                    
                    logger.info(f"Retrieved {len(keywords)} PPC keywords for {domain}")
                    return keywords
                else:
                    logger.warning(f"SpyFu API returned status {response.status_code} for domain {domain}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error retrieving PPC keywords for {domain}: {e}")
            return []
    
    async def get_ppc_competitors(self, domain: str, limit: int = 20) -> List[PPCCompetitor]:
        """Get top PPC competitors for a domain"""
        if not self.available:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/paid_serp_api/paid_serps"
                params = {
                    "r": domain,  # SpyFu uses 'r' parameter for domain
                    "api_key": self.api_key
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers=self.auth_header
                )
                
                if response.status_code == 200:
                    data = response.json()
                    competitors = []
                    
                    for item in data.get('results', []):
                        competitors.append(PPCCompetitor(
                            domain=item.get('domain', ''),
                            overlapping_keywords=item.get('overlapping_keywords', 0),
                            estimated_monthly_spend=float(item.get('estimated_spend', 0.0)),
                            shared_keywords_count=item.get('shared_keywords', 0)
                        ))
                    
                    logger.info(f"Retrieved {len(competitors)} PPC competitors for {domain}")
                    return competitors
                else:
                    logger.warning(f"SpyFu competitors API returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error retrieving PPC competitors for {domain}: {e}")
            return []
    
    async def get_ad_history(self, domain: str, limit: int = 25) -> List[AdHistoryEntry]:
        """Get ad history for a domain"""
        if not self.available:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/ad_history_api/domain_ad_history"
                params = {
                    "r": domain,  # SpyFu uses 'r' parameter for domain
                    "api_key": self.api_key
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers=self.auth_header
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ads = []
                    
                    for item in data.get('results', []):
                        ads.append(AdHistoryEntry(
                            ad_text=item.get('ad_text', ''),
                            keyword=item.get('keyword', ''),
                            first_seen=item.get('first_seen'),
                            last_seen=item.get('last_seen'),
                            position=item.get('position')
                        ))
                    
                    logger.info(f"Retrieved {len(ads)} ad history entries for {domain}")
                    return ads
                else:
                    logger.warning(f"SpyFu ad history API returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error retrieving ad history for {domain}: {e}")
            return []
    
    async def get_domain_stats(self, domain: str) -> Optional[DomainStats]:
        """Get comprehensive domain statistics"""
        if not self.available:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/organic_serp_api/serp_analysis_keywords"
                params = {
                    "r": domain,  # SpyFu uses 'r' parameter for domain
                    "api_key": self.api_key
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers=self.auth_header
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    stats = DomainStats(
                        domain=domain,
                        organic_keywords=data.get('organic_keywords', 0),
                        paid_keywords=data.get('paid_keywords', 0),
                        estimated_monthly_organic_traffic=data.get('organic_traffic', 0),
                        estimated_monthly_paid_traffic=data.get('paid_traffic', 0),
                        estimated_monthly_ad_spend=float(data.get('estimated_spend', 0.0))
                    )
                    
                    logger.info(f"Retrieved domain stats for {domain}")
                    return stats
                else:
                    logger.warning(f"SpyFu domain stats API returned status {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving domain stats for {domain}: {e}")
            return None
    
    async def generate_ppc_intelligence_report(self, domain: str) -> PPCIntelligenceReport:
        """Generate comprehensive PPC intelligence report for a domain"""
        logger.info(f"Generating PPC intelligence report for {domain}")
        
        # Clean domain (remove protocol, www, etc.)
        clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        # For now, generate realistic demo data while SpyFu API access is being configured
        # This shows the user what PPC intelligence will look like
        logger.info(f"Generating demo PPC intelligence data for {clean_domain}")
        
        # Generate realistic demo keywords based on domain
        demo_keywords = self._generate_demo_keywords(clean_domain)
        demo_competitors = self._generate_demo_competitors(clean_domain)
        demo_ads = self._generate_demo_ads(clean_domain)
        demo_stats = self._generate_demo_stats(clean_domain)
        
        report = PPCIntelligenceReport(
            target_domain=clean_domain,
            paid_keywords=demo_keywords,
            top_competitors=demo_competitors,
            ad_history=demo_ads,
            domain_stats=demo_stats,
            confidence_level="Demo Data - SpyFu Integration Pending"
        )
        
        logger.info(f"Demo PPC intelligence report generated for {clean_domain}: {len(demo_keywords)} keywords, {len(demo_competitors)} competitors")
        return report
    
    def _generate_demo_keywords(self, domain: str) -> List[PPCKeyword]:
        """Generate realistic demo PPC keywords"""
        # Extract business type from domain for relevant keywords
        domain_lower = domain.lower()
        
        if 'event' in domain_lower or 'rental' in domain_lower:
            base_keywords = [
                ("event rentals", 5400, 2.45, "Medium"),
                ("party equipment rental", 1200, 3.20, "High"),
                ("wedding rentals", 3600, 4.15, "High"),
                ("tent rental near me", 2200, 2.80, "Medium"),
                ("corporate event planning", 1800, 5.30, "High"),
                ("event supplies rental", 900, 2.10, "Low"),
                ("party tent rental", 1500, 3.45, "Medium"),
                ("event equipment rental", 800, 2.95, "Medium")
            ]
        else:
            # Generic business keywords
            base_keywords = [
                (f"{domain.split('.')[0]} services", 2400, 3.25, "Medium"),
                (f"best {domain.split('.')[0]}", 1800, 2.90, "High"),
                (f"{domain.split('.')[0]} near me", 3200, 2.15, "Low"),
                (f"professional {domain.split('.')[0]}", 1100, 4.20, "High"),
                (f"affordable {domain.split('.')[0]}", 950, 2.80, "Medium")
            ]
        
        keywords = []
        for i, (keyword, searches, cpc, comp) in enumerate(base_keywords):
            estimated_cost = searches * cpc * 0.3  # Rough estimate
            keywords.append(PPCKeyword(
                keyword=keyword,
                monthly_searches=searches,
                cpc=cpc,
                competition=comp,
                position=i + 1,
                estimated_monthly_cost=estimated_cost
            ))
        
        return keywords
    
    def _generate_demo_competitors(self, domain: str) -> List[PPCCompetitor]:
        """Generate realistic demo PPC competitors"""
        domain_lower = domain.lower()
        
        if 'event' in domain_lower or 'rental' in domain_lower:
            competitor_domains = [
                ("partyrentals.com", 45, 12500),
                ("eventnetwork.com", 38, 8900),
                ("aaaeventrental.com", 32, 15200),
                ("partypro.com", 28, 7800),
                ("rentalequipment.com", 25, 9400)
            ]
        else:
            # Generic competitors based on domain name
            base_name = domain.split('.')[0]
            competitor_domains = [
                (f"{base_name}pro.com", 35, 8500),
                (f"best{base_name}.com", 28, 6200),
                (f"{base_name}services.net", 22, 4800),
                (f"elite{base_name}.com", 18, 7100)
            ]
        
        competitors = []
        for domain_name, keywords, spend in competitor_domains:
            competitors.append(PPCCompetitor(
                domain=domain_name,
                overlapping_keywords=keywords,
                estimated_monthly_spend=spend,
                shared_keywords_count=keywords
            ))
        
        return competitors
    
    def _generate_demo_ads(self, domain: str) -> List[AdHistoryEntry]:
        """Generate realistic demo ad examples"""
        domain_lower = domain.lower()
        
        if 'event' in domain_lower or 'rental' in domain_lower:
            ad_examples = [
                ("Premium Event Rentals - Free Delivery & Setup. Quality Equipment for Memorable Events!", "event rentals"),
                ("Wedding Tent Rentals - Beautiful, Weather-Proof Tents. Book Your Dream Wedding Today!", "wedding tent rental"),
                ("Corporate Event Planning - Full Service Event Management. Call for Free Quote!", "corporate events"),
                ("Party Equipment Rental - Tables, Chairs, Linens & More. Same-Day Delivery Available!", "party rentals")
            ]
        else:
            base_name = domain.split('.')[0].title()
            ad_examples = [
                (f"{base_name} Services - Professional & Reliable. Get Your Free Estimate Today!", f"{base_name.lower()} services"),
                (f"Best {base_name} in Town - 5-Star Reviews. Call Now for Special Pricing!", f"best {base_name.lower()}"),
                (f"Affordable {base_name} Solutions - Quality Work, Fair Prices. Book Online!", f"affordable {base_name.lower()}")
            ]
        
        ads = []
        for i, (ad_text, keyword) in enumerate(ad_examples):
            ads.append(AdHistoryEntry(
                ad_text=ad_text,
                keyword=keyword,
                position=i + 1
            ))
        
        return ads
    
    def _generate_demo_stats(self, domain: str) -> DomainStats:
        """Generate realistic demo domain statistics"""
        return DomainStats(
            domain=domain,
            organic_keywords=1250,
            paid_keywords=185,
            estimated_monthly_organic_traffic=8400,
            estimated_monthly_paid_traffic=2100,
            estimated_monthly_ad_spend=15800
        )

# Global service instance
spyfu_service = SpyFuService()

# Helper function to extract domain from company name
def extract_domain_from_company(company_name: str) -> str:
    """Extract likely domain from company name for SpyFu analysis"""
    # Basic domain extraction - can be enhanced
    clean_name = company_name.lower().strip()
    
    # Common mappings
    domain_mappings = {
        'apple': 'apple.com',
        'google': 'google.com',
        'microsoft': 'microsoft.com',
        'amazon': 'amazon.com',
        'facebook': 'facebook.com',
        'meta': 'facebook.com',
        'netflix': 'netflix.com',
        'spotify': 'spotify.com',
        'uber': 'uber.com',
        'airbnb': 'airbnb.com',
        'paypal': 'paypal.com',
        'stripe': 'stripe.com',
        'salesforce': 'salesforce.com',
        'slack': 'slack.com',
        'shopify': 'shopify.com',
        'starbucks': 'starbucks.com',
        'mcdonalds': 'mcdonalds.com',
        'coca cola': 'coca-cola.com',
        'pepsi': 'pepsi.com',
        'nike': 'nike.com',
        'adidas': 'adidas.com',
        'walmart': 'walmart.com',
        'target': 'target.com',
        'home depot': 'homedepot.com',
        'best buy': 'bestbuy.com'
    }
    
    # Check for direct matches first
    if clean_name in domain_mappings:
        return domain_mappings[clean_name]
    
    # Check for partial matches
    for company, domain in domain_mappings.items():
        if company in clean_name or clean_name in company:
            return domain
    
    # Fallback: try to construct domain from company name
    # Remove common words and create potential domain
    words_to_remove = ['inc', 'corp', 'corporation', 'company', 'ltd', 'llc', 'the', 'and', '&']
    name_parts = [word for word in clean_name.split() if word not in words_to_remove]
    
    if name_parts:
        potential_domain = ''.join(name_parts) + '.com'
        return potential_domain
    
    return clean_name + '.com'