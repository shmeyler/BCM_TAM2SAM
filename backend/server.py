from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from together import Together
import json
import io
import pandas as pd
from fastapi.responses import StreamingResponse, Response
import asyncio
import sys
import os
from pdf_generator import create_market_report_pdf

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

# Together AI setup with Kimi K2 Instruct
together_client = None
try:
    together_client = Together(
        api_key=os.environ.get('TOGETHER_API_KEY', '')
    )
    logger.info("Together AI client initialized successfully with Kimi K2 Instruct 0905")
except Exception as e:
    logger.error(f"Failed to initialize Together AI client: {e}")
    together_client = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class MarketInput(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    industry: str
    geography: str
    target_user: str
    demand_driver: str
    transaction_type: str
    key_metrics: str
    benchmarks: Optional[str] = ""
    output_format: str = "excel"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MarketSegment(BaseModel):
    name: str
    description: str
    size_estimate: float
    growth_rate: float
    key_players: List[str]

class Competitor(BaseModel):
    name: str
    strengths: List[str]
    weaknesses: List[str]
    market_share: Optional[float] = None
    price_range: Optional[str] = None
    price_tier: Optional[str] = None
    innovation_focus: Optional[str] = None
    user_segment: Optional[str] = None

class MarketMap(BaseModel):
    id: str
    market_input_id: str
    # Market Overview
    total_market_size: float
    market_growth_rate: float
    key_drivers: List[str]
    # Market Segmentation
    segmentation_by_geographics: List[MarketSegment]
    segmentation_by_demographics: List[MarketSegment]
    segmentation_by_psychographics: List[MarketSegment]
    segmentation_by_behavioral: List[MarketSegment]
    # Competitive Analysis
    competitors: List[Competitor]
    # Strategic Analysis
    opportunities: List[str]
    threats: List[str]
    strategic_recommendations: List[str]
    # Executive Summary
    executive_summary: str
    # Sources and Methodology
    data_sources: List[str]
    confidence_level: str
    methodology: str
    timestamp: datetime

class MarketAnalysis(BaseModel):
    market_input: MarketInput
    market_map: MarketMap
    visual_map: Optional[Dict[str, Any]] = None

# Enhanced AI Agent Classes
class MarketIntelligenceAgent:
    @staticmethod
    def get_curated_market_data(product_name: str, industry: str, geography: str) -> Dict[str, Any]:
        """Get curated market data for common market segments"""
        # Curated database of realistic market segments
        market_segments = {
            # Craft Beer Markets
            ("craft beer", "food & beverage", "united states"): {
                "tam": 27800000000,  # $27.8B (Brewers Association)
                "growth_rate": 0.084,  # 8.4% CAGR
                "competitors": ["Sierra Nevada", "Stone Brewing", "New Belgium", "Dogfish Head", "Bell's Brewery"],
                "sources": ["Brewers Association", "IBISWorld"],
                "confidence": "high"
            },
            ("payment processing", "financial services", "global"): {
                "tam": 125000000000,  # $125B
                "growth_rate": 0.087,  # 8.7% CAGR
                "competitors": ["Visa", "Mastercard", "PayPal", "Stripe", "Square"],
                "sources": ["McKinsey", "PwC Global Payments Report"],
                "confidence": "high"
            },
            # Wearable Technology / Fitness Markets
            ("fitness tracker", "wearable technology", "global"): {
                "tam": 42000000000,  # $42B
                "growth_rate": 0.092,  # 9.2% CAGR
                "competitors": ["Apple", "Fitbit", "Garmin", "Xiaomi", "Samsung"],
                "sources": ["Grand View Research", "Allied Market Research"],
                "confidence": "high"
            },
            # Software Markets
            ("project management software", "software", "global"): {
                "tam": 6800000000,  # $6.8B
                "growth_rate": 0.105,  # 10.5% CAGR
                "competitors": ["Microsoft Project", "Asana", "Monday.com", "Jira", "ClickUp", "Trello"],
                "sources": ["Grand View Research", "MarketsandMarkets"],
                "confidence": "high"
            }
        }

        # Normalize inputs for matching
        product_key = product_name.lower().strip()
        industry_key = industry.lower().strip()
        geography_key = geography.lower().strip()

        # Normalize geography variations
        if geography_key in ['usa', 'us', 'america', 'united states', 'united states of america']:
            geography_key = 'united states'
        elif geography_key in ['worldwide', 'international', 'global']:
            geography_key = 'global'

        # Try exact match first
        exact_key = (product_key, industry_key, geography_key)
        if exact_key in market_segments:
            return market_segments[exact_key]

        # Try partial matches with better fuzzy matching
        for key, data in market_segments.items():
            key_product, key_industry, key_geography = key
            
            # Check if any key words from product match
            product_words = product_key.split()
            key_product_words = key_product.split()
            product_match = (
                product_key in key_product or
                key_product in product_key or
                any(word in key_product for word in product_words if len(word) > 3) or
                any(word in product_key for word in key_product_words if len(word) > 3)
            )
            
            # Check industry match (more flexible)
            industry_match = (
                industry_key == key_industry or
                industry_key in key_industry or
                key_industry in industry_key or
                (industry_key == 'wearable technology' and key_industry == 'technology') or
                (industry_key == 'technology' and 'software' in key_industry) or
                (industry_key == 'fintech' and key_industry == 'financial services')
            )
            
            # Check geography match (flexible)
            geography_match = (
                geography_key == key_geography or
                (geography_key == 'global' and key_geography in ['global', 'worldwide']) or
                (geography_key == 'united states' and key_geography == 'united states')
            )
            
            if product_match and industry_match and geography_match:
                return data

        return None

    @staticmethod
    async def analyze_market_landscape(market_input: MarketInput) -> Dict[str, Any]:
        """Comprehensive market intelligence analysis using Together AI Kimi K2 with real market research"""
        
        # Check if Together AI client is available
        if together_client is None:
            logger.warning("Together AI client not available, using fallback analysis")
            return MarketIntelligenceAgent._get_fallback_analysis(market_input)
        
        # Use Together AI Kimi K2 for dynamic market analysis
        try:
            prompt = f"""
            You are a senior market research analyst conducting a specific analysis for {market_input.product_name} in the {market_input.industry} industry.

            CRITICAL: This analysis must be UNIQUELY SPECIFIC to {market_input.product_name}. Do NOT use generic market analysis templates.

            MARKET TO ANALYZE:
            - Product/Service: {market_input.product_name}
            - Industry: {market_input.industry}
            - Geography: {market_input.geography}
            - Target Users: {market_input.target_user}
            - Market Drivers: {market_input.demand_driver}
            - Revenue Model: {market_input.transaction_type}
            - Key Metrics: {market_input.key_metrics}
            - Known Benchmarks: {market_input.benchmarks}

            CRITICAL REQUIREMENTS:
            1. Use REALISTIC market sizes - avoid $500B defaults
            2. Research REAL companies that exist in this market - MINIMUM 4 COMPETITORS ALWAYS
            3. ALWAYS include {market_input.product_name} as the primary company being analyzed in the competitive landscape
            4. Provide SPECIFIC growth rates based on actual industry data
            5. Use credible data sources and methodology
            6. Geographic segmentation must be GRANULAR - include urban/suburban, specific states, DMA codes, metro areas
            7. Strategic recommendations must be ACTIONABLE and SPECIFIC

            COMPETITIVE ANALYSIS REQUIREMENTS:
            - {market_input.product_name} MUST be included as one of the key competitors for benchmarking
            - Include at least 3-4 other major competitors in the {market_input.industry} space
            - Provide realistic market share estimates for all competitors including {market_input.product_name}
            - Compare {market_input.product_name} strengths and weaknesses against competitors

            MARKET SIZE GUIDELINES BY CATEGORY:
            - Software niches: $1B-$50B TAM
            - Consumer products: $500M-$20B TAM
            - Healthcare segments: $2B-$100B TAM
            - Technology platforms: $10B-$200B TAM

            Return accurate, research-based data for {market_input.product_name} in {market_input.geography}.

            IMPORTANT: Use proper market segmentation categories:
            
            1. GEOGRAPHICS: Must be GRANULAR - Country, State, Metro Area, Urban/Suburban, DMA, ZIP codes when relevant
            2. DEMOGRAPHICS: Age, Gender, Income, Education, Social Status, Family, Life Stage, Occupation  
            3. PSYCHOGRAPHICS: Lifestyle, AIO (Activity/Interest/Opinion), Concerns, Personality, Values, Attitudes
            4. BEHAVIORAL: Purchase, Usage, Intent, Occasion, Buyer Stage, Life Cycle Stage, Engagement

            Provide a comprehensive JSON response with the following structure:
            {{
                "market_overview": {{
                    "total_market_size": [realistic TAM in dollars],
                    "growth_rate": [realistic annual growth rate as decimal],
                    "key_drivers": [list of 3-4 real market drivers],
                    "tam_methodology": "explanation of TAM calculation",
                    "sam_calculation": "SAM as percentage of TAM with rationale",
                    "som_estimation": "SOM as realistic subset of SAM"
                }},
                "segmentation": {{
                    "by_geographics": [
                        {{
                            "name": "geographic segment name",
                            "description": "geographic description focusing on location, density, climate etc",
                            "size": [size in dollars],
                            "growth": [growth rate as decimal],
                            "key_players": ["company1", "company2"],
                            "geographic_factors": ["Country/Region", "Urban/Rural density", "Climate considerations"]
                        }}
                    ],
                    "by_demographics": [
                        {{
                            "name": "demographic segment name", 
                            "description": "demographic description focusing on age, income, education, occupation",
                            "size": [size in dollars],
                            "growth": [growth rate as decimal],
                            "key_players": ["company1", "company2"],
                            "demographic_factors": ["Age range", "Income level", "Education", "Occupation"]
                        }}
                    ],
                    "by_psychographics": [
                        {{
                            "name": "psychographic segment name",
                            "description": "psychographic description focusing on lifestyle, values, attitudes, interests",
                            "size": [size in dollars], 
                            "growth": [growth rate as decimal],
                            "key_players": ["company1", "company2"],
                            "psychographic_factors": ["Lifestyle", "Values", "Attitudes", "Interests"]
                        }}
                    ],
                    "by_behavioral": [
                        {{
                            "name": "behavioral segment name",
                            "description": "behavioral description focusing on usage, purchase patterns, buyer stage",
                            "size": [size in dollars],
                            "growth": [growth rate as decimal], 
                            "key_players": ["company1", "company2"],
                            "behavioral_factors": ["Usage patterns", "Purchase frequency", "Buyer stage", "Engagement level"]
                        }}
                    ]
                }},
                "competitors": [
                    {{
                        "name": "{market_input.product_name}",
                        "share": [market share as decimal for {market_input.product_name}],
                        "strengths": ["specific strengths of {market_input.product_name}"],
                        "weaknesses": ["specific weaknesses or challenges for {market_input.product_name}"],
                        "price_range": "actual price range for {market_input.product_name} services",
                        "price_tier": "Premium/Mid-Range/Budget",
                        "innovation_focus": "key focus areas for {market_input.product_name}",
                        "user_segment": "{market_input.target_user}"
                    }},
                    {{
                        "name": "major competitor 1 name",
                        "share": [market share as decimal],
                        "strengths": ["strength1", "strength2"],
                        "weaknesses": ["weakness1", "weakness2"],
                        "price_range": "actual price range",
                        "price_tier": "Premium/Mid-Range/Budget",
                        "innovation_focus": "focus area",
                        "user_segment": "target segment"
                    }},
                    {{
                        "name": "major competitor 2 name", 
                        "share": [market share as decimal],
                        "strengths": ["strength1", "strength2"],
                        "weaknesses": ["weakness1", "weakness2"],
                        "price_range": "actual price range",
                        "price_tier": "Premium/Mid-Range/Budget",
                        "innovation_focus": "focus area",
                        "user_segment": "target segment"
                    }},
                    {{
                        "name": "major competitor 3 name",
                        "share": [market share as decimal],
                        "strengths": ["strength1", "strength2"],
                        "weaknesses": ["weakness1", "weakness2"],
                        "price_range": "actual price range",
                        "price_tier": "Premium/Mid-Range/Budget",
                        "innovation_focus": "focus area",
                        "user_segment": "target segment"
                    }}
                ],
                "opportunities": [list of 4-5 specific opportunities],
                "threats": [list of 4-5 specific threats],
                "recommendations": [list of 4-5 actionable recommendations],
                "executive_summary": "A comprehensive 3-4 paragraph executive summary that includes: (1) Market Overview with TAM/SAM/SOM highlights, (2) Competitive Landscape key insights, (3) Strategic Opportunities and Recommendations, (4) Key Takeaways and Action Items. Make this client-ready and professional.",
                "data_sources": [
                    {{"name": "Gartner Market Research", "url": "https://www.gartner.com/en/research"}},
                    {{"name": "McKinsey Industry Reports", "url": "https://www.mckinsey.com/industries"}},
                    {{"name": "IBISWorld Market Analysis", "url": "https://www.ibisworld.com"}},
                    {{"name": "Forrester Research", "url": "https://www.forrester.com/research"}},
                    {{"name": "PwC Industry Insights", "url": "https://www.pwc.com/us/en/industries.html"}}
                ],
                "confidence_level": "high/medium/low",
                "methodology": "description of analysis methodology"
            }}

            CRITICAL: The executive_summary MUST be a well-written, comprehensive 3-4 paragraph summary suitable for C-level executives. Include specific numbers, insights, and actionable recommendations.

            Return only valid JSON with accurate, researched market intelligence.
            """

            # Call Together AI API with Kimi K2 Instruct 0905
            response = await asyncio.to_thread(
                together_client.chat.completions.create,
                model="moonshotai/Kimi-K2-Instruct-0905",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a market research expert. Return ONLY valid JSON with no markdown formatting or additional text."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=8000
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Together AI (Kimi K2) response length: {len(content)} characters")
            
            # Parse JSON response with better error handling
            try:
                # Clean up any markdown formatting
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                if content.startswith("```"):
                    content = content[3:]
                
                content = content.strip()
                ai_analysis = json.loads(content)
                logger.info("Successfully parsed AI analysis for %s", market_input.product_name)
                
                return ai_analysis
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"JSON parsing error for {market_input.product_name}: {e}")
                logger.error("Raw content: %s", content[:500])
                # Fall through to fallback analysis
                logger.info(f"Falling back to curated data for {market_input.product_name}")
                return MarketIntelligenceAgent._get_fallback_analysis(market_input)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return MarketIntelligenceAgent._get_fallback_analysis(market_input)
                
        except Exception as e:
            logger.error(f"Error with Together AI (Kimi) analysis: {e}")
            return MarketIntelligenceAgent._get_fallback_analysis(market_input)

    @staticmethod
    def _get_fallback_analysis(market_input: MarketInput) -> Dict[str, Any]:
        """Minimal fallback analysis when OpenAI fails - no curated database"""
        logger.warning(f"Using minimal fallback analysis for {market_input.product_name}")
        
        # Generate basic market analysis without curated data
        tam = 1000000000  # $1B default TAM
        sam = int(tam * 0.3)  # 30% SAM
        som = int(sam * 0.1)  # 10% SOM
        
        # Generic competitors based on industry
        competitors = [
            {
                "name": "Market Leader",
                "share": 0.25,
                "strengths": ["Market dominance", "Brand recognition"],
                "weaknesses": ["High pricing", "Legacy systems"],
                "price_range": "$200-$500",
                "price_tier": "Premium",
                "innovation_focus": "Market expansion",
                "user_segment": market_input.target_user
            },
            {
                "name": "Technology Innovator",
                "share": 0.20,
                "strengths": ["Innovation", "Technology leadership"],
                "weaknesses": ["Limited market reach", "Resource constraints"],
                "price_range": "$150-$400",
                "price_tier": "Mid-Range",
                "innovation_focus": "Technology advancement",
                "user_segment": market_input.target_user
            },
            {
                "name": "Growth Challenger",
                "share": 0.15,
                "strengths": ["Rapid growth", "Customer focus"],
                "weaknesses": ["Scale limitations", "Brand awareness"],
                "price_range": "$100-$300",
                "price_tier": "Mid-Range",
                "innovation_focus": "Customer experience",
                "user_segment": market_input.target_user
            },
            {
                "name": "Value Player",
                "share": 0.10,
                "strengths": ["Cost efficiency", "Accessibility"],
                "weaknesses": ["Limited features", "Low margins"],
                "price_range": "$50-$200",
                "price_tier": "Budget",
                "innovation_focus": "Cost optimization",
                "user_segment": market_input.target_user
            }
        ]

        return {
            "market_overview": {
                "total_market_size": tam,
                "growth_rate": 0.08,
                "key_drivers": [
                    market_input.demand_driver,
                    "Technology adoption",
                    "Market expansion",
                    "Consumer demand growth"
                ],
                "tam_methodology": "Basic market estimation",
                "sam_calculation": f"30% of TAM: ${sam:,}",
                "som_estimation": f"10% of SAM: ${som:,}"
            },
            "segmentation": {
                "by_geographics": [
                    {
                        "name": "Major Metro Areas",
                        "description": "Urban markets with high population density",
                        "size": int(sam * 0.4),
                        "growth": 0.07,
                        "key_players": ["Market Leader", "Technology Innovator"]
                    },
                    {
                        "name": "Suburban Markets",
                        "description": "Suburban areas with growing populations",
                        "size": int(sam * 0.35),
                        "growth": 0.09,
                        "key_players": ["Growth Challenger", "Value Player"]
                    },
                    {
                        "name": "Secondary Cities",
                        "description": "Mid-size cities and rural areas",
                        "size": int(sam * 0.25),
                        "growth": 0.11,
                        "key_players": ["Value Player", "Market Leader"]
                    }
                ],
                "by_demographics": [
                    {
                        "name": "Young Adults",
                        "description": "Tech-savvy professionals 25-35",
                        "size": int(sam * 0.4),
                        "growth": 0.10,
                        "key_players": ["Technology Innovator", "Growth Challenger"]
                    },
                    {
                        "name": "Middle-aged",
                        "description": "Established professionals 36-50",
                        "size": int(sam * 0.4),
                        "growth": 0.06,
                        "key_players": ["Market Leader", "Technology Innovator"]
                    },
                    {
                        "name": "Seniors",
                        "description": "Mature consumers 51+",
                        "size": int(sam * 0.2),
                        "growth": 0.08,
                        "key_players": ["Market Leader", "Value Player"]
                    }
                ],
                "by_psychographics": [
                    {
                        "name": "Innovation Adopters",
                        "description": "Early adopters of new technology",
                        "size": int(sam * 0.4),
                        "growth": 0.12,
                        "key_players": ["Technology Innovator", "Growth Challenger"]
                    },
                    {
                        "name": "Quality Focused",
                        "description": "Premium quality seekers",
                        "size": int(sam * 0.4),
                        "growth": 0.09,
                        "key_players": ["Market Leader", "Technology Innovator"]
                    },
                    {
                        "name": "Budget Conscious",
                        "description": "Value-oriented consumers",
                        "size": int(sam * 0.2),
                        "growth": 0.05,
                        "key_players": ["Value Player", "Growth Challenger"]
                    }
                ],
                "by_behavioral": [
                    {
                        "name": "Regular Users",
                        "description": "Daily active users",
                        "size": int(sam * 0.4),
                        "growth": 0.08,
                        "key_players": ["Market Leader", "Technology Innovator"]
                    },
                    {
                        "name": "Occasional Users",
                        "description": "Periodic usage patterns",
                        "size": int(sam * 0.4),
                        "growth": 0.06,
                        "key_players": ["Growth Challenger", "Value Player"]
                    },
                    {
                        "name": "New Users",
                        "description": "First-time market entrants",
                        "size": int(sam * 0.2),
                        "growth": 0.15,
                        "key_players": ["Growth Challenger", "Technology Innovator"]
                    }
                ]
            },
            "competitors": competitors,
            "opportunities": [
                f"{market_input.demand_driver} driving market growth",
                f"Underserved segments in {market_input.geography}",
                f"Technology integration opportunities",
                f"Partnership potential in {market_input.industry}"
            ],
            "threats": [
                f"Intense competition in {market_input.industry}",
                f"Market saturation risks",
                f"Regulatory challenges",
                f"Economic uncertainty"
            ],
            "recommendations": [
                f"Focus on {market_input.target_user} segment differentiation",
                f"Leverage {market_input.demand_driver} trends for growth",
                f"Build strategic partnerships in {market_input.industry}",
                f"Invest in {market_input.key_metrics} capabilities"
            ],
            "data_sources": ["Basic market estimation"],
            "confidence_level": "low",
            "methodology": "Minimal fallback analysis"
        }

class VisualMapGenerator:
    @staticmethod
    def generate_visual_market_map(market_data: Dict[str, Any], product_name: str) -> Dict[str, Any]:
        """Generate professional visual market map with segments and styling"""
        # Extract segmentation data
        geographic_segments = market_data.get("segmentation", {}).get("by_geographics", [])
        demographic_segments = market_data.get("segmentation", {}).get("by_demographics", [])
        psychographic_segments = market_data.get("segmentation", {}).get("by_psychographics", [])
        behavioral_segments = market_data.get("segmentation", {}).get("by_behavioral", [])

        # Create visual market map structure
        visual_map = {
            "title": f"{product_name} Market Segmentation",
            "geographic_segments": [],
            "demographic_segments": [],
            "psychographic_segments": [],
            "behavioral_segments": [],
            "market_overview": market_data.get("market_overview", {})
        }

        # Process geographic segments
        for i, segment in enumerate(geographic_segments):
            icon = "🌍" if i == 0 else "🏙️" if i == 1 else "🌆" if i == 2 else "🏞️"
            color = "blue" if i == 0 else "green" if i == 1 else "teal" if i == 2 else "indigo"
            
            visual_map["geographic_segments"].append({
                "name": segment.get("name", f"Geographic Segment {i+1}"),
                "description": segment.get("description", "Geographic market segment"),
                "size": segment.get("size", 1000000000),
                "growth": segment.get("growth", 0.05),
                "icon": icon,
                "color": color,
                "key_players": segment.get("key_players", [])
            })

        # Process demographic segments
        for i, segment in enumerate(demographic_segments):
            icon = "👥" if i == 0 else "👨‍💼" if i == 1 else "👩‍🎓" if i == 2 else "👨‍👩‍👧‍👦"
            color = "orange" if i == 0 else "red" if i == 1 else "purple" if i == 2 else "pink"
            
            visual_map["demographic_segments"].append({
                "name": segment.get("name", f"Demographic Segment {i+1}"),
                "description": segment.get("description", "Demographic market segment"),
                "size": segment.get("size", 500000000),
                "growth": segment.get("growth", 0.06),
                "icon": icon,
                "color": color,
                "key_players": segment.get("key_players", [])
            })

        # Process psychographic segments
        for i, segment in enumerate(psychographic_segments):
            icon = "🧠" if i == 0 else "💭" if i == 1 else "🎯" if i == 2 else "💡"
            color = "yellow" if i == 0 else "amber" if i == 1 else "lime" if i == 2 else "emerald"
            
            visual_map["psychographic_segments"].append({
                "name": segment.get("name", f"Psychographic Segment {i+1}"),
                "description": segment.get("description", "Psychographic market segment"),
                "size": segment.get("size", 800000000),
                "growth": segment.get("growth", 0.07),
                "icon": icon,
                "color": color,
                "key_players": segment.get("key_players", [])
            })

        # Process behavioral segments
        for i, segment in enumerate(behavioral_segments):
            icon = "🛒" if i == 0 else "🔄" if i == 1 else "📈" if i == 2 else "⚡"
            color = "violet" if i == 0 else "cyan" if i == 1 else "rose" if i == 2 else "slate"
            
            visual_map["behavioral_segments"].append({
                "name": segment.get("name", f"Behavioral Segment {i+1}"),
                "description": segment.get("description", "Behavioral market segment"),
                "size": segment.get("size", 600000000),
                "growth": segment.get("growth", 0.08),
                "icon": icon,
                "color": color,
                "key_players": segment.get("key_players", [])
            })

        return visual_map

class ComprehensiveAnalysisEngine:
    @staticmethod
    async def generate_market_map(market_input: MarketInput, ai_analysis: Dict[str, Any]) -> MarketMap:
        """Generate comprehensive market map from AI analysis"""
        try:
            market_overview = ai_analysis.get("market_overview", {})
            segmentation = ai_analysis.get("segmentation", {})
            competitors = ai_analysis.get("competitors", [])
            opportunities = ai_analysis.get("opportunities", [])
            threats = ai_analysis.get("threats", [])
            recommendations = ai_analysis.get("recommendations", [])

            # Convert to structured format
            functional_segments = []
            for seg in segmentation.get("by_function", []):
                functional_segments.append(MarketSegment(
                    name=seg.get("name", "Segment"),
                    description=seg.get("description", "Market segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Player 1", "Player 2"])
                ))

            user_segments = []
            for seg in segmentation.get("by_user", []):
                user_segments.append(MarketSegment(
                    name=seg.get("name", "User Segment"),
                    description=seg.get("description", "User segment"),
                    size_estimate=float(seg.get("size", 500000000)),
                    growth_rate=float(seg.get("growth", 0.06)),
                    key_players=seg.get("key_players", ["Company A", "Company B"])
                ))

            price_segments = []
            for seg in segmentation.get("by_price", []):
                price_segments.append(MarketSegment(
                    name=seg.get("name", "Price Tier"),
                    description=seg.get("description", "Price segment"),
                    size_estimate=float(seg.get("size", 800000000)),
                    growth_rate=float(seg.get("growth", 0.07)),
                    key_players=seg.get("key_players", ["Brand X", "Brand Y"])
                ))

            competitor_objects = []
            for comp in competitors:
                competitor_objects.append(Competitor(
                    name=comp.get("name", "Competitor"),
                    strengths=comp.get("strengths", ["Strength 1", "Strength 2"]),
                    weaknesses=comp.get("weaknesses", ["Weakness 1", "Weakness 2"]),
                    market_share=comp.get("share", 0.1),
                    price_range=comp.get("price_range", "$100-$250")
                ))

            # Initialize empty segment lists if not present in segmentation
            geographic_segments = []
            demographic_segments = []
            psychographic_segments = []
            behavioral_segments = []
            
            # Convert segments if they exist in the segmentation data
            for seg in segmentation.get("by_geographics", []):
                geographic_segments.append(MarketSegment(
                    name=seg.get("name", "Geographic Segment"),
                    description=seg.get("description", "Geographic segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Company A", "Company B"])
                ))
            
            for seg in segmentation.get("by_demographics", []):
                demographic_segments.append(MarketSegment(
                    name=seg.get("name", "Demographic Segment"),
                    description=seg.get("description", "Demographic segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Company A", "Company B"])
                ))
            
            for seg in segmentation.get("by_psychographics", []):
                psychographic_segments.append(MarketSegment(
                    name=seg.get("name", "Psychographic Segment"),
                    description=seg.get("description", "Psychographic segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Company A", "Company B"])
                ))
            
            for seg in segmentation.get("by_behavioral", []):
                behavioral_segments.append(MarketSegment(
                    name=seg.get("name", "Behavioral Segment"),
                    description=seg.get("description", "Behavioral segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Company A", "Company B"])
                ))

            return MarketMap(
                id=str(uuid.uuid4()),
                market_input_id=market_input.id,
                total_market_size=float(market_overview.get("total_market_size", 5000000000)),
                market_growth_rate=float(market_overview.get("growth_rate", 0.08)),
                key_drivers=market_overview.get("key_drivers", ["Digital transformation", "Consumer demand"]),
                segmentation_by_geographics=geographic_segments,
                segmentation_by_demographics=demographic_segments,
                segmentation_by_psychographics=psychographic_segments,
                segmentation_by_behavioral=behavioral_segments,
                competitors=competitor_objects,
                opportunities=opportunities,
                threats=threats,
                strategic_recommendations=recommendations,
                data_sources=[
                    source.get("name", str(source)) if isinstance(source, dict) else str(source)
                    for source in ai_analysis.get("data_sources", ["Industry reports", "Market research", "Public data"])
                ],
                confidence_level=ai_analysis.get("confidence_level", "medium"),
                methodology=ai_analysis.get("methodology", "AI-powered analysis with market research"),
                executive_summary=ai_analysis.get("executive_summary", "Executive summary not available"),
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error generating market map: {e}")
            # Return basic fallback market map
            return MarketMap(
                id=str(uuid.uuid4()),
                market_input_id=market_input.id,
                total_market_size=5000000000,
                market_growth_rate=0.08,
                key_drivers=["Market growth", "Technology adoption"],
                segmentation_by_geographics=[],
                segmentation_by_demographics=[],
                segmentation_by_psychographics=[],
                segmentation_by_behavioral=[],
                competitors=[],
                opportunities=["Market opportunity 1", "Market opportunity 2"],
                threats=["Market threat 1", "Market threat 2"],
                strategic_recommendations=["Focus on differentiation", "Build partnerships"],
                executive_summary=f"""
                **MARKET OPPORTUNITY OVERVIEW**
                The {market_input.product_name} market represents a significant opportunity driven by {market_input.demand_driver}. With a total addressable market of $5B and steady growth trajectory, this sector presents compelling investment potential for organizations targeting {market_input.target_user}.

                **COMPETITIVE LANDSCAPE**
                The market features established players alongside emerging competitors, creating opportunities for differentiation through {market_input.key_metrics} optimization and strategic positioning in underserved segments.

                **MARKET SEGMENTATION INSIGHTS**
                Geographic and demographic segmentation reveals distinct opportunities across various market segments, with particular strength in areas experiencing rapid adoption of {market_input.transaction_type} models.

                **STRATEGIC RECOMMENDATIONS**
                Key priorities include focused market entry in high-growth segments, strategic partnerships with established players, and investment in capabilities that leverage {market_input.demand_driver} trends to capture market share.
                """.strip(),
                data_sources=["Market research", "Industry analysis"],
                confidence_level="medium",
                methodology="AI analysis",
                timestamp=datetime.utcnow()
            )

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Market Map API Ready", "version": "2.0.0"}

@api_router.post("/analyze-market", response_model=MarketAnalysis)
async def analyze_market(market_input: MarketInput):
    try:
        # Step 1: Comprehensive AI Market Intelligence
        ai_analysis = await MarketIntelligenceAgent.analyze_market_landscape(market_input)

        # Step 2: Generate Market Map
        market_map = await ComprehensiveAnalysisEngine.generate_market_map(market_input, ai_analysis)

        # Step 3: Generate Visual Map
        visual_map = VisualMapGenerator.generate_visual_market_map(ai_analysis, market_input.product_name)

        # Save to database
        await db.market_inputs.insert_one(market_input.dict())
        await db.market_maps.insert_one(market_map.dict())

        # Generate analysis
        analysis = MarketAnalysis(
            market_input=market_input,
            market_map=market_map,
            visual_map=visual_map
        )

        return analysis

    except Exception as e:
        logging.error(f"Error in analyze_market: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/export-market-map/{analysis_id}")
async def export_market_map(analysis_id: str):
    try:
        # Get analysis from database
        market_map = await db.market_maps.find_one({"id": analysis_id})
        if not market_map:
            raise HTTPException(status_code=404, detail="Market map not found")

        market_input = await db.market_inputs.find_one({"id": market_map["market_input_id"]})
        if not market_input:
            raise HTTPException(status_code=404, detail="Market input not found")

        # Create comprehensive Excel report
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Market Overview Sheet
            overview_data = {
                "Metric": ["Total Market Size", "Growth Rate", "Geography", "Analysis Date"],
                "Value": [
                    f"${market_map['total_market_size']/1000000000:.1f}B",
                    f"{market_map['market_growth_rate']*100:.1f}%",
                    market_input["geography"],
                    str(market_map["timestamp"])  # Convert datetime to string
                ]
            }
            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='Market Overview', index=False)

            # Competitive Analysis Sheet
            if market_map["competitors"]:
                comp_data = []
                for comp in market_map["competitors"]:
                    comp_data.append({
                        "Competitor": comp["name"],
                        "Market Share": f"{comp.get('market_share', 0)*100:.1f}%" if comp.get('market_share') else "N/A",
                        "Strengths": "; ".join(comp["strengths"]),
                        "Weaknesses": "; ".join(comp["weaknesses"]),
                        "Price Range": comp.get("price_range", "N/A")
                    })
                comp_df = pd.DataFrame(comp_data)
                comp_df.to_excel(writer, sheet_name='Competitive Analysis', index=False)

        # Save the workbook and get the bytes
        output.seek(0)
        excel_data = output.getvalue()

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=Market_Map_{analysis_id[:8]}.xlsx",
                "Content-Length": str(len(excel_data))
            }
        )

    except Exception as e:
        logging.error(f"Error in export_market_map: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/export-pdf/{analysis_id}")
