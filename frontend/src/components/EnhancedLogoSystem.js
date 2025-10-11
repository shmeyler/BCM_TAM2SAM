import React, { useState } from 'react';
import { 
  BuildingOfficeIcon, 
  GlobeAltIcon, 
  ShoppingCartIcon, 
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  TruckIcon,
  HomeIcon,
  CameraIcon,
  MusicalNoteIcon,
  FilmIcon,
  NewspaperIcon,
  TvIcon,
  RadioIcon
} from '@heroicons/react/24/outline';

import { 
  Building2, 
  Plane, 
  Car, 
  Coffee, 
  ShoppingBag,
  Smartphone,
  Monitor,
  Camera,
  Music,
  Video,
  Newspaper,
  Radio,
  Globe,
  Factory,
  Store,
  Briefcase
} from 'lucide-react';

// Company domain mapping for real logos
const COMPANY_DOMAINS = {
  // Tech Giants
  'apple': 'apple.com',
  'google': 'google.com', 
  'microsoft': 'microsoft.com',
  'amazon': 'amazon.com',
  'meta': 'meta.com',
  'facebook': 'facebook.com',
  'netflix': 'netflix.com',
  'spotify': 'spotify.com',
  'uber': 'uber.com',
  'airbnb': 'airbnb.com',
  'tesla': 'tesla.com',
  
  // Financial & Payments
  'paypal': 'paypal.com',
  'stripe': 'stripe.com',
  'visa': 'visa.com',
  'mastercard': 'mastercard.com',
  'american express': 'americanexpress.com',
  'amex': 'americanexpress.com',
  'jpmorgan': 'jpmorganchase.com',
  'goldman sachs': 'goldmansachs.com',
  
  // Enterprise Software
  'salesforce': 'salesforce.com',
  'slack': 'slack.com',
  'zoom': 'zoom.us',
  'dropbox': 'dropbox.com',
  'shopify': 'shopify.com',
  'hubspot': 'hubspot.com',
  'atlassian': 'atlassian.com',
  'oracle': 'oracle.com',
  'sap': 'sap.com',
  
  // Travel & Hospitality
  'marriott': 'marriott.com',
  'hilton': 'hilton.com',
  'expedia': 'expedia.com',
  'booking': 'booking.com',
  'airbnb': 'airbnb.com',
  'tripadvisor': 'tripadvisor.com',
  'delta': 'delta.com',
  'united': 'united.com',
  'american airlines': 'aa.com',
  
  // Retail & E-commerce
  'walmart': 'walmart.com',
  'target': 'target.com',
  'home depot': 'homedepot.com',
  'costco': 'costco.com',
  'best buy': 'bestbuy.com',
  
  // Food & Beverage  
  'starbucks': 'starbucks.com',
  'mcdonalds': 'mcdonalds.com',
  'coca cola': 'coca-cola.com',
  'pepsi': 'pepsi.com',
  
  // Media & Entertainment
  'disney': 'disney.com',
  'warner bros': 'warnerbros.com',
  'paramount': 'paramount.com',
  'nbc': 'nbc.com',
  'cbs': 'cbs.com',
  'fox': 'fox.com',
  'espn': 'espn.com',
  'cnn': 'cnn.com',
  'new york times': 'nytimes.com',
  'wall street journal': 'wsj.com'
};

// Industry-specific professional icons
const INDUSTRY_ICONS = {
  // Technology
  'software': <ComputerDesktopIcon className="w-6 h-6" />,
  'tech': <DevicePhoneMobileIcon className="w-6 h-6" />,
  'saas': <Monitor className="w-6 h-6" />,
  'mobile': <Smartphone className="w-6 h-6" />,
  
  // Business Services
  'consulting': <Briefcase className="w-6 h-6" />,
  'finance': <BuildingOfficeIcon className="w-6 h-6" />,
  'real estate': <HomeIcon className="w-6 h-6" />,
  'manufacturing': <Factory className="w-6 h-6" />,
  
  // Retail & Commerce
  'retail': <Store className="w-6 h-6" />,
  'ecommerce': <ShoppingCartIcon className="w-6 h-6" />,
  'marketplace': <ShoppingBag className="w-6 h-6" />,
  
  // Transportation  
  'transportation': <TruckIcon className="w-6 h-6" />,
  'automotive': <Car className="w-6 h-6" />,
  'logistics': <TruckIcon className="w-6 h-6" />,
  'airlines': <Plane className="w-6 h-6" />,
  
  // Media & Entertainment
  'media': <TvIcon className="w-6 h-6" />,
  'entertainment': <FilmIcon className="w-6 h-6" />,
  'music': <MusicalNoteIcon className="w-6 h-6" />,
  'gaming': <ComputerDesktopIcon className="w-6 h-6" />,
  'news': <NewspaperIcon className="w-6 h-6" />,
  'radio': <RadioIcon className="w-6 h-6" />,
  
  // Other Industries
  'food': <Coffee className="w-6 h-6" />,
  'healthcare': <Building2 className="w-6 h-6" />,
  'education': <BuildingOfficeIcon className="w-6 h-6" />,
  'photography': <CameraIcon className="w-6 h-6" />
};

