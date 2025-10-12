from fastapi import FastAPI, APIRouter, HTTPException, Depends
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
import re
from fastapi.responses import StreamingResponse, Response
import asyncio
import sys
from pdf_generator import create_market_report_pdf
from auth_routes import auth_router, require_auth, get_db
from auth_models import User

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import SpyFu service after environment is loaded
from spyfu_service import spyfu_service, extract_domain_from_company, PPCIntelligenceReport

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

# Make database accessible to auth routes
app.state.db = db

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

# Simplified Resonate-focused persona data models
class ResonateBaseDemographics(BaseModel):
    age_range: Optional[str] = None  # e.g., "25-34", "35-44"
    gender: Optional[str] = None     # e.g., "Male", "Female", "Mixed"
    household_income: Optional[str] = None  # e.g., "$50K-$75K", "$75K-$100K"
    education: Optional[str] = None  # e.g., "College Graduate", "High School"
    employment: Optional[str] = None # e.g., "Professional", "Management", "Service"

class ResonateGeographics(BaseModel):
    region: Optional[str] = None     # e.g., "Northeast", "West Coast"
    market_size: Optional[str] = None # e.g., "Major Metro", "Small City"
    geography_type: Optional[str] = None # e.g., "Urban", "Suburban", "Rural"

class ResonateMediaUsage(BaseModel):
    primary_media: List[str] = []    # e.g., ["Social Media", "TV", "Digital"]
    digital_engagement: Optional[str] = None # e.g., "High", "Medium", "Low"
    content_preferences: List[str] = [] # e.g., ["Video", "Articles", "Podcasts"]

class ResonateSegmentMapping(BaseModel):
    # Core Resonate taxonomy categories this segment maps to
    demographics: Optional[ResonateBaseDemographics] = None
    geographics: Optional[ResonateGeographics] = None  
    media_usage: Optional[ResonateMediaUsage] = None
    # Direct taxonomy paths for easy Resonate entry
    resonate_taxonomy_paths: List[str] = []
    # Confidence level for mapping accuracy
    mapping_confidence: Optional[str] = None

