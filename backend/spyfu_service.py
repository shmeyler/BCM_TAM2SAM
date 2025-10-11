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
            
        # Create auth header
        self.auth_header = None
        if self.available:
            # SpyFu uses the API key as username with empty password for Basic Auth
            credentials = f"{self.api_key}:"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.auth_header = {"Authorization": f"Basic {encoded_credentials}"}
    
    async def get_ppc_keywords(self, domain: str, limit: int = 50) -> List[PPCKeyword]:
        """Get PPC keywords for a domain"""
        if not self.available:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/domain_stats_api/ppc_keywords"
                params = {
                    "domain": domain,
                    "limit": limit
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
                url = f"{self.base_url}/competitor_api/ppc_competitors"
                params = {
                    "domain": domain,
                    "limit": limit
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
                url = f"{self.base_url}/ad_history_api/domain_ads"
                params = {
                    "domain": domain,
                    "limit": limit
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
                url = f"{self.base_url}/domain_stats_api/all_stats"
                params = {"domain": domain}
                
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
        
        if not self.available:
            return PPCIntelligenceReport(
                target_domain=clean_domain,
                confidence_level="Low - SpyFu API Not Available"
            )
        
        try:
            # Make all API calls concurrently
            keywords_task = self.get_ppc_keywords(clean_domain, 50)
            competitors_task = self.get_ppc_competitors(clean_domain, 20)
            ad_history_task = self.get_ad_history(clean_domain, 25)
            domain_stats_task = self.get_domain_stats(clean_domain)
            
            # Wait for all to complete
            keywords, competitors, ad_history, domain_stats = await asyncio.gather(
                keywords_task,
                competitors_task, 
                ad_history_task,
                domain_stats_task,
                return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(keywords, Exception):
                logger.error(f"Keywords task failed: {keywords}")
                keywords = []
            if isinstance(competitors, Exception):
                logger.error(f"Competitors task failed: {competitors}")
                competitors = []
            if isinstance(ad_history, Exception):
                logger.error(f"Ad history task failed: {ad_history}")
                ad_history = []
            if isinstance(domain_stats, Exception):
                logger.error(f"Domain stats task failed: {domain_stats}")
                domain_stats = None
            
            # Determine confidence level based on available data
            confidence_level = "High"
            if len(keywords) == 0 and len(competitors) == 0:
                confidence_level = "Low - Limited Data Available"
            elif len(keywords) < 10 or len(competitors) < 5:
                confidence_level = "Medium - Partial Data Available"
                
            report = PPCIntelligenceReport(
                target_domain=clean_domain,
                paid_keywords=keywords or [],
                top_competitors=competitors or [],
                ad_history=ad_history or [],
                domain_stats=domain_stats,
                confidence_level=confidence_level
            )
            
            logger.info(f"PPC intelligence report generated for {clean_domain}: {len(keywords)} keywords, {len(competitors)} competitors")
            return report
            
        except Exception as e:
            logger.error(f"Error generating PPC intelligence report for {domain}: {e}")
            return PPCIntelligenceReport(
                target_domain=clean_domain,
                confidence_level="Low - Error Occurred"
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