async def export_pdf(analysis_id: str):
    """Export market analysis as professional PDF with BCM branding"""
    try:
        # Get analysis from database
        market_map = await db.market_maps.find_one({"id": analysis_id})
        if not market_map:
            raise HTTPException(status_code=404, detail="Market map not found")

        market_input = await db.market_inputs.find_one({"id": market_map["market_input_id"]})
        if not market_input:
            raise HTTPException(status_code=404, detail="Market input not found")

        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#FF6B35'),  # BCM Orange
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#FF6B35'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=14
        )

        # Header with BCM Logo placeholder and title
        story.append(Paragraph("BCM", title_style))
        story.append(Paragraph("Market Intelligence Report", ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceAfter=20
        )))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Product Title
        story.append(Paragraph(f"<b>{market_input['product_name']}</b>", title_style))
        story.append(Paragraph(f"{market_input['industry']} • {market_input['geography']}", 
                              ParagraphStyle('ProductSubtitle', parent=body_style, alignment=TA_CENTER, fontSize=11)))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        exec_summary = market_map.get('executive_summary', 'Executive summary not available')
        for para in exec_summary.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Market Overview
        story.append(Paragraph("Market Overview", heading_style))
        
        market_data = [
            ['Metric', 'Value'],
            ['Total Addressable Market (TAM)', f"${market_map['total_market_size']/1000000000:.2f}B"],
            ['Market Growth Rate', f"{market_map['market_growth_rate']*100:.1f}% annually"],
            ['Confidence Level', market_map.get('confidence_level', 'medium').upper()],
            ['Analysis Date', str(market_map['timestamp'])[:10]]
        ]
        
        market_table = Table(market_data, colWidths=[3*inch, 3*inch])
        market_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(market_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Key Market Drivers
        story.append(Paragraph("Key Market Drivers", subheading_style))
        for i, driver in enumerate(market_map.get('key_drivers', [])[:5], 1):
            story.append(Paragraph(f"{i}. {driver}", body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Page Break
        story.append(PageBreak())
        
        # Market Segmentation
        story.append(Paragraph("Market Segmentation Analysis", heading_style))
        story.append(Paragraph("Comprehensive breakdown of market segments across multiple dimensions", body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Geographic Segmentation
        story.append(Paragraph("Geographic Segmentation", subheading_style))
        geo_data = [['Segment', 'Size', 'Growth', 'Description']]
        for seg in market_map.get('segmentation_by_geographics', [])[:3]:
            geo_data.append([
                seg['name'],
                f"${seg['size_estimate']/1000000:.0f}M",
                f"{seg['growth_rate']*100:.1f}%",
                seg['description'][:60] + '...' if len(seg['description']) > 60 else seg['description']
            ])
        
        if len(geo_data) > 1:
            geo_table = Table(geo_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 3.2*inch])
            geo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(geo_table)
            story.append(Spacer(1, 0.15*inch))
        
        # Demographic Segmentation
        story.append(Paragraph("Demographic Segmentation", subheading_style))
        demo_data = [['Segment', 'Size', 'Growth', 'Description']]
        for seg in market_map.get('segmentation_by_demographics', [])[:3]:
            demo_data.append([
                seg['name'],
                f"${seg['size_estimate']/1000000:.0f}M",
                f"{seg['growth_rate']*100:.1f}%",
                seg['description'][:60] + '...' if len(seg['description']) > 60 else seg['description']
            ])
        
        if len(demo_data) > 1:
            demo_table = Table(demo_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 3.2*inch])
            demo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(demo_table)
            story.append(Spacer(1, 0.15*inch))
        
        # Psychographic Segmentation
        story.append(Paragraph("Psychographic Segmentation", subheading_style))
        psycho_data = [['Segment', 'Size', 'Growth', 'Description']]
        for seg in market_map.get('segmentation_by_psychographics', [])[:3]:
            psycho_data.append([
                seg['name'],
                f"${seg['size_estimate']/1000000:.0f}M",
                f"{seg['growth_rate']*100:.1f}%",
                seg['description'][:60] + '...' if len(seg['description']) > 60 else seg['description']
            ])
        
        if len(psycho_data) > 1:
            psycho_table = Table(psycho_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 3.2*inch])
            psycho_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(psycho_table)
            story.append(Spacer(1, 0.15*inch))
        
        # Behavioral Segmentation
        story.append(Paragraph("Behavioral Segmentation", subheading_style))
        behav_data = [['Segment', 'Size', 'Growth', 'Description']]
        for seg in market_map.get('segmentation_by_behavioral', [])[:3]:
            behav_data.append([
                seg['name'],
                f"${seg['size_estimate']/1000000:.0f}M",
                f"{seg['growth_rate']*100:.1f}%",
                seg['description'][:60] + '...' if len(seg['description']) > 60 else seg['description']
            ])
        
        if len(behav_data) > 1:
            behav_table = Table(behav_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 3.2*inch])
            behav_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(behav_table)
        
        # Page Break
        story.append(PageBreak())
        
        # Competitive Analysis
        story.append(Paragraph("Competitive Analysis", heading_style))
        story.append(Paragraph("Key competitors and their market positioning", body_style))
        story.append(Spacer(1, 0.15*inch))
        
        comp_data = [['Competitor', 'Market Share', 'Price Tier', 'Key Strengths']]
        for comp in market_map.get('competitors', [])[:5]:
            comp_data.append([
                comp['name'],
                f"{comp.get('market_share', 0)*100:.1f}%" if comp.get('market_share') else 'N/A',
                comp.get('price_tier', 'N/A'),
                ', '.join(comp.get('strengths', [])[:2])
            ])
        
        if len(comp_data) > 1:
            comp_table = Table(comp_data, colWidths=[2*inch, 1*inch, 1*inch, 2.5*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.linen),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(comp_table)
        
        story.append(Spacer(1, 0.2*inch))
        
        # Strategic Recommendations
        story.append(Paragraph("Strategic Recommendations", heading_style))
        story.append(Paragraph("Actionable insights for market entry and growth", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        for i, rec in enumerate(market_map.get('strategic_recommendations', [])[:5], 1):
            story.append(Paragraph(f"<b>{i}.</b> {rec}", body_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Opportunities & Threats
        story.append(Paragraph("Market Opportunities", subheading_style))
        for i, opp in enumerate(market_map.get('opportunities', [])[:4], 1):
            story.append(Paragraph(f"• {opp}", body_style))
        
        story.append(Spacer(1, 0.15*inch))
        
        story.append(Paragraph("Market Threats", subheading_style))
        for i, threat in enumerate(market_map.get('threats', [])[:4], 1):
            story.append(Paragraph(f"• {threat}", body_style))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("_" * 80, body_style))
        story.append(Paragraph(
            f"<i>Report generated by BCM Market Intelligence Platform • Powered by Kimi K2 • {str(market_map['timestamp'])[:10]}</i>",
            ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        
        # Return PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=BCM_Market_Report_{market_input['product_name'].replace(' ', '_')}.pdf"
            }
        )
        
    except Exception as e:
        logging.error(f"Error in export_pdf: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    try:
        # Get market map from database
        market_map = await db.market_maps.find_one({"id": analysis_id})
        if not market_map:
            raise HTTPException(status_code=404, detail="Analysis not found")

        market_input = await db.market_inputs.find_one({"id": market_map["market_input_id"]})
        if not market_input:
            raise HTTPException(status_code=404, detail="Market input not found")

        # Recreate analysis object
        analysis = MarketAnalysis(
            market_input=MarketInput(**market_input),
            market_map=MarketMap(**market_map)
        )

        # Generate visual map using the existing segmentation data
        visual_map = VisualMapGenerator.generate_visual_market_map({
            "segmentation": {
                "by_geographics": market_map["segmentation_by_geographics"],
                "by_demographics": market_map["segmentation_by_demographics"],
                "by_psychographics": market_map["segmentation_by_psychographics"],
                "by_behavioral": market_map["segmentation_by_behavioral"]
            }
        }, market_input["product_name"])

        analysis.visual_map = visual_map

        return analysis

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error in get_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analysis-history")
async def get_analysis_history():
    try:
        # Get recent analyses
        results = await db.market_maps.find().sort("timestamp", -1).limit(10).to_list(10)
        
        history = []
        for result in results:
            market_input = await db.market_inputs.find_one({"id": result["market_input_id"]})
            if market_input:
                history.append({
                    "id": result["id"],
                    "product_name": market_input["product_name"],
                    "geography": market_input["geography"],
                    "market_size": result["total_market_size"],
                    "confidence_level": result["confidence_level"],
                    "timestamp": result["timestamp"]
                })

        return {"history": history}

    except Exception as e:
        logging.error(f"Error in get_analysis_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/test-integrations")
async def test_integrations():
    """Test endpoint to verify all integrations are working"""
    try:
        # Test Together AI (Kimi)
        together_status = "Failed"
        try:
            if together_client is not None:
                # Test with a simple API call
                together_test = await asyncio.to_thread(
                    together_client.chat.completions.create,
                    model="moonshotai/Kimi-K2-Instruct-0905",
                    messages=[{"role": "user", "content": "Say 'OK'"}],
                    max_tokens=5
                )
                if together_test.choices[0].message.content:
                    together_status = "OK"
                else:
                    together_status = "Failed - No response"
            else:
                together_status = "Failed - Client not initialized"
        except Exception as e:
            logger.error(f"Error testing Together AI: {e}")
            together_status = f"Failed - {str(e)}"

        # Test MongoDB
        try:
            await db.test_collection.insert_one({"test": "data"})
            await db.test_collection.delete_one({"test": "data"})
            mongo_status = "OK"
        except Exception as e:
            logger.error(f"MongoDB test failed: {e}")
            mongo_status = "Failed"

        return {
            "integrations": {
                "together_ai": together_status,
                "kimi_model": "moonshotai/Kimi-K2-Instruct-0905",
                "mongodb": mongo_status
            },
            "api_version": "2.0.0",
            "features": ["Market Maps", "Competitive Analysis", "Strategic Insights", "Powered by Kimi K2"]
        }

    except Exception as e:
        logger.error(f"Error in test_integrations: {e}")
        return {
            "integrations": {
                "openai": "Failed",
                "mongodb": "Failed"
            },
            "error": str(e)
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    mongo_client.close()