class MarketSegment(BaseModel):
    name: str
    description: str
    size_estimate: float
    growth_rate: float
    key_players: List[str]
    # Resonate-ready segment mapping
    resonate_mapping: Optional[ResonateSegmentMapping] = None

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
    # Analysis Perspective
    analysis_perspective: str  # "existing_brand" or "new_entrant"
    brand_position: Optional[str] = None  # Current position if existing brand
    # Market Segmentation
    segmentation_by_geographics: List[MarketSegment]
    segmentation_by_demographics: List[MarketSegment]
    segmentation_by_psychographics: List[MarketSegment]
    segmentation_by_behavioral: List[MarketSegment]
    segmentation_by_firmographics: List[MarketSegment]  # NEW: B2B segmentation
    # Competitive Analysis
    competitors: List[Competitor]
    # Strategic Analysis
    opportunities: List[str]
    threats: List[str]
    strategic_recommendations: List[str]
    # Marketing-Specific Analysis
    marketing_opportunities: Optional[List[str]] = []
    marketing_threats: Optional[List[str]] = []
    marketing_recommendations: Optional[List[str]] = []
    competitive_digital_assessment: Optional[Dict[str, Any]] = {}
    # PPC Competitive Intelligence
    ppc_intelligence: Optional[Dict[str, Any]] = {}
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
            # Event Equipment Rental Markets
            ("event equipment rental", "event services", "united states"): {
                "tam": 18500000000,  # $18.5B
                "growth_rate": 0.058,  # 5.8% CAGR
                "competitors": ["United Rentals", "Home Depot Tool Rental", "Party City", "Abbey Party Rents", "Classic Party Rentals", "Tent Rental Plus"],
                "sources": ["IBISWorld", "American Rental Association", "Event Rental Systems"],
                "confidence": "high"
            },
            ("event planning", "event services", "united states"): {
                "tam": 5200000000,  # $5.2B
                "growth_rate": 0.087,  # 8.7% CAGR
                "competitors": ["Eventbrite", "Cvent", "Meeting Professionals International", "International Live Events Association"],
                "sources": ["IBISWorld", "Grand View Research"],
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
        
        # Determine analysis perspective based on product name
        has_specific_brand = bool(market_input.product_name and 
                                 market_input.product_name.strip() and 
                                 market_input.product_name.lower() not in ['new product', 'new service', 'startup', 'new company'])
        analysis_perspective = "existing_brand" if has_specific_brand else "new_entrant"
        
        # Determine if this is B2B for firmographic analysis
        is_b2b = any(term in market_input.industry.lower() for term in ['b2b', 'business', 'enterprise', 'saas', 'software', 'financial services', 'consulting', 'professional services'])
        
        # Prepare brand position JSON
        brand_position_json = ""
        if analysis_perspective == "existing_brand":
            brand_position_json = f'"brand_position": "Current market position and competitive standing of {market_input.product_name}",'
        
        # Use Together AI Kimi K2 for dynamic market analysis
        try:
            perspective_instruction = ""
            if analysis_perspective == "existing_brand":
                perspective_instruction = f"""
            ANALYSIS PERSPECTIVE: EXISTING BRAND ANALYSIS
            This analysis is from the perspective of {market_input.product_name} as an existing player in the market.
            - Focus on {market_input.product_name}'s current market position, competitive advantages, and growth opportunities
            - Include {market_input.product_name} prominently in competitive analysis with current market position
            - Provide strategic recommendations for {market_input.product_name}'s market expansion or defense
            - Analyze how {market_input.product_name} can leverage its existing strengths against competitors
            """
            else:
                perspective_instruction = f"""
            ANALYSIS PERSPECTIVE: NEW ENTRANT ANALYSIS  
            This analysis is from the perspective of a NEW ENTRANT entering the {market_input.industry} market.
            - Focus on market entry opportunities and barriers for a new player
            - Analyze competitive landscape from an outsider's perspective looking to disrupt
            - Provide strategic recommendations for market entry and differentiation
            - Identify gaps in the current market that a new entrant could exploit
            """
            
            firmographic_instruction = ""
            firmographic_json = ""
            if is_b2b:
                firmographic_instruction = """
            5. FIRMOGRAPHICS (B2B ONLY): Industry vertical, Company size (employees/revenue), Geographic location (city-level), Job titles/roles, Company revenue estimates
            """
                firmographic_json = """,
                    "by_firmographics": [
                        {
                            "name": "firmographic segment name",
                            "description": "B2B segment description focusing on company characteristics and business attributes",
                            "size": [size in dollars],
                            "growth": [growth rate as decimal],
                            "key_players": ["company1", "company2"],
                            "firmographic_factors": ["Industry vertical", "Company size", "Geographic location", "Job titles/roles", "Company revenue"]
                        }
                    ]"""
            
            prompt = f"""
            You are a senior market research analyst conducting a specific analysis for {market_input.product_name} in the {market_input.industry} industry.

            CRITICAL: This analysis must be UNIQUELY SPECIFIC to {market_input.product_name}. Do NOT use generic market analysis templates.

            {perspective_instruction}

            MARKET TO ANALYZE:
            - Product/Service: {market_input.product_name}
            - Industry: {market_input.industry}
            - Geography: {market_input.geography}
            - Target Users: {market_input.target_user}
            - Market Drivers: {market_input.demand_driver}
            - Revenue Model: {market_input.transaction_type}
            - Key Metrics: {market_input.key_metrics}
            - Known Benchmarks: {market_input.benchmarks}

            MARKETING & ADVERTISING FOCUS:
            This analysis is from a MARKETING CONSULTANT perspective, focusing on growth through marketing and advertising strategies rather than operational improvements.
            
            CRITICAL REQUIREMENTS:
            1. Use REALISTIC market sizes - avoid $500B defaults
            2. Research REAL companies that exist in this market - MINIMUM 4 COMPETITORS ALWAYS
            3. ALWAYS include {market_input.product_name} as the primary company being analyzed in the competitive landscape
            4. Focus on MARKETING and ADVERTISING growth strategies, not operational efficiencies
            5. Analyze digital marketing approaches, advertising spend, channel strategies, and brand positioning
            6. Geographic segmentation must consider MARKETING REACH - include media markets, DMA codes, digital penetration
            7. Strategic recommendations must be MARKETING-ACTIONABLE (campaigns, channels, messaging, targeting)
            8. ENSURE PROPER SPACING in all text - add spaces around company names, product names, and between words

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

            TEXT FORMATTING REQUIREMENTS:
            - Ensure proper spacing between all words and phrases
            - Add spaces before and after company names in sentences
            - Properly format numbers with appropriate spacing
            - Use correct grammar and sentence structure
            - Proofread all generated text for spacing errors

            IMPORTANT: Use proper market segmentation categories:
            
            1. GEOGRAPHICS: Must be GRANULAR - Country, State, Metro Area, Urban/Suburban, DMA, ZIP codes when relevant
            2. DEMOGRAPHICS: Age, Gender, Income, Education, Social Status, Family, Life Stage, Occupation  
            3. PSYCHOGRAPHICS: Lifestyle, AIO (Activity/Interest/Opinion), Concerns, Personality, Values, Attitudes
            4. BEHAVIORAL: Purchase, Usage, Intent, Occasion, Buyer Stage, Life Cycle Stage, Engagement{firmographic_instruction}

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
                "analysis_perspective": "{analysis_perspective}",
                {brand_position_json}
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
                            "demographic_factors": ["Age range", "Income level", "Education", "Occupation"],
                            "resonate_mapping": {{
                                "demographics": {{
                                    "age_range": "specific age range for Resonate (e.g., '25-34', '35-44', '45-54')",
                                    "gender": "gender composition (e.g., 'Male', 'Female', 'Mixed')", 
                                    "household_income": "household income bracket (e.g., '$50K-$75K', '$75K-$100K', '$100K+')",
                                    "education": "education level (e.g., 'College Graduate', 'High School', 'Post Graduate')",
                                    "employment": "employment category (e.g., 'Professional', 'Management', 'Service', 'Retired')"
                                }},
                                "geographics": {{
                                    "region": "geographic region (e.g., 'Northeast', 'Southeast', 'West Coast', 'Midwest')",
                                    "market_size": "market type (e.g., 'Major Metro', 'Mid-size City', 'Small City', 'Rural')", 
                                    "geography_type": "area type (e.g., 'Urban', 'Suburban', 'Rural')"
                                }},
                                "media_usage": {{
                                    "primary_media": ["main media channels (e.g., 'Social Media', 'TV', 'Digital', 'Radio', 'Print')"],
                                    "digital_engagement": "digital engagement level (e.g., 'High', 'Medium', 'Low')",
                                    "content_preferences": ["content types (e.g., 'Video', 'Articles', 'Podcasts', 'Social Content')"]
                                }},
                                "resonate_taxonomy_paths": [
                                    "Demographics > Demographics > Identity > Age Group > [age_range]",
                                    "Demographics > Demographics > Identity > Gender > [gender]", 
                                    "Demographics > Demographics > SocioEconomic > Household Income > [income_bracket]",
                                    "Demographics > Demographics > SocioEconomic > Education > [education_level]"
                                ],
                                "mapping_confidence": "confidence level for Resonate mapping (High, Medium, Low)"
                            }}
                        }}
                    ],
                    "by_psychographics": [
                        {{
                            "name": "psychographic segment name",
                            "description": "psychographic description focusing on lifestyle, values, attitudes, interests",
                            "size": [size in dollars], 
                            "growth": [growth rate as decimal],
                            "key_players": ["company1", "company2"],
                            "psychographic_factors": ["Lifestyle", "Values", "Attitudes", "Interests"],
                            "resonate_mapping": {{
                                "demographics": {{
                                    "age_range": "age range (e.g., '25-34', '35-44', '45-54')",
                                    "gender": "gender mix (e.g., 'Male', 'Female', 'Mixed')", 
                                    "household_income": "income level (e.g., '$50K-$75K', '$75K-$100K', '$100K+')",
                                    "education": "education (e.g., 'College Graduate', 'High School', 'Post Graduate')",
                                    "employment": "job category (e.g., 'Professional', 'Management', 'Creative')"
                                }},
                                "geographics": {{
                                    "region": "region (e.g., 'Northeast', 'West Coast', 'Midwest')",
                                    "market_size": "market type (e.g., 'Major Metro', 'Mid-size City')", 
                                    "geography_type": "area (e.g., 'Urban', 'Suburban')"
                                }},
                                "media_usage": {{
                                    "primary_media": ["media channels based on psychographic profile"],
                                    "digital_engagement": "engagement level (e.g., 'High', 'Medium', 'Low')",
                                    "content_preferences": ["content aligned with values and lifestyle"]
                                }},
                                "resonate_taxonomy_paths": [
                                    "Demographics > Demographics > Identity > Age Group > [age_range]",
                                    "Demographics > Demographics > SocioEconomic > Household Income > [income_bracket]",
                                    "Media > Media Consumption > Digital Engagement > [engagement_level]"
                                ],
                                "mapping_confidence": "mapping confidence (High, Medium, Low)"
                            }}
                        }}
                    ],
                    "by_behavioral": [
                        {{
                            "name": "behavioral segment name",
                            "description": "behavioral description focusing on usage, purchase patterns, buyer stage",
                            "size": [size in dollars],
                            "growth": [growth rate as decimal], 
                            "key_players": ["company1", "company2"],
                            "behavioral_factors": ["Usage patterns", "Purchase frequency", "Buyer stage", "Engagement level"],
                            "resonate_mapping": {{
                                "demographics": {{
                                    "age_range": "age range (e.g., '25-34', '35-44', '45-54')",
                                    "gender": "gender composition (e.g., 'Male', 'Female', 'Mixed')", 
                                    "household_income": "income bracket (e.g., '$50K-$75K', '$75K-$100K', '$100K+')",
                                    "education": "education level (e.g., 'College Graduate', 'High School', 'Post Graduate')",
                                    "employment": "employment type (e.g., 'Professional', 'Management', 'Service')"
                                }},
                                "geographics": {{
                                    "region": "geographic region (e.g., 'Northeast', 'West Coast', 'Midwest')",
                                    "market_size": "market size (e.g., 'Major Metro', 'Mid-size City', 'Small City')", 
                                    "geography_type": "geography (e.g., 'Urban', 'Suburban', 'Rural')"
                                }},
                                "media_usage": {{
                                    "primary_media": ["media consumption patterns based on behavior"],
                                    "digital_engagement": "digital usage level (e.g., 'High', 'Medium', 'Low')",
                                    "content_preferences": ["content types that drive behavior"]
                                }},
                                "resonate_taxonomy_paths": [
                                    "Demographics > Demographics > Identity > Age Group > [age_range]",
                                    "Demographics > Demographics > SocioEconomic > Household Income > [income_bracket]",
                                    "Media > Media Consumption > Digital Engagement > [engagement_level]",
                                    "Consumer Preferences > Shopping Behavior > [behavior_type] > [intensity]"
                                ],
                                "mapping_confidence": "confidence level (High, Medium, Low)"
                            }}
                        }}
                    ]{firmographic_json}
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
                "competitive_digital_assessment": {{
                    // IMPORTANT: Use actual competitor company names from the competitors list above, NOT placeholder names like "competitor_1". Replace the placeholder keys with real company names like "Apple", "Fitbit", "Garmin", etc.
                    "{market_input.product_name}": {{
                        "digital_marketing_strategy": "Current digital marketing approach and channels",
                        "advertising_spend_estimate": "Estimated annual advertising budget",
                        "primary_channels": ["channel1", "channel2", "channel3"],
                        "social_media_presence": "Assessment of social media strategy and engagement",
                        "content_marketing": "Content strategy and thought leadership approach",
                        "paid_advertising": "Paid search, display, social advertising strategy",
                        "seo_positioning": "Organic search presence and keyword strategy",
                        "marketing_strengths": ["strength1", "strength2"],
                        "marketing_gaps": ["gap1", "gap2"]
                    }},
                    "[USE ACTUAL COMPETITOR NAME FROM COMPETITORS LIST - e.g., Apple, Fitbit, Garmin]": {{
                        "digital_marketing_strategy": "Competitor's digital marketing approach and channel strategy",
                        "advertising_spend_estimate": "Estimated annual advertising budget",
                        "primary_channels": ["primary marketing channels they use"],
                        "social_media_presence": "Assessment of social media strategy and engagement levels",
                        "content_marketing": "Content strategy and thought leadership approach",
                        "paid_advertising": "Paid search, display, social advertising strategy",
                        "seo_positioning": "Organic search presence and keyword strategy",
                        "marketing_strengths": ["specific marketing strengths"],
                        "marketing_gaps": ["identified marketing weaknesses"]
                    }},
                    "[USE SECOND ACTUAL COMPETITOR NAME FROM COMPETITORS LIST]": {{
                        "digital_marketing_strategy": "Second competitor's digital marketing approach",
                        "advertising_spend_estimate": "Estimated annual advertising budget", 
                        "primary_channels": ["primary marketing channels they use"],
                        "social_media_presence": "Assessment of social media strategy and engagement levels",
                        "content_marketing": "Content strategy and thought leadership approach",
                        "paid_advertising": "Paid search, display, social advertising strategy",
                        "seo_positioning": "Organic search presence and keyword strategy",
                        "marketing_strengths": ["specific marketing strengths"],
                        "marketing_gaps": ["identified marketing weaknesses"]
                    }}
                }},
                "opportunities": [list of 4-5 marketing-specific market opportunities],
                "threats": [list of 4-5 marketing-specific competitive threats], 
                "recommendations": [list of 4-5 actionable marketing recommendations],
                "marketing_opportunities": [list of 4-5 marketing-specific opportunities],
                "marketing_threats": [list of 4-5 marketing-specific competitive threats],
                "marketing_recommendations": [list of 4-5 actionable marketing recommendations],
                "executive_summary": "A well-formatted executive summary structured as follows:\\n\\n**1. MARKETING CHALLENGE**\\nFormulate a SMART marketing question for {market_input.product_name}, focusing on market share growth through marketing and advertising strategies. Example: 'How can {market_input.product_name} increase market share by X% through enhanced digital marketing and targeted advertising campaigns by 2027?'\\n\\n**2. MARKET CONTEXT**\\nDescribe the marketing landscape, digital trends, competitive positioning, brand awareness gaps, and marketing budget considerations. Focus on customer acquisition costs, lifetime value, and channel effectiveness.\\n\\n**3. MARKETING SUCCESS METRICS**\\nDefine success through marketing KPIs: brand awareness lift, lead generation improvement, conversion rate optimization, customer acquisition cost reduction, and campaign ROI targets.\\n\\n**4. MARKETING SCOPE & FOCUS**\\nOutline target markets, customer segments, geographic focus, and marketing channels included. Specify any constraints such as budget limitations or organic vs. paid growth focus.\\n\\n**5. KEY MARKETING STAKEHOLDERS**\\nIdentify marketing decision-makers, brand managers, customer segments, marketing agencies, and media partners who influence marketing success.\\n\\n**6. MARKETING INSIGHT SOURCES**\\nList customer research needs, competitive intelligence, digital analytics, campaign data, and external marketing expertise required for strategy execution.",
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

            CRITICAL: The executive_summary MUST follow the 6-section structure outlined above and be suitable for C-level executives. Include specific numbers, insights, and actionable recommendations. The analysis perspective is: {analysis_perspective} - ensure the summary is written accordingly.

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
                
                # Sanitize JSON content to remove invalid control characters
                def sanitize_json_content(json_str):
                    """Remove invalid control characters that break JSON parsing"""
                    # Remove control characters except for \n, \r, \t which are valid in JSON strings
                    json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
                    # Fix common control character issues
                    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    # Handle unescaped quotes within strings
                    json_str = re.sub(r'(?<!\\)"(?=.*".*:)', '\\"', json_str)
                    return json_str
                
                # Apply sanitization before parsing
                sanitized_content = sanitize_json_content(content)
                ai_analysis = json.loads(sanitized_content)
                logger.info("Successfully parsed AI analysis for %s", market_input.product_name)
                
                return ai_analysis
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"JSON parsing error for {market_input.product_name}: {e}")
                logger.error("Raw content length: %d characters", len(content))
                logger.error("Raw content sample: %s", content[:500])
                logger.error("Sanitized content sample: %s", sanitized_content[:500] if 'sanitized_content' in locals() else "N/A")
                
                # Try a more aggressive cleanup as last resort
                try:
                    # Remove all control characters and try again
                    emergency_clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', content)
                    emergency_clean = re.sub(r'\s+', ' ', emergency_clean)  # Normalize whitespace
                    ai_analysis = json.loads(emergency_clean)
                    logger.warning(f"Emergency JSON cleanup successful for {market_input.product_name}")
                    return ai_analysis
                except:
                    logger.error(f"Emergency cleanup also failed for {market_input.product_name}")
                
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
        """Fallback analysis - try curated data first, then generic fallback"""
        logger.warning(f"Using fallback analysis for {market_input.product_name}")
        
        # Determine analysis perspective  
        has_specific_brand = bool(market_input.product_name and 
                                 market_input.product_name.strip() and 
                                 market_input.product_name.lower() not in ['new product', 'new service', 'startup', 'new company'])
        analysis_perspective = "existing_brand" if has_specific_brand else "new_entrant"
        
        # Determine if this is B2B for firmographic analysis
        is_b2b = any(term in market_input.industry.lower() for term in ['b2b', 'business', 'enterprise', 'saas', 'software', 'financial services', 'consulting', 'professional services'])
        
        # Try to get curated market data first
        curated_data = MarketIntelligenceAgent.get_curated_market_data(
            market_input.product_name.lower(), 
            market_input.industry.lower(), 
            market_input.geography.lower()
        )
        
        if curated_data:
            logger.info(f"Using curated market data for {market_input.product_name}")
            # Use curated data for better analysis
            tam = curated_data["tam"]
            sam = int(tam * 0.3)  # 30% SAM
            som = int(sam * 0.1)  # 10% SOM
            
            # Use real competitors from curated data
            real_competitors = []
            for i, comp_name in enumerate(curated_data["competitors"][:5]):
                real_competitors.append({
                    "name": comp_name,
                    "share": [0.25, 0.20, 0.15, 0.12, 0.10][i] if i < 5 else 0.08,
                    "strengths": ["Market presence", "Brand recognition"],
                    "weaknesses": ["Competition", "Market saturation"],
                    "price_range": "$150-$400",
                    "price_tier": "Mid-Range",
                    "innovation_focus": "Market growth",
                    "user_segment": market_input.target_user
                })
            competitors = real_competitors
        else:
            logger.info(f"No curated data found, using generic analysis for {market_input.product_name}")
            # Generate basic market analysis with generic data
            tam = 1000000000  # $1B default TAM
            sam = int(tam * 0.3)  # 30% SAM
            som = int(sam * 0.1)  # 10% SOM
            
            # Generic competitors as fallback
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

        # Build segmentation data
        segmentation = {
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
        }
        
        # Add firmographic segmentation only for B2B
        if is_b2b:
            segmentation["by_firmographics"] = [
                {
                    "name": "Enterprise Clients",
                    "description": "Large corporations with 1000+ employees",
                    "size": int(sam * 0.4),
                    "growth": 0.06,
                    "key_players": ["Market Leader", "Technology Innovator"],
                    "firmographic_factors": ["Enterprise", "1000+ employees", "Global locations", "C-suite", "$1B+ revenue"]
                },
                {
                    "name": "Mid-Market Companies",
                    "description": "Growing companies with 100-1000 employees",
                    "size": int(sam * 0.35),
                    "growth": 0.09,
                    "key_players": ["Growth Challenger", "Technology Innovator"],
                    "firmographic_factors": ["Mid-market", "100-1000 employees", "Regional presence", "Director level", "$10M-$1B revenue"]
                },
                {
                    "name": "Small Businesses",
                    "description": "Small businesses with under 100 employees",
                    "size": int(sam * 0.25),
                    "growth": 0.12,
                    "key_players": ["Value Player", "Growth Challenger"],
                    "firmographic_factors": ["Small business", "Under 100 employees", "Local presence", "Manager level", "Under $10M revenue"]
                }
            ]
        else:
            segmentation["by_firmographics"] = []
            
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
            "analysis_perspective": analysis_perspective,
            **({"brand_position": f"Fallback position analysis for {market_input.product_name}"} if analysis_perspective == "existing_brand" else {}),
            "segmentation": segmentation,
            "competitors": competitors,
            "opportunities": [
                f"{market_input.demand_driver} driving market growth",
                f"Underserved segments in {market_input.geography}",
                "Technology integration opportunities",
                f"Partnership potential in {market_input.industry}"
            ],
            "threats": [
                f"Intense competition in {market_input.industry}",
                "Market saturation risks",
                "Regulatory challenges",
                "Economic uncertainty"
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
            "firmographic_segments": [],
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

        # Process firmographic segments (B2B only)
        firmographic_segments = market_data.get("segmentation", {}).get("by_firmographics", [])
        for i, segment in enumerate(firmographic_segments):
            icon = "🏢" if i == 0 else "🏭" if i == 1 else "🏪" if i == 2 else "🏬"
            color = "teal" if i == 0 else "cyan" if i == 1 else "sky" if i == 2 else "slate"
            
            visual_map["firmographic_segments"].append({
                "name": segment.get("name", f"Firmographic Segment {i+1}"),
                "description": segment.get("description", "B2B firmographic segment"),
                "size": segment.get("size", 700000000),
                "growth": segment.get("growth", 0.06),
                "icon": icon,
                "color": color,
                "key_players": segment.get("key_players", [])
            })

        return visual_map

class ComprehensiveAnalysisEngine:
    @staticmethod
    async def generate_market_map(market_input: MarketInput, ai_analysis: Dict[str, Any], ppc_intelligence: Dict[str, Any] = None) -> MarketMap:
        """Generate comprehensive market map from AI analysis"""
        try:
            # Determine analysis perspective
            has_specific_brand = bool(market_input.product_name and 
                                     market_input.product_name.strip() and 
                                     market_input.product_name.lower() not in ['new product', 'new service', 'startup', 'new company'])
            analysis_perspective = "existing_brand" if has_specific_brand else "new_entrant"
            
            market_overview = ai_analysis.get("market_overview", {})
            segmentation = ai_analysis.get("segmentation", {})
            competitors = ai_analysis.get("competitors", [])
            opportunities = ai_analysis.get("opportunities", [])
            if not opportunities:  # If opportunities is empty, try marketing_opportunities
                opportunities = ai_analysis.get("marketing_opportunities", [])
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
            firmographic_segments = []
            
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
                # Process resonate mapping data if available
                resonate_mapping = None
                if "resonate_mapping" in seg:
                    try:
                        rm_data = seg["resonate_mapping"]
                        resonate_mapping = ResonateSegmentMapping(
                            demographics=ResonateBaseDemographics(**rm_data.get("demographics", {})) if "demographics" in rm_data else None,
                            geographics=ResonateGeographics(**rm_data.get("geographics", {})) if "geographics" in rm_data else None,
                            media_usage=ResonateMediaUsage(**rm_data.get("media_usage", {})) if "media_usage" in rm_data else None,
                            resonate_taxonomy_paths=rm_data.get("resonate_taxonomy_paths", []),
                            mapping_confidence=rm_data.get("mapping_confidence")
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create Resonate mapping for demographic segment {seg.get('name', 'Unknown')}: {e}")
                        resonate_mapping = None
                
                demographic_segments.append(MarketSegment(
                    name=seg.get("name", "Demographic Segment"),
                    description=seg.get("description", "Demographic segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Company A", "Company B"]),
                    resonate_mapping=resonate_mapping
                ))
            
            for seg in segmentation.get("by_psychographics", []):
                # Process resonate mapping data if available
                resonate_mapping = None
                if "resonate_mapping" in seg:
                    try:
                        rm_data = seg["resonate_mapping"]
                        resonate_mapping = ResonateSegmentMapping(
                            demographics=ResonateBaseDemographics(**rm_data.get("demographics", {})) if "demographics" in rm_data else None,
                            geographics=ResonateGeographics(**rm_data.get("geographics", {})) if "geographics" in rm_data else None,
                            media_usage=ResonateMediaUsage(**rm_data.get("media_usage", {})) if "media_usage" in rm_data else None,
                            resonate_taxonomy_paths=rm_data.get("resonate_taxonomy_paths", []),
                            mapping_confidence=rm_data.get("mapping_confidence")
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create Resonate mapping for psychographic segment {seg.get('name', 'Unknown')}: {e}")
                        resonate_mapping = None
                
                psychographic_segments.append(MarketSegment(
                    name=seg.get("name", "Psychographic Segment"),
                    description=seg.get("description", "Psychographic segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Company A", "Company B"]),
                    resonate_mapping=resonate_mapping
                ))
            
            for seg in segmentation.get("by_behavioral", []):
                # Process resonate mapping data if available
                resonate_mapping = None
                if "resonate_mapping" in seg:
                    try:
                        rm_data = seg["resonate_mapping"]
                        resonate_mapping = ResonateSegmentMapping(
                            demographics=ResonateBaseDemographics(**rm_data.get("demographics", {})) if "demographics" in rm_data else None,
                            geographics=ResonateGeographics(**rm_data.get("geographics", {})) if "geographics" in rm_data else None,
                            media_usage=ResonateMediaUsage(**rm_data.get("media_usage", {})) if "media_usage" in rm_data else None,
                            resonate_taxonomy_paths=rm_data.get("resonate_taxonomy_paths", []),
                            mapping_confidence=rm_data.get("mapping_confidence")
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create Resonate mapping for behavioral segment {seg.get('name', 'Unknown')}: {e}")
                        resonate_mapping = None
                
                behavioral_segments.append(MarketSegment(
                    name=seg.get("name", "Behavioral Segment"),
                    description=seg.get("description", "Behavioral segment"),
                    size_estimate=float(seg.get("size", 1000000000)),
                    growth_rate=float(seg.get("growth", 0.05)),
                    key_players=seg.get("key_players", ["Company A", "Company B"]),
                    resonate_mapping=resonate_mapping
                ))
            
            for seg in segmentation.get("by_firmographics", []):
                firmographic_segments.append(MarketSegment(
                    name=seg.get("name", "Firmographic Segment"),
                    description=seg.get("description", "Firmographic segment"),
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
                analysis_perspective=ai_analysis.get("analysis_perspective", analysis_perspective),
                brand_position=ai_analysis.get("brand_position"),
                segmentation_by_geographics=geographic_segments,
                segmentation_by_demographics=demographic_segments,
                segmentation_by_psychographics=psychographic_segments,
                segmentation_by_behavioral=behavioral_segments,
                segmentation_by_firmographics=firmographic_segments,
                competitors=competitor_objects,
                opportunities=opportunities,
                threats=threats,
                strategic_recommendations=recommendations,
                marketing_opportunities=ai_analysis.get("marketing_opportunities", []),
                marketing_threats=ai_analysis.get("marketing_threats", []),
                marketing_recommendations=ai_analysis.get("marketing_recommendations", []),
                competitive_digital_assessment=ai_analysis.get("competitive_digital_assessment", {}),
                ppc_intelligence=ppc_intelligence or {},
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
            # Determine analysis perspective for fallback
            has_specific_brand = bool(market_input.product_name and 
                                     market_input.product_name.strip() and 
                                     market_input.product_name.lower() not in ['new product', 'new service', 'startup', 'new company'])
            analysis_perspective = "existing_brand" if has_specific_brand else "new_entrant"
            # Return basic fallback market map
            return MarketMap(
                id=str(uuid.uuid4()),
                market_input_id=market_input.id,
                total_market_size=5000000000,
                market_growth_rate=0.08,
                key_drivers=["Market growth", "Technology adoption"],
                analysis_perspective=analysis_perspective,
                brand_position=f"Fallback position analysis for {market_input.product_name}" if analysis_perspective == "existing_brand" else None,
                segmentation_by_geographics=[],
                segmentation_by_demographics=[],
                segmentation_by_psychographics=[],
                segmentation_by_behavioral=[],
                segmentation_by_firmographics=[],
                competitors=[],
                opportunities=["Market opportunity 1", "Market opportunity 2"],
                threats=["Market threat 1", "Market threat 2"],
                strategic_recommendations=["Focus on differentiation", "Build partnerships"],
                marketing_opportunities=["Digital marketing expansion", "Social media engagement"],
                marketing_threats=["Competitor digital presence", "Rising advertising costs"],
                marketing_recommendations=["Invest in content marketing", "Optimize conversion funnels"],
                competitive_digital_assessment={},
                ppc_intelligence={},
                executive_summary=f"""
                **1. MARKETING CHALLENGE**
                How can {market_input.product_name} increase market share by 15-25% through enhanced digital marketing campaigns and targeted advertising strategies within the next 2-3 years?

                **2. MARKET CONTEXT**  
                The {market_input.industry} marketing landscape is evolving with digital-first customer acquisition driven by {market_input.demand_driver}. {market_input.product_name} needs strategic marketing positioning to effectively reach {market_input.target_user} in an increasingly competitive advertising environment.

                **3. MARKETING SUCCESS METRICS**
                Success will be measured by brand awareness lift, lead generation improvement, customer acquisition cost reduction, campaign ROI optimization, and improved {market_input.key_metrics} through marketing initiatives.

                **4. MARKETING SCOPE & FOCUS**
                Analysis focuses on {market_input.geography} digital marketing opportunities with emphasis on paid advertising, content marketing, and social media strategies within the {market_input.industry} sector.

                **5. KEY MARKETING STAKEHOLDERS**
                Marketing team, brand managers, target customers ({market_input.target_user}), digital agencies, media partners, and competitive marketing teams.

                **6. MARKETING INSIGHT SOURCES**
                Customer research, competitive advertising intelligence, digital analytics, campaign performance data, and marketing industry benchmarks for strategic campaign development.

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
async def analyze_market(market_input: MarketInput, user: User = Depends(require_auth)):
    try:
        logger.info(f"Starting market analysis for: {market_input.product_name}")
        
        # Step 1: Comprehensive AI Market Intelligence
        logger.info("Step 1: Starting AI market intelligence analysis...")
        ai_analysis = await MarketIntelligenceAgent.analyze_market_landscape(market_input)
        logger.info("Step 1: AI analysis completed successfully")

        # Step 1.5: PPC Competitive Intelligence
        logger.info("Step 1.5: Starting PPC competitive intelligence analysis...")
        ppc_intelligence = {}
        try:
            # Extract domain from product name for PPC analysis
            target_domain = extract_domain_from_company(market_input.product_name)
            ppc_report = await spyfu_service.generate_ppc_intelligence_report(target_domain)
            
            ppc_intelligence = {
                "target_domain": ppc_report.target_domain,
                "paid_keywords_count": len(ppc_report.paid_keywords),
                "top_keywords": [
                    {
                        "keyword": kw.keyword,
                        "monthly_searches": kw.monthly_searches,
                        "cpc": kw.cpc,
                        "competition": kw.competition,
                        "estimated_monthly_cost": kw.estimated_monthly_cost
                    } for kw in ppc_report.paid_keywords[:10]
                ],
                "competitors_count": len(ppc_report.top_competitors),
                "top_ppc_competitors": [
                    {
                        "domain": comp.domain,
                        "overlapping_keywords": comp.overlapping_keywords,
                        "estimated_monthly_spend": comp.estimated_monthly_spend
                    } for comp in ppc_report.top_competitors[:10]
                ],
                "ad_history_count": len(ppc_report.ad_history),
                "recent_ads": [
                    {
                        "ad_text": ad.ad_text,
                        "keyword": ad.keyword,
                        "position": ad.position
                    } for ad in ppc_report.ad_history[:5]
                ],
                "domain_stats": ppc_report.domain_stats.dict() if ppc_report.domain_stats else None,
                "confidence_level": ppc_report.confidence_level
            }
            logger.info("Step 1.5: PPC intelligence analysis completed successfully")
        except Exception as e:
            logger.warning(f"Step 1.5: PPC intelligence analysis failed: {e}")
            ppc_intelligence = {"error": str(e), "confidence_level": "Low - PPC Data Not Available"}

        # Step 2: Generate Market Map
        logger.info("Step 2: Starting market map generation...")
        market_map = await ComprehensiveAnalysisEngine.generate_market_map(market_input, ai_analysis, ppc_intelligence)
        logger.info("Step 2: Market map generation completed successfully")

        # Step 3: Generate Visual Map
        logger.info("Step 3: Starting visual map generation...")
        visual_map = VisualMapGenerator.generate_visual_market_map(ai_analysis, market_input.product_name)
        logger.info("Step 3: Visual map generation completed successfully")

        # Step 4: Save to database
        logger.info("Step 4: Saving data to database...")
        await db.market_inputs.insert_one(market_input.dict())
        logger.info("Step 4a: Market input saved to database")
        
        await db.market_maps.insert_one(market_map.dict())
        logger.info("Step 4b: Market map saved to database")

        # Step 5: Generate final analysis
        logger.info("Step 5: Generating final analysis response...")
        analysis = MarketAnalysis(
            market_input=market_input,
            market_map=market_map,
            visual_map=visual_map
        )
        logger.info("Step 5: Final analysis generated successfully")

        logger.info(f"Market analysis completed successfully for: {market_input.product_name}")
        return analysis

    except Exception as e:
        logger.error(f"Error in analyze_market for {market_input.product_name}: {e}")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")

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
    """Export market analysis as professional PDF matching web design"""
    try:
        # Get analysis from database
        market_map = await db.market_maps.find_one({"id": analysis_id})
        if not market_map:
            raise HTTPException(status_code=404, detail="Market map not found")

        market_input = await db.market_inputs.find_one({"id": market_map["market_input_id"]})
        if not market_input:
            raise HTTPException(status_code=404, detail="Market input not found")
        
        # Generate PDF using new generator
        pdf_data = create_market_report_pdf(market_map, market_input)
        
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

        # Handle backward compatibility for older reports missing new fields
        market_map_data = dict(market_map)
        
        # Add default values for missing fields in older reports
        if "analysis_perspective" not in market_map_data:
            market_map_data["analysis_perspective"] = "new_entrant"
        if "brand_position" not in market_map_data:
            market_map_data["brand_position"] = None
        if "segmentation_by_firmographics" not in market_map_data:
            market_map_data["segmentation_by_firmographics"] = []
        
        # Recreate analysis object
        analysis = MarketAnalysis(
            market_input=MarketInput(**market_input),
            market_map=MarketMap(**market_map_data)
        )

        # Generate visual map using the existing segmentation data
        visual_map = VisualMapGenerator.generate_visual_market_map({
            "segmentation": {
                "by_geographics": market_map_data.get("segmentation_by_geographics", []),
                "by_demographics": market_map_data.get("segmentation_by_demographics", []),
                "by_psychographics": market_map_data.get("segmentation_by_psychographics", []),
                "by_behavioral": market_map_data.get("segmentation_by_behavioral", []),
                "by_firmographics": market_map_data.get("segmentation_by_firmographics", [])
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

@api_router.get("/export-personas/{analysis_id}")
async def export_personas(analysis_id: str):
    """Export enhanced persona data for persona development and Resonate rAI integration"""
    try:
        # Get market map from database
        market_map = await db.market_maps.find_one({"id": analysis_id})
        if not market_map:
            raise HTTPException(status_code=404, detail="Analysis not found")

        market_input = await db.market_inputs.find_one({"id": market_map["market_input_id"]})
        if not market_input:
            raise HTTPException(status_code=404, detail="Market input not found")

        # Extract personas from all segment types
        personas = {
            "analysis_info": {
                "product_name": market_input["product_name"],
                "industry": market_input["industry"],
                "geography": market_input["geography"],
                "analysis_date": market_map.get("timestamp", ""),
                "market_size": market_map.get("total_market_size", 0)
            },
            "demographic_personas": [],
            "psychographic_personas": [],
            "behavioral_personas": [],
            "resonate_taxonomy_mapping": [],
            "persona_summary": {
                "total_segments": 0,
                "personas_with_enhanced_data": 0,
                "resonate_categories_covered": []
            }
        }

        # Process demographic segments
        for segment in market_map.get("segmentation_by_demographics", []):
            resonate_mapping = segment.get("resonate_mapping", {}) or {}
            
            # For older analyses without enhanced data, provide basic inference
            if not resonate_mapping or not any(resonate_mapping.values()):
                # Generate basic demographic data from segment description and name
                segment_desc = segment.get("description", "").lower()
                segment_name = segment.get("name", "").lower()
                
                # Infer basic demographics from description
                age_range = "25-54"  # Default professional range
                if "young" in segment_desc or "millennial" in segment_desc:
                    age_range = "25-34"
                elif "senior" in segment_desc or "mature" in segment_desc:
                    age_range = "45-64"
                
                income_bracket = "$50K-$100K"  # Default middle class
                if "high income" in segment_desc or "affluent" in segment_desc or "executive" in segment_desc:
                    income_bracket = "$100K+"
                elif "budget" in segment_desc or "cost-conscious" in segment_desc:
                    income_bracket = "$25K-$50K"
                
                education = "College Graduate"
                if "professional" in segment_desc or "corporate" in segment_desc:
                    education = "College Graduate"
                
                employment = "Professional"
                if "manager" in segment_desc or "executive" in segment_desc:
                    employment = "Management"
                
                # Create basic resonate mapping for legacy data
                resonate_mapping = {
                    "demographics": {
                        "age_range": age_range,
                        "gender": "Mixed",
                        "household_income": income_bracket,
                        "education": education,
                        "employment": employment
                    },
                    "geographics": {
                        "region": market_input.get("geography", "United States"),
                        "market_size": "Major Metro",
                        "geography_type": "Urban"
                    },
                    "media_usage": {
                        "primary_media": ["Digital", "Social Media"],
                        "digital_engagement": "High",
                        "content_preferences": ["Professional Content", "Industry News"]
                    },
                    "resonate_taxonomy_paths": [
                        f"Demographics > Demographics > Identity > Age Group > {age_range}",
                        f"Demographics > Demographics > SocioEconomic > Household Income > {income_bracket}",
                        f"Demographics > Demographics > SocioEconomic > Education > {education}"
                    ],
                    "mapping_confidence": "Medium (Inferred)"
                }
            
            persona_data = {
                "segment_name": segment.get("name"),
                "description": segment.get("description"),
                "market_size": segment.get("size_estimate", 0),
                "growth_rate": segment.get("growth_rate", 0),
                "resonate_ready_data": {
                    "demographics": resonate_mapping.get("demographics", {}),
                    "geographics": resonate_mapping.get("geographics", {}),
                    "media_usage": resonate_mapping.get("media_usage", {}),
                    "taxonomy_paths": resonate_mapping.get("resonate_taxonomy_paths", []),
                    "confidence": resonate_mapping.get("mapping_confidence", "Medium")
                }
            }
            personas["demographic_personas"].append(persona_data)
            
            # Extract Resonate mappings for easy integration
            if resonate_mapping:
                personas["resonate_taxonomy_mapping"].append({
                    "segment_name": segment.get("name"),
                    "segment_type": "demographic", 
                    "demographics": resonate_mapping.get("demographics", {}),
                    "geographics": resonate_mapping.get("geographics", {}),
                    "media_usage": resonate_mapping.get("media_usage", {}),
                    "taxonomy_paths": resonate_mapping.get("resonate_taxonomy_paths", []),
                    "confidence": resonate_mapping.get("mapping_confidence", "Medium")
                })

        # Process psychographic segments  
        for segment in market_map.get("segmentation_by_psychographics", []):
            resonate_mapping = segment.get("resonate_mapping", {})
            persona_data = {
                "segment_name": segment.get("name"),
                "description": segment.get("description"), 
                "market_size": segment.get("size_estimate", 0),
                "growth_rate": segment.get("growth_rate", 0),
                "resonate_ready_data": {
                    "demographics": resonate_mapping.get("demographics", {}),
                    "geographics": resonate_mapping.get("geographics", {}),
                    "media_usage": resonate_mapping.get("media_usage", {}),
                    "taxonomy_paths": resonate_mapping.get("resonate_taxonomy_paths", []),
                    "confidence": resonate_mapping.get("mapping_confidence", "Medium")
                }
            }
            personas["psychographic_personas"].append(persona_data)
            
            # Extract Resonate mappings
            if resonate_mapping:
                personas["resonate_taxonomy_mapping"].append({
                    "segment_name": segment.get("name"),
                    "segment_type": "psychographic", 
                    "demographics": resonate_mapping.get("demographics", {}),
                    "geographics": resonate_mapping.get("geographics", {}),
                    "media_usage": resonate_mapping.get("media_usage", {}),
                    "taxonomy_paths": resonate_mapping.get("resonate_taxonomy_paths", []),
                    "confidence": resonate_mapping.get("mapping_confidence", "Medium")
                })

        # Process behavioral segments
        for segment in market_map.get("segmentation_by_behavioral", []):
            resonate_mapping = segment.get("resonate_mapping", {})
            persona_data = {
                "segment_name": segment.get("name"),
                "description": segment.get("description"),
                "market_size": segment.get("size_estimate", 0), 
                "growth_rate": segment.get("growth_rate", 0),
                "resonate_ready_data": {
                    "demographics": resonate_mapping.get("demographics", {}),
                    "geographics": resonate_mapping.get("geographics", {}),
                    "media_usage": resonate_mapping.get("media_usage", {}),
                    "taxonomy_paths": resonate_mapping.get("resonate_taxonomy_paths", []),
                    "confidence": resonate_mapping.get("mapping_confidence", "Medium")
                }
            }
            personas["behavioral_personas"].append(persona_data)
            
            # Extract Resonate mappings
            if resonate_mapping:
                personas["resonate_taxonomy_mapping"].append({
                    "segment_name": segment.get("name"),
                    "segment_type": "behavioral",
                    "demographics": resonate_mapping.get("demographics", {}),
                    "geographics": resonate_mapping.get("geographics", {}),
                    "media_usage": resonate_mapping.get("media_usage", {}),
                    "taxonomy_paths": resonate_mapping.get("resonate_taxonomy_paths", []),
                    "confidence": resonate_mapping.get("mapping_confidence", "Medium")
                })

        # Calculate summary statistics
        total_segments = len(personas["demographic_personas"]) + len(personas["psychographic_personas"]) + len(personas["behavioral_personas"])
        resonate_ready_count = sum(1 for p in personas["demographic_personas"] + personas["psychographic_personas"] + personas["behavioral_personas"] if p.get("resonate_ready_data"))
        
        # Collect unique taxonomy categories
        all_taxonomy_paths = []
        for mapping in personas["resonate_taxonomy_mapping"]:
            all_taxonomy_paths.extend(mapping.get("taxonomy_paths", []))
        
        personas["persona_summary"] = {
            "total_segments": total_segments,
            "resonate_ready_segments": resonate_ready_count,
            "total_taxonomy_mappings": len(all_taxonomy_paths),
            "resonate_integration_ready": resonate_ready_count > 0
        }

        return personas

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in export_personas: {e}")
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

# Include routers in the main app
app.include_router(api_router)
app.include_router(auth_router, prefix="/api")

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