// Real Brand Logo Component
const RealBrandLogo = ({ companyName, size = 32, className = "" }) => {
  const [logoError, setLogoError] = useState(false);
  const [logoLoaded, setLogoLoaded] = useState(false);
  
  // Extract domain from company name
  const getDomainFromCompany = (name) => {
    const cleanName = name.toLowerCase()
      .replace(/[^\w\s]/g, '') // Remove special characters
      .trim();
      
    // Check exact matches first
    if (COMPANY_DOMAINS[cleanName]) {
      return COMPANY_DOMAINS[cleanName];
    }
    
    // Check partial matches
    for (const [key, domain] of Object.entries(COMPANY_DOMAINS)) {
      if (cleanName.includes(key) || key.includes(cleanName)) {
        return domain;
      }
    }
    
    return null;
  };
  
  // Get professional fallback icon
  const getFallbackIcon = (name) => {
    const lowerName = name.toLowerCase();
    
    // Check industry keywords
    for (const [industry, icon] of Object.entries(INDUSTRY_ICONS)) {
      if (lowerName.includes(industry)) {
        return icon;
      }
    }
    
    // Default professional building icon
    return <BuildingOfficeIcon className="w-6 h-6 text-gray-600" />;
  };
  
  const domain = getDomainFromCompany(companyName);
  
  // If no domain found, return professional icon
  if (!domain) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        {getFallbackIcon(companyName)}
      </div>
    );
  }
  
  // Try to load real logo
  const logoUrl = `https://logo.clearbit.com/${domain}`;
  
  if (logoError) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        {getFallbackIcon(companyName)}
      </div>
    );
  }
  
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <img
        src={logoUrl}
        alt={`${companyName} logo`}
        width={size}
        height={size}
        className={`object-contain ${!logoLoaded ? 'opacity-0' : 'opacity-100'} transition-opacity`}
        onError={() => setLogoError(true)}
        onLoad={() => setLogoLoaded(true)}
        style={{ maxWidth: size, maxHeight: size }}
      />
      {!logoLoaded && !logoError && (
        <div className="animate-pulse bg-gray-200 rounded" 
             style={{ width: size, height: size }} />
      )}
    </div>
  );
};

// Enhanced Company Icon (combines logos + professional icons)
export const getEnhancedCompanyIcon = (companyName, size = 24) => {
  return <RealBrandLogo companyName={companyName} size={size} className="inline-flex" />;
};

// Direct Brand Logo Component for use in JSX
export const BrandLogo = ({ companyName, size = 32, className = "" }) => {
  return <RealBrandLogo companyName={companyName} size={size} className={className} />;
};

// Media Channel Icons (for advertising analysis)
export const getMediaChannelIcon = (channelName) => {
  const name = channelName.toLowerCase();
  
  const mediaIcons = {
    'google': <RealBrandLogo companyName="Google" size={20} />,
    'facebook': <RealBrandLogo companyName="Facebook" size={20} />,
    'instagram': <RealBrandLogo companyName="Facebook" size={20} />, // Instagram owned by Meta
    'linkedin': <RealBrandLogo companyName="LinkedIn" size={20} />,
    'twitter': <Globe className="w-5 h-5 text-blue-400" />, // Generic for Twitter/X
    'youtube': <RealBrandLogo companyName="Google" size={20} />, // YouTube owned by Google
    'tiktok': <Video className="w-5 h-5 text-black" />,
    'tv': <TvIcon className="w-5 h-5 text-gray-600" />,
    'radio': <RadioIcon className="w-5 h-5 text-gray-600" />,
    'print': <NewspaperIcon className="w-5 h-5 text-gray-700" />,
    'digital': <Monitor className="w-5 h-5 text-blue-600" />,
    'mobile': <Smartphone className="w-5 h-5 text-purple-600" />,
    'email': <GlobeAltIcon className="w-5 h-5 text-green-600" />
  };
  
  // Check for exact or partial matches
  for (const [key, icon] of Object.entries(mediaIcons)) {
    if (name.includes(key)) {
      return icon;
    }
  }
  
  return <GlobeAltIcon className="w-5 h-5 text-gray-500" />; // Default media icon
};

export default RealBrandLogo;