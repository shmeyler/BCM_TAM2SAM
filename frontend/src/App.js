import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Login from './components/Login';
import AdminPanel from './components/AdminPanel';
// Import React Icons for professional icons
import { 
  FaGlobe, 
  FaUsers, 
  FaBrain, 
  FaShoppingCart, 
  FaBuilding,
  FaApple,
  FaGoogle,
  FaMicrosoft,
  FaAmazon,
  FaFacebook,
  FaAirbnb,
  FaUber,
  FaSpotify,
  FaTwitter,
  FaInstagram,
  FaLinkedin,
  FaYoutube,
  FaNike,
  FaPaypal,
  FaStripe,
  FaSalesforce,
  FaSlack,
  FaDropbox,
  FaShopify,
  FaHotel,
  FaPlane,
  FaCar,
  FaMapMarkerAlt,
  FaTicketAlt,
  FaUmbrellaBeach,
  FaMountain,
  FaCity,
  FaGamepad,
  FaFilm,
  FaMusic,
  FaCamera,
  FaWifi,
  FaCoffee,
  FaPizzaSlice,
  FaHamburger,
  FaBeer,
  FaWineGlass
} from 'react-icons/fa';
import { 
  SiAdobe,
  SiAsana,
  SiTrello,
  SiNotion,
  SiFigma,
  SiCanva,
  SiVisa,
  SiMastercard
} from 'react-icons/si';

// Import Heroicons for professional icons
import { 
  ChartBarIcon,
  TvIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  TrophyIcon,
  StarIcon
} from '@heroicons/react/24/outline';

// Auto-detect backend URL based on current domain
const getBackendUrl = () => {
  const hostname = window.location.hostname;
  
  // If on custom domain, use same domain for backend
  if (hostname === 'www.bcmventas.com' || hostname === 'bcmventas.com') {
    return `https://${hostname}`;
  }
  
  // If on preview/localhost, use environment variable or current origin
  return process.env.REACT_APP_BACKEND_URL || window.location.origin;
};

const BACKEND_URL = getBackendUrl();
const API = `${BACKEND_URL}/api`;

console.log('Backend URL:', BACKEND_URL);

// Import Enhanced Logo System
import { getEnhancedCompanyIcon, getMediaChannelIcon, BrandLogo } from './components/EnhancedLogoSystem';

// Enhanced Company Icon Mapper (now uses real brand logos)
const getCompanyIcon = (companyName) => {
  return getEnhancedCompanyIcon(companyName, 24);
  // All icon mapping now handled by Enhanced Logo System
};

// Get Company Logo for larger displays
const getCompanyLogo = (companyName) => {
  return getEnhancedCompanyIcon(companyName, 32);
};

// Get Media Channel Icon for advertising analysis  
const getMediaIcon = (channelName) => {
  return getMediaChannelIcon(channelName);
};

// Helper function to format time in a user-friendly way
const formatTimeRemaining = (seconds) => {
  if (seconds <= 0) return '';
  if (seconds < 60) return `${seconds} seconds`;
  
  const minutes = Math.ceil(seconds / 60);
  if (minutes === 1) return '1 minute';
  if (minutes <= 5) return `${minutes} minutes`;
  
  // For longer times, show a range
  const minMinutes = Math.floor(minutes * 0.8);
  const maxMinutes = Math.ceil(minutes * 1.2);
  return `${minMinutes}-${maxMinutes} minutes`;
};

const MarketMapApp = () => {
  // Authentication state
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [showAdminPanel, setShowAdminPanel] = useState(false);

  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    product_name: '',
    industry: '',
    geography: '',
    target_user: '',
    demand_driver: '',
    transaction_type: '',
    key_metrics: '',
    benchmarks: '',
    output_format: 'excel'
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState({
    currentStep: 0,
    totalSteps: 5,
    stepName: '',
    estimatedTimeLeft: 0,
    steps: [
      { name: 'Analyzing Market Landscape with AI', duration: 60 },
      { name: 'Processing Competitive Intelligence', duration: 45 },
      { name: 'Generating Market Segmentation', duration: 30 },
      { name: 'Creating Executive Summary', duration: 50 },
      { name: 'Finalizing Visual Market Map', duration: 15 }
    ]
  });
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingMessage, setProcessingMessage] = useState('');

  // Check authentication on mount and handle OAuth redirect
  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (user) {
      loadHistory();
    }
  }, [user]);

  const checkAuth = async () => {
    try {
      // Check if we're coming back from OAuth with session_id in URL FRAGMENT (after #)
      const hashFragment = window.location.hash.substring(1); // Remove the #
      const hashParams = new URLSearchParams(hashFragment);
      const sessionId = hashParams.get('session_id');

      console.log('Checking auth...');
      console.log('- Full URL:', window.location.href);
      console.log('- Hash fragment:', hashFragment);
      console.log('- Session ID found:', sessionId);

      if (sessionId) {
        console.log('✅ Found session_id in hash, creating session...');
        // Create session from OAuth redirect
        await createSession(sessionId);
        // Clean URL hash
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
      }

      // Check existing session
      console.log('Checking for existing session...');
      const response = await axios.get(`${API}/auth/me`, {
        withCredentials: true
      });
      console.log('Existing session found:', response.data);
      setUser(response.data);
    } catch (error) {
      console.log('Not authenticated:', error.response?.status);
      setUser(null);
    } finally {
      setAuthLoading(false);
    }
  };

  const createSession = async (sessionId) => {
    try {
      console.log('Creating session with session_id:', sessionId);
      console.log('API endpoint:', `${API}/auth/session`);
      
      const response = await axios.post(
        `${API}/auth/session`,
        {},
        {
          headers: { 'X-Session-ID': sessionId },
          withCredentials: true
        }
      );
      console.log('✅ Session created successfully:', response.data);
      setUser(response.data.user);
      setAuthLoading(false);
    } catch (error) {
      console.error('❌ Session creation failed!');
      console.error('Error object:', error);
      console.error('Response status:', error.response?.status);
      console.error('Response data:', error.response?.data);
      console.error('Error message:', error.message);
      
      let errorMessage = error.response?.data?.detail || error.message || 'Authentication failed';
      
      // Make error more user-friendly
      if (errorMessage.includes('Invalid session') || errorMessage.includes('expired')) {
        errorMessage = 'Authentication session expired. This can happen if the login process takes too long. Please try logging in again.';
      } else if (errorMessage.includes('not authenticated')) {
        errorMessage = 'Authentication failed. Please try logging in again.';
      }
      
      console.error('Showing alert:', errorMessage);
      alert(errorMessage);
      
      setAuthLoading(false);
      setUser(null);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      setUser(null);
      setAnalysis(null);
      setHistory([]);
      setCurrentStep(1);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const loadAnalysis = async (analysisId) => {
    try {
      const response = await axios.get(`${API}/analysis/${analysisId}`, {
        withCredentials: true
      });
      setAnalysis(response.data);
      setCurrentStep(4);
    } catch (error) {
      console.error('Error loading analysis:', error);
      alert('Error loading analysis. Please try again.');
    }
  };

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API}/analysis-history`, {
        withCredentials: true
      });
      setHistory(response.data.history);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const loadExample = () => {
    setFormData({
      product_name: 'Fitness Tracker',
      industry: 'Wearable Technology',
      geography: 'Global',
      target_user: 'Health-conscious consumers, athletes, casual fitness enthusiasts',
      demand_driver: 'Health and wellness trends, preventive healthcare',
      transaction_type: 'One-time Purchase',
      key_metrics: 'Device sales, subscription revenue, user engagement',
      benchmarks: 'Wearable tech market growing at 9.2% CAGR',
      output_format: 'excel'
    });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const nextStep = () => {
    if (currentStep < 3) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const simulateProgress = () => {
    return new Promise((resolve) => {
      let currentStep = 0;
      const steps = analysisProgress.steps;
      
      const updateProgress = () => {
        if (currentStep < steps.length) {
          const step = steps[currentStep];
          const remainingTime = steps.slice(currentStep + 1).reduce((sum, s) => sum + s.duration, 0);
          
          setAnalysisProgress(prev => ({
            ...prev,
            currentStep: currentStep + 1,
            stepName: step.name,
            estimatedTimeLeft: remainingTime + step.duration
          }));
          
          setTimeout(() => {
            currentStep++;
            updateProgress();
          }, step.duration * 1000);
        } else {
          resolve();
        }
      };
      
      updateProgress();
    });
  };

  const analyzeMarket = async () => {
    setIsAnalyzing(true);
    
    // Reset progress
    setAnalysisProgress(prev => ({
      ...prev,
      currentStep: 0,
      stepName: '',
      estimatedTimeLeft: prev.steps.reduce((sum, step) => sum + step.duration, 0)
    }));

    // Start progress simulation (decorative only - don't wait for it)
    simulateProgress();

    try {
      // Make API call independently
      const response = await axios.post(`${API}/analyze-market`, formData, {
        timeout: 300000,  // 300 seconds (5 minutes) timeout for production AI processing
        withCredentials: true
      });
      
      console.log('Market analysis response:', response.data);
      
      // Immediately update state when API completes
      setAnalysis(response.data);
      setCurrentStep(4);
      loadHistory();
      
      // Stop progress simulation
      setAnalysisProgress(prev => ({
        ...prev,
        currentStep: prev.totalSteps,
        stepName: 'Complete!',
        estimatedTimeLeft: 0
      }));

    } catch (error) {
      console.error('Error analyzing market:', error);
      
      // More detailed error handling
      if (error.code === 'ECONNABORTED') {
        alert('Analysis timed out after 2 minutes. This may happen with complex analyses. Please try again - most analyses complete within 2-3 minutes.');
      } else if (error.response) {
        alert(`Server error: ${error.response.status} - ${error.response.data?.detail || 'Unknown error'}`);
      } else if (error.request) {
        alert('Network error: Unable to connect to the server. Please check your connection.');
      } else {
        alert('Error analyzing market. Please try again.');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const exportPersonas = async (analysisId) => {
    try {
      setIsProcessing(true);
      setProcessingMessage('Exporting persona data for Resonate rAI...');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/export-personas/${analysisId}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to export persona data');
      }
      
      const personaData = await response.json();
      
      // Create downloadable JSON file
      const dataStr = JSON.stringify(personaData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `resonate-personas-${personaData.analysis_info.product_name.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      // Show success message with summary
      alert(`✅ Persona Export Complete!\n\nSummary:\n• ${personaData.persona_summary.total_segments} segments exported\n• ${personaData.persona_summary.resonate_ready_segments} Resonate-ready segments\n• ${personaData.persona_summary.total_taxonomy_mappings} taxonomy mappings\n\nReady for Resonate rAI integration!`);
      
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export persona data. Please try again.');
    } finally {
      setIsProcessing(false);
      setProcessingMessage('');
    }
  };

  const exportMarketMap = async () => {
    try {
      console.log('Starting Excel export for analysis:', analysis.market_map.id);
      
      // Show loading message
      const loadingDiv = document.createElement('div');
      loadingDiv.id = 'download-loading';
      loadingDiv.className = 'fixed top-4 right-4 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      loadingDiv.textContent = '⏳ Preparing Excel download...';
      document.body.appendChild(loadingDiv);
      
      const url = `${process.env.REACT_APP_BACKEND_URL}/api/export-market-map/${analysis.market_map.id}`;
      console.log('Fetching from:', url);
      
      const response = await fetch(url);
      console.log('Response status:', response.status, 'OK:', response.ok);
      
      // Remove loading message
      const loading = document.getElementById('download-loading');
      if (loading) loading.remove();
      
      if (response.ok || response.status === 200) {
        const blob = await response.blob();
        console.log('Blob size:', blob.size, 'type:', blob.type);
        
        // Use direct link method (more reliable)
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = `market-map-${analysis.market_input.product_name.replace(/\s+/g, '-').toLowerCase()}.xlsx`;
        a.target = '_blank';
        
        // Try multiple methods to trigger download
        document.body.appendChild(a);
        
        // Method 1: Click
        a.click();
        
        // Method 2: Dispatch event (for some browsers)
        setTimeout(() => {
          const clickEvent = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: false
          });
          a.dispatchEvent(clickEvent);
        }, 100);
        
        // Cleanup after delay
        setTimeout(() => {
          window.URL.revokeObjectURL(downloadUrl);
          document.body.removeChild(a);
        }, 1000);
        
        console.log('Excel download triggered successfully');
        
        // Show detailed success message
        const messageDiv = document.createElement('div');
        messageDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-md';
        messageDiv.innerHTML = `
          <div class="font-bold mb-1">✅ Excel Generated!</div>
          <div class="text-sm">Check your browser's Downloads folder</div>
          <div class="text-xs mt-1 opacity-90">File: market-map-${analysis.market_input.product_name.replace(/\s+/g, '-').toLowerCase()}.xlsx</div>
        `;
        document.body.appendChild(messageDiv);
        setTimeout(() => messageDiv.remove(), 5000);
      } else {
        console.error('Response not OK:', response.status, response.statusText);
        const text = await response.text();
        console.error('Response body:', text);
        alert(`Failed to export Excel: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      const loading = document.getElementById('download-loading');
      if (loading) loading.remove();
      console.error('Export failed:', error);
      alert(`Failed to export market map: ${error.message}`);
    }
  };

  const exportPDF = async () => {
    try {
      console.log('Starting PDF export for analysis:', analysis.market_map.id);
      
      // Show loading message
      const loadingDiv = document.createElement('div');
      loadingDiv.id = 'download-loading';
      loadingDiv.className = 'fixed top-4 right-4 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      loadingDiv.textContent = '⏳ Preparing PDF download...';
      document.body.appendChild(loadingDiv);
      
      const url = `${process.env.REACT_APP_BACKEND_URL}/api/export-pdf/${analysis.market_map.id}`;
      console.log('Fetching from:', url);
      
      const response = await fetch(url);
      console.log('Response status:', response.status, 'OK:', response.ok);
      
      // Remove loading message
      const loading = document.getElementById('download-loading');
      if (loading) loading.remove();
      
      if (response.ok || response.status === 200) {
        const blob = await response.blob();
        console.log('Blob size:', blob.size, 'type:', blob.type);
        
        // Use direct link method (more reliable)
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = `BCM-Market-Report-${analysis.market_input.product_name.replace(/\s+/g, '-')}.pdf`;
        a.target = '_blank';
        
        // Try multiple methods to trigger download
        document.body.appendChild(a);
        
        // Method 1: Click
        a.click();
        
        // Method 2: Dispatch event (for some browsers)
        setTimeout(() => {
          const clickEvent = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: false
          });
          a.dispatchEvent(clickEvent);
        }, 100);
        
        // Cleanup after delay
        setTimeout(() => {
          window.URL.revokeObjectURL(downloadUrl);
          document.body.removeChild(a);
        }, 1000);
        
        console.log('PDF download triggered successfully');
        
        // Show detailed success message
        const messageDiv = document.createElement('div');
        messageDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-md';
        messageDiv.innerHTML = `
          <div class="font-bold mb-1">✅ PDF Generated!</div>
          <div class="text-sm">Check your browser's Downloads folder</div>
          <div class="text-xs mt-1 opacity-90">File: BCM-Market-Report-${analysis.market_input.product_name.replace(/\s+/g, '-')}.pdf</div>
        `;
        document.body.appendChild(messageDiv);
        setTimeout(() => messageDiv.remove(), 5000);
      } else {
        console.error('Response not OK:', response.status, response.statusText);
        const text = await response.text();
        console.error('Response body:', text);
        alert(`Failed to export PDF: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      const loading = document.getElementById('download-loading');
      if (loading) loading.remove();
      console.error('PDF export failed:', error);
      alert(`Failed to export PDF report: ${error.message}`);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value);
  };

  const getCompanyLogo = (companyName) => {
    // Enhanced logo mapping with better fallbacks and direct links
    const logoMap = {
      // Technology Companies
      'Apple': 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg',
      'Google': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
      'Microsoft': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg',
      'Samsung': 'https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg',
      'Amazon': 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
      'Meta': 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg',
      'IBM': 'https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg',
      'Oracle': 'https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg',
      'Salesforce': 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg',
      
      // Financial Services
      'JPMorgan Chase': 'https://upload.wikimedia.org/wikipedia/commons/4/44/JPMorgan_Chase_logo.svg',
      'Goldman Sachs': 'https://upload.wikimedia.org/wikipedia/commons/6/61/Goldman_Sachs.svg',
      'Morgan Stanley': 'https://upload.wikimedia.org/wikipedia/commons/1/12/Morgan_Stanley_Logo_1.svg',
      'Bank of America': 'https://upload.wikimedia.org/wikipedia/commons/4/47/Bank_of_America_logo.svg',
      'Wells Fargo': 'https://upload.wikimedia.org/wikipedia/commons/b/b3/Wells_Fargo_Bank.svg',
      'Citi': 'https://upload.wikimedia.org/wikipedia/commons/1/1c/Citi.svg',
      'DTCC': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/DTCC_logo.svg/320px-DTCC_logo.svg.png',
      'Clearstream': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%2300529C"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E',
      'Euroclear': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%230066CC"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E',
      
      // Payment Services
      'PayPal': 'https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg',
      'Stripe': 'https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg',
      'Square': 'https://upload.wikimedia.org/wikipedia/commons/6/64/Square%2C_Inc._logo.svg',
      'Visa': 'https://upload.wikimedia.org/wikipedia/commons/5/5e/Visa_Inc._logo.svg',
      'Mastercard': 'https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg',
      
      // Fitness & Wearables
      'Fitbit': 'https://upload.wikimedia.org/wikipedia/commons/3/33/Fitbit_logo16.svg',
      'Garmin': 'https://upload.wikimedia.org/wikipedia/commons/5/53/Garmin_logo.svg',
      'Xiaomi': 'https://upload.wikimedia.org/wikipedia/commons/2/29/Xiaomi_logo.svg',
      
      // Food & Beverage
      'Starbucks': 'https://upload.wikimedia.org/wikipedia/en/d/d3/Starbucks_Corporation_Logo_2011.svg',
      'McDonald\'s': 'https://upload.wikimedia.org/wikipedia/commons/3/36/McDonald%27s_Golden_Arches.svg',
      'Coca-Cola': 'https://upload.wikimedia.org/wikipedia/commons/c/ce/Coca-Cola_logo.svg',
      'Sierra Nevada': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23228B22"%3E%3Cpath d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/%3E%3C/svg%3E',
      'Stone Brewing': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23654321"%3E%3Cpath d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/%3E%3C/svg%3E',
      
      // SaaS/Software
      'Asana': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/Asana_logo.svg',
      'Slack': 'https://upload.wikimedia.org/wikipedia/commons/7/76/Slack_Icon.png',
      'Zoom': 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Zoom_Communications_Logo.svg',
      'HubSpot': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23FF7A59"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E',
      
      // Electric Vehicle/Energy
      'Tesla': 'https://upload.wikimedia.org/wikipedia/commons/b/bb/Tesla_T_symbol.svg',
      'ChargePoint': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%230099CC"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E',
      'EVgo': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%2300B04F"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E',
      
      // Food Delivery
      'DoorDash': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23FF3008"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E',
      'Uber Eats': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23000000"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E',
      'Grubhub': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23F63440"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/%3E%3C/svg%3E'
    };

    // Return specific logo if mapped, otherwise return a default business icon
    return logoMap[companyName] || "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='%23374151'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z'/%3E%3C/svg%3E";
  };

  const resetForm = () => {
    setFormData({
      product_name: '',
      industry: '',
      geography: '',
      target_user: '',
      demand_driver: '',
      transaction_type: '',
      key_metrics: '',
      benchmarks: '',
      output_format: 'excel'
    });
    setAnalysis(null);
    setCurrentStep(1);
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!user) {
    return <Login />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Admin Panel Modal */}
      {showAdminPanel && (
        <AdminPanel user={user} onClose={() => setShowAdminPanel(false)} />
      )}

      {/* Orange Header Stripe */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="w-12 h-12 flex items-center justify-center mr-4">
                <img 
                  src="https://www.beebyclarkmeyler.com/hs-fs/hubfs/BCM_2024_Logo_Update_White.png?width=2550&height=3300&name=BCM_2024_Logo_Update_White.png" 
                  alt="BCM Logo" 
                  className="w-full h-full object-contain"
                />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Market Map Generator</h1>
                <p className="text-white text-opacity-90 text-sm">AI-Powered Comprehensive Market Intelligence</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {currentStep === 4 && (
                <button
                  onClick={resetForm}
                  className="bg-white text-orange-600 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  New Analysis
                </button>
              )}
              
              {/* Admin Panel Button */}
              {user.is_admin && (
                <button
                  onClick={() => setShowAdminPanel(true)}
                  className="bg-white bg-opacity-20 text-white px-4 py-2 rounded-lg font-semibold hover:bg-opacity-30 transition-colors flex items-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  <span>Admin Panel</span>
                </button>
              )}
              
              {/* User Menu */}
              <div className="flex items-center space-x-3 bg-white bg-opacity-20 rounded-lg px-4 py-2">
                {user.picture ? (
                  <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-white text-orange-600 flex items-center justify-center font-semibold">
                    {user.name.charAt(0)}
                  </div>
                )}
                <div className="text-white">
                  <div className="text-sm font-medium">{user.name}</div>
                  <div className="text-xs opacity-90">{user.email}</div>
                </div>
                <button
                  onClick={handleLogout}
                  className="ml-2 text-white hover:text-gray-200 transition-colors"
                  title="Logout"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        {currentStep < 4 && (
          <div className="bg-white rounded-lg shadow-md p-8">
            {/* Progress Bar */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                {[1, 2, 3].map((step) => (
                  <div key={step} className="flex items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                      currentStep >= step ? 'bg-orange-500 text-white' : 'bg-gray-300 text-gray-600'
                    }`}>
                      {step}
                    </div>
                    {step < 3 && (
                      <div className={`w-24 h-1 mx-4 rounded ${
                        currentStep > step ? 'bg-orange-500' : 'bg-gray-300'
                      }`} />
                    )}
                  </div>
                ))}
              </div>
              <div className="flex justify-between mt-3 text-sm font-medium">
                <span className={currentStep >= 1 ? 'text-orange-600' : 'text-gray-500'}>Product Definition</span>
                <span className={currentStep >= 2 ? 'text-orange-600' : 'text-gray-500'}>Market Context</span>
                <span className={currentStep >= 3 ? 'text-orange-600' : 'text-gray-500'}>Analysis Setup</span>
              </div>
            </div>

            {/* Example Button */}
            {currentStep === 1 && (
              <div className="mb-8 p-6 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Try an Example</h3>
                    <p className="text-gray-600">Load the fitness tracker example to see comprehensive market mapping</p>
                  </div>
                  <button
                    onClick={loadExample}
                    className="bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-orange-600 transition-colors"
                  >
                    Load Fitness Tracker Example
                  </button>
                </div>
              </div>
            )}

            {/* Step 1: Product Definition */}
            {currentStep === 1 && (
              <div className="space-y-8">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold mb-3 text-gray-900">Define Your Product</h2>
                  <div className="w-24 h-1 bg-orange-500 mx-auto"></div>
                  <p className="text-lg text-gray-600 max-w-2xl mx-auto mt-4">
                    Tell us about your product to generate comprehensive market intelligence
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Product/Service Name *
                    </label>
                    <input
                      type="text"
                      value={formData.product_name}
                      onChange={(e) => handleInputChange('product_name', e.target.value)}
                      placeholder="e.g., Fitness Tracker"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Industry *
                    </label>
                    <input
                      type="text"
                      value={formData.industry}
                      onChange={(e) => handleInputChange('industry', e.target.value)}
                      placeholder="e.g., Wearable Technology"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Geography *
                    </label>
                    <input
                      type="text"
                      value={formData.geography}
                      onChange={(e) => handleInputChange('geography', e.target.value)}
                      placeholder="e.g., Global, United States, Europe"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Target Users *
                    </label>
                    <textarea
                      value={formData.target_user}
                      onChange={(e) => handleInputChange('target_user', e.target.value)}
                      placeholder="e.g., Health-conscious consumers, athletes, casual fitness enthusiasts"
                      rows={2}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Market Context */}
            {currentStep === 2 && (
              <div className="space-y-8">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold mb-3 text-gray-900">Market Context</h2>
                  <div className="w-24 h-1 bg-orange-500 mx-auto"></div>
                  <p className="text-lg text-gray-600 max-w-2xl mx-auto mt-4">
                    Help us understand your market dynamics and business model
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Primary Market Drivers *
                    </label>
                    <textarea
                      value={formData.demand_driver}
                      onChange={(e) => handleInputChange('demand_driver', e.target.value)}
                      placeholder="e.g., Health and wellness trends, preventive healthcare, aging population"
                      rows={2}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Revenue Model *
                    </label>
                    <select
                      value={formData.transaction_type}
                      onChange={(e) => handleInputChange('transaction_type', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    >
                      <option value="">Select revenue model...</option>
                      <option value="One-time Purchase">One-time Purchase</option>
                      <option value="Subscription">Subscription</option>
                      <option value="Freemium">Freemium</option>
                      <option value="Usage-based">Usage-based</option>
                      <option value="Commission-based">Commission-based</option>
                      <option value="Advertising">Advertising</option>
                    </select>
                  </div>

                  <div className="md:col-span-2 space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Key Performance Metrics *
                    </label>
                    <textarea
                      value={formData.key_metrics}
                      onChange={(e) => handleInputChange('key_metrics', e.target.value)}
                      placeholder="e.g., Device sales, subscription revenue, user engagement, retention rate"
                      rows={2}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Analysis Setup */}
            {currentStep === 3 && (
              <div className="space-y-8">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold mb-3 text-gray-900">Analysis Configuration</h2>
                  <div className="w-24 h-1 bg-orange-500 mx-auto"></div>
                  <p className="text-lg text-gray-600 max-w-2xl mx-auto mt-4">
                    Add any known market data to enhance the analysis accuracy
                  </p>
                </div>

                <div className="space-y-6 max-w-4xl mx-auto">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Known Market Benchmarks (Optional)
                    </label>
                    <textarea
                      value={formData.benchmarks}
                      onChange={(e) => handleInputChange('benchmarks', e.target.value)}
                      placeholder="e.g., Wearable tech market growing at 9.2% CAGR, $97.4B global market size"
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>

                  {/* Review Summary */}
                  <div className="bg-gray-50 p-6 rounded-lg border">
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">Market Analysis Summary</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span className="font-medium text-gray-600">Product:</span>
                        <span className="text-gray-900">{formData.product_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium text-gray-600">Industry:</span>
                        <span className="text-gray-900">{formData.industry}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium text-gray-600">Geography:</span>
                        <span className="text-gray-900">{formData.geography}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium text-gray-600">Revenue Model:</span>
                        <span className="text-gray-900">{formData.transaction_type}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-12 pt-6 border-t border-gray-200">
              {/* Back Button - Hidden during analysis */}
              {!isAnalyzing && (
                <button
                  onClick={prevStep}
                  disabled={currentStep === 1}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Back
                </button>
              )}

              {/* Subtle back option during analysis */}
              {isAnalyzing && (
                <div className="flex items-center">
                  <button
                    onClick={() => {
                      if (window.confirm('Are you sure you want to cancel the analysis? This will stop the current process.')) {
                        setIsAnalyzing(false);
                        setAnalysisProgress(prev => ({
                          ...prev,
                          currentStep: 0,
                          stepName: '',
                          estimatedTimeLeft: 0
                        }));
                      }
                    }}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                  >
                    Cancel Analysis
                  </button>
                </div>
              )}

              {currentStep < 3 ? (
                <button
                  onClick={nextStep}
                  disabled={currentStep === 1 && !formData.product_name}
                  className="bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              ) : (
                <div className="flex flex-col items-end">
                  <button
                    onClick={analyzeMarket}
                    disabled={isAnalyzing || !formData.product_name}
                    className="bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {isAnalyzing ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span className="font-medium">Generating Market Map...</span>
                      </>
                    ) : (
                      'Generate Market Map'
                    )}
                  </button>

                  {/* Progress Indicator - Full Width Prominent Modal */}
                  {isAnalyzing && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                      <div className="bg-white p-8 rounded-xl shadow-2xl border-2 border-orange-200 w-full max-w-3xl">
                        <div className="text-center mb-6">
                          <h4 className="text-2xl font-bold text-gray-900 mb-2">Market Analysis in Progress</h4>
                          <p className="text-base text-gray-600">
                            Step {analysisProgress.currentStep} of {analysisProgress.totalSteps}
                          </p>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-gray-200 rounded-full h-4 mb-6">
                          <div
                            className="bg-gradient-to-r from-orange-500 to-orange-600 h-4 rounded-full transition-all duration-500 ease-out"
                            style={{ width: `${(analysisProgress.currentStep / analysisProgress.totalSteps) * 100}%` }}
                          ></div>
                        </div>

                        {/* Current Step */}
                        <div className="text-center mb-6">
                          <div className="text-lg font-semibold text-gray-900 mb-2">
                            {analysisProgress.stepName || 'Initializing...'}
                          </div>
                          {analysisProgress.estimatedTimeLeft > 0 && (
                            <div className="text-sm text-gray-600">
                              Estimated time remaining: {analysisProgress.estimatedTimeLeft} seconds
                            </div>
                          )}
                        </div>

                        {/* Steps List */}
                        <div className="space-y-3 mb-6">
                          {analysisProgress.steps.map((step, index) => (
                            <div key={index} className={`flex items-center text-sm ${
                              index < analysisProgress.currentStep ? 'text-green-600' :
                              index === analysisProgress.currentStep - 1 ? 'text-orange-600' :
                              'text-gray-400'
                            }`}>
                              <div className={`w-5 h-5 rounded-full mr-3 flex items-center justify-center ${
                                index < analysisProgress.currentStep ? 'bg-green-600' :
                                index === analysisProgress.currentStep - 1 ? 'bg-orange-600' :
                                'bg-gray-200'
                              }`}>
                                {index < analysisProgress.currentStep ? (
                                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                ) : index === analysisProgress.currentStep - 1 ? (
                                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                                ) : (
                                  <div className="w-2 h-2 bg-white rounded-full"></div>
                                )}
                              </div>
                              <span className="font-medium">{step.name}</span>
                            </div>
                          ))}
                        </div>

                        {/* Cancel Button - Prominent Red Button */}
                        <div className="mt-8 pt-6 border-t-2 border-gray-200 flex justify-center">
                          <button
                            onClick={() => {
                              if (window.confirm('Are you sure you want to cancel the analysis? This will stop the current process.')) {
                                setIsAnalyzing(false);
                                setAnalysisProgress(prev => ({
                                  ...prev,
                                  currentStep: 0,
                                  stepName: '',
                                  estimatedTimeLeft: 0
                                }));
                              }
                            }}
                            className="px-8 py-3 bg-red-500 text-white rounded-lg text-base font-semibold hover:bg-red-600 transition-colors shadow-lg hover:shadow-xl flex items-center space-x-2"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            <span>Cancel Analysis</span>
                          </button>
                        </div>

                        {/* Help text */}
                        <div className="mt-6">
                          <p className="text-sm text-gray-500 text-center">
                            Powered by Kimi K2 • Please wait while we generate your comprehensive market analysis...
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Results Step - Market Map */}
        {currentStep === 4 && analysis && (
          <div className="space-y-8">
            {/* Market Map Header */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <div className="text-center mb-6">
                <h2 className="text-4xl font-bold text-gray-900 mb-2">Market Map: {analysis.market_input.product_name}</h2>
                <div className="w-24 h-1 bg-orange-500 mx-auto"></div>
                <p className="text-lg text-gray-600 mt-4">{analysis.market_input.geography} • {analysis.market_input.industry}</p>
                
                <div className="flex justify-center space-x-6 mt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-500">{formatCurrency(analysis.market_map.total_market_size)}</div>
                    <div className="text-sm text-gray-600">Total Market Size</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{(analysis.market_map.market_growth_rate * 100).toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Annual Growth Rate</div>
                  </div>
                  <div className={`text-center px-4 py-2 rounded-full text-sm font-semibold ${
                    analysis.market_map.confidence_level === 'high' ? 'bg-green-100 text-green-800' :
                    analysis.market_map.confidence_level === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {analysis.market_map.confidence_level.toUpperCase()} CONFIDENCE
                  </div>
                </div>
              </div>
            </div>

            {/* Executive Summary Section - Moved to Top */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg p-8 border border-blue-100">
              <div className="text-center mb-8">
                <h3 className="text-3xl font-bold text-gray-900 mb-3">Executive Summary</h3>
                <div className="w-24 h-1 bg-blue-500 mx-auto"></div>
                <p className="text-gray-600 mt-3">Strategic Overview and Key Insights</p>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                {/* Key Market Metrics */}
                <div className="bg-white rounded-lg p-6 shadow-sm border">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <span className="w-3 h-3 bg-blue-500 rounded-full mr-3"></span>
                    Market Opportunity
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total Market Size:</span>
                      <span className="font-semibold text-blue-600">{formatCurrency(analysis.market_map.total_market_size)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Growth Rate:</span>
                      <span className="font-semibold text-green-600">{(analysis.market_map.market_growth_rate * 100).toFixed(1)}% CAGR</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Serviceable Market:</span>
                      <span className="font-semibold text-orange-600">{formatCurrency(analysis.market_map.total_market_size * 0.3)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Target Revenue:</span>
                      <span className="font-semibold text-purple-600">{formatCurrency(analysis.market_map.total_market_size * 0.03)}</span>
                    </div>
                  </div>
                </div>

                {/* Competitive Landscape */}
                <div className="bg-white rounded-lg p-6 shadow-sm border">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <span className="w-3 h-3 bg-orange-500 rounded-full mr-3"></span>
                    Competitive Dynamics
                  </h4>
                  <div className="space-y-3">
                    {analysis.market_map.competitors.slice(0, 4).map((competitor, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-700 font-medium">{competitor.name}</span>
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {competitor.market_share ? `${(competitor.market_share * 100).toFixed(0)}%` : 'N/A'}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-600">
                      Market features {analysis.market_map.competitors.length} key players with opportunities for differentiation
                    </p>
                  </div>
                </div>

                {/* Strategic Priorities */}
                <div className="bg-white rounded-lg p-6 shadow-sm border">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <span className="w-3 h-3 bg-green-500 rounded-full mr-3"></span>
                    Key Drivers & Trends
                  </h4>
                  <div className="space-y-3">
                    {analysis.market_map.key_drivers.slice(0, 4).map((driver, index) => (
                      <div key={index} className="flex items-start">
                        <span className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                        <span className="text-sm text-gray-700">{driver}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-600">
                      Primary growth driven by {analysis.market_input.demand_driver}
                    </p>
                  </div>
                </div>
              </div>

              {/* Detailed Executive Summary Text */}
              {analysis.market_map && analysis.market_map.executive_summary ? (
                <div className="bg-white rounded-lg p-8 shadow-sm border">
                  <div className="prose prose-lg max-w-none">
                    <div className="text-gray-700 leading-relaxed whitespace-pre-line text-base">
                      {analysis.market_map.executive_summary}
                    </div>
                  </div>
                  
                  {/* Analysis Metadata */}
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-600">Analysis Date:</span>
                        <span className="ml-2 text-gray-700">
                          {new Date(analysis.market_map.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-600">Confidence Level:</span>
                        <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                          analysis.market_map.confidence_level === 'high' ? 'bg-green-100 text-green-700' :
                          analysis.market_map.confidence_level === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {analysis.market_map.confidence_level.toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-600">Data Sources:</span>
                        <div className="ml-2 space-y-1">
                          {analysis.market_map.data_sources.map((source, index) => (
                            <div key={index}>
                              {source.url ? (
                                <a 
                                  href={source.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:text-blue-800 underline text-xs"
                                >
                                  {source.name}
                                </a>
                              ) : (
                                <span className="text-gray-700 text-xs">{source}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg p-8 shadow-sm border">
                  <div className="text-gray-600 italic text-center py-8">
                    Executive summary will be generated with the market analysis
                  </div>
                </div>
              )}
            </div>

            {/* TAM → SAM → SOM Visual Chart - Moved after Executive Summary */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">Market Size Analysis</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                {/* Left side - Detailed Analytical Descriptions */}
                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="w-4 h-4 bg-blue-900 rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <h4 className="text-lg font-bold text-blue-900 mb-2">TAM - {formatCurrency(analysis.market_map.total_market_size)}</h4>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        <strong>Total Addressable Market:</strong> Represents 100% of global revenue opportunity for {analysis.market_input.product_name}{' '}
                        across all customer segments in {analysis.market_input.geography}. Based on{' '}
                        {analysis.market_map.data_sources.slice(0, 3).map((source, idx) => {
                          const sourceMapping = {
                            "Gartner Market Research": "https://www.gartner.com/en/research",
                            "McKinsey Industry Reports": "https://www.mckinsey.com/industries",
                            "IBISWorld Market Analysis": "https://www.ibisworld.com",
                            "Forrester Research": "https://www.forrester.com/research",
                            "PwC Industry Insights": "https://www.pwc.com/us/en/industries.html",
                            "Statista": "https://www.statista.com",
                            "CB Insights": "https://www.cbinsights.com"
                          };
                          
                          const sourceName = typeof source === 'string' ? source : source.name;
                          const sourceUrl = typeof source === 'object' && source.url ? source.url : sourceMapping[sourceName];
                          
                          return (
                            <span key={idx}>
                              {idx > 0 && (idx === analysis.market_map.data_sources.slice(0, 3).length - 1 ? ' and ' : ', ')}
                              {sourceUrl ? (
                                <a 
                                  href={sourceUrl} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:text-blue-800 underline"
                                  title={`Visit ${sourceName}`}
                                >
                                  {sourceName}
                                </a>
                              ) : (
                                <span>{sourceName}</span>
                              )}
                              <sup className="text-blue-600">[{idx + 1}]</sup>
                            </span>
                          );
                        })}
                        {' '}data, growing at {(analysis.market_map.market_growth_rate * 100).toFixed(1)}% CAGR driven by {analysis.market_map.key_drivers.slice(0,2).join(' and ')}.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-4 h-4 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <h4 className="text-lg font-bold text-blue-600 mb-2">SAM - {formatCurrency(analysis.market_map.total_market_size * 0.3)}</h4>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        <strong>Serviceable Addressable Market:</strong> 30% of TAM ({formatCurrency(analysis.market_map.total_market_size * 0.3)}){' '}
                        representing segments we can realistically serve with our {analysis.market_input.transaction_type} business model.{' '}
                        Focused on {analysis.market_input.target_user} who prioritize {analysis.market_input.key_metrics.split(',')[0]}{' '}
                        and are motivated by {analysis.market_input.demand_driver}.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-4 h-4 bg-blue-300 rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <h4 className="text-lg font-bold text-blue-300 mb-2">SOM - {formatCurrency(analysis.market_map.total_market_size * 0.03)}</h4>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        <strong>Serviceable Obtainable Market:</strong> 10% of SAM ({formatCurrency(analysis.market_map.total_market_size * 0.03)}){' '}
                        based on realistic 3-5 year market penetration assuming competitive response from {analysis.market_map.competitors.slice(0,2).map(c => c.name).join(' and ')}.{' '}
                        Achievable through {analysis.market_map.strategic_recommendations.slice(0,1)[0]?.toLowerCase() || 'focused market strategy'}.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Right side - Concentric Circles Visualization with Better Labels and Arrows */}
                <div className="flex justify-center relative">
                  <div className="relative w-80 h-80">
                    {/* TAM - Outer Circle */}
                    <div className="absolute inset-0 w-80 h-80 bg-blue-900 rounded-full flex items-center justify-center">
                      <div className="text-white text-center">
                        <div className="text-xl font-bold">{formatCurrency(analysis.market_map.total_market_size)}</div>
                        <div className="text-sm font-medium">TAM</div>
                      </div>
                    </div>
                      
                    {/* SAM - Middle Circle - Properly centered */}
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-56 h-56 bg-blue-600 rounded-full flex items-center justify-center">
                      <div className="text-white text-center">
                        <div className="text-lg font-bold">{formatCurrency(analysis.market_map.total_market_size * 0.3)}</div>
                        <div className="text-sm font-medium">SAM</div>
                      </div>
                    </div>
                        
                    {/* SOM - Inner Circle - Properly centered */}
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-blue-300 rounded-full flex items-center justify-center">
                      <div className="text-white text-center">
                        <div className="text-base font-bold">{formatCurrency(analysis.market_map.total_market_size * 0.03)}</div>
                        <div className="text-xs font-medium">SOM</div>
                      </div>
                    </div>
                    
                    {/* Simple labeling: TAM top, SAM right, SOM in center */}
                    
                    {/* TAM - Above pointing to outermost circle */}
                    <div className="absolute -top-12 left-1/2 transform -translate-x-1/2">
                      <div className="flex flex-col items-center">
                        <div className="text-sm font-semibold text-gray-700 mb-2">TAM</div>
                        <div className="w-0 h-0 border-l-3 border-r-3 border-t-4 border-transparent border-t-gray-500"></div>
                      </div>
                    </div>
                    
                    {/* SAM - Right side pointing to middle circle */}
                    <div className="absolute top-1/2 -right-12 transform -translate-y-1/2">
                      <div className="flex items-center">
                        <div className="text-sm font-semibold text-gray-700 mr-2">SAM</div>
                        <div className="w-0 h-0 border-t-3 border-b-3 border-l-4 border-transparent border-l-gray-500"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Detailed Market Analysis Summary */}
              <div className="mt-8 p-6 bg-gray-50 rounded-lg">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Market Sizing Methodology & Assumptions</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-white rounded-lg">
                    <div className="text-2xl font-bold text-blue-900 mb-2">{formatCurrency(analysis.market_map.total_market_size)}</div>
                    <div className="text-sm font-semibold text-gray-700 mb-2">Total Addressable Market</div>
                    <div className="text-xs text-gray-600 leading-relaxed">
                      100% market opportunity based on {analysis.market_map.methodology}. 
                      Growth rate: {(analysis.market_map.market_growth_rate * 100).toFixed(1)}% CAGR.
                      Confidence: {analysis.market_map.confidence_level}.
                    </div>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg">
                    <div className="text-2xl font-bold text-blue-600 mb-2">{formatCurrency(analysis.market_map.total_market_size * 0.3)}</div>
                    <div className="text-sm font-semibold text-gray-700 mb-2">Serviceable Addressable Market</div>
                    <div className="text-xs text-gray-600 leading-relaxed">
                      30% of TAM filtering for {analysis.market_input.target_user} segments compatible with 
                      {analysis.market_input.transaction_type} model and {analysis.market_input.key_metrics.split(',')[0]} requirements.
                    </div>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg">
                    <div className="text-2xl font-bold text-blue-300 mb-2">{formatCurrency(analysis.market_map.total_market_size * 0.03)}</div>
                    <div className="text-sm font-semibold text-gray-700 mb-2">Serviceable Obtainable Market</div>
                    <div className="text-xs text-gray-600 leading-relaxed">
                      10% of SAM assuming competitive market with established players 
                      ({analysis.market_map.competitors.slice(0,2).map(c => c.name).join(', ')}) and 3-5 year penetration timeline.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Visual Market Map */}
            {analysis.visual_map && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">{analysis.visual_map.title}</h3>
                
                {/* Market Segmentation Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Geographic Segmentation */}
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <div className="text-center mb-6">
                      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 mb-3">
                        <FaGlobe className="text-2xl text-blue-600" />
                      </div>
                      <h4 className="text-lg font-bold text-gray-900">Geographic Segmentation</h4>
                      <div className="w-16 h-1 bg-blue-500 mx-auto mt-2"></div>
                      <p className="text-xs text-gray-600 mt-2">Country, City, Density, Language, Climate, Area, Population</p>
                    </div>
                    
                    <div className="space-y-4">
                      {analysis.visual_map.geographic_segments && analysis.visual_map.geographic_segments.map((segment, index) => (
                        <div key={index} className="bg-white p-4 rounded-lg border">
                          <div className="flex items-center mb-2">
                            <span className="text-xl mr-3">{segment.icon}</span>
                            <div className="flex-1">
                              <div className="font-semibold text-gray-900">{segment.name}</div>
                              <div className="text-sm text-gray-600">{segment.description}</div>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-xs mt-3">
                            <div className="flex justify-between">
                              <span className="font-medium">Market Size:</span>
                              <span className="text-blue-600 font-semibold">{formatCurrency(segment.size)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="font-medium">Growth:</span>
                              <span className="text-green-600 font-semibold">{(segment.growth * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                          {segment.key_players && segment.key_players.length > 0 && (
                            <div className="mt-2">
                              <div className="text-xs font-medium text-gray-600 mb-1">Key Players:</div>
                              <div className="flex flex-wrap gap-1">
                                {segment.key_players.slice(0, 3).map((player, i) => (
                                  <span key={i} className="inline-flex items-center bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                                    <span className="mr-1">{getCompanyIcon(player)}</span>
                                    {player}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Demographic Segmentation */}
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <div className="text-center mb-6">
                      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-orange-100 mb-3">
                        <FaUsers className="text-2xl text-orange-600" />
                      </div>
                      <h4 className="text-lg font-bold text-gray-900">Demographic Segmentation</h4>
                      <div className="w-16 h-1 bg-orange-500 mx-auto mt-2"></div>
                      <p className="text-xs text-gray-600 mt-2">Age, Gender, Income, Education, Social Status, Family, Life Stage, Occupation</p>
                    </div>
                    
                    <div className="space-y-4">
                      {analysis.visual_map.demographic_segments && analysis.visual_map.demographic_segments.map((segment, index) => (
                        <div key={index} className="bg-white p-4 rounded-lg border">
                          <div className="flex items-center mb-2">
                            <span className="text-xl mr-3">{segment.icon}</span>
                            <div className="flex-1">
                              <div className="font-semibold text-gray-900">{segment.name}</div>
                              <div className="text-sm text-gray-600">{segment.description}</div>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-xs mt-3">
                            <div className="flex justify-between">
                              <span className="font-medium">Market Size:</span>
                              <span className="text-orange-600 font-semibold">{formatCurrency(segment.size)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="font-medium">Growth:</span>
                              <span className="text-green-600 font-semibold">{(segment.growth * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                          {segment.key_players && segment.key_players.length > 0 && (
                            <div className="mt-2">
                              <div className="text-xs font-medium text-gray-600 mb-1">Key Players:</div>
                              <div className="flex flex-wrap gap-1">
                                {segment.key_players.slice(0, 3).map((player, i) => (
                                  <span key={i} className="inline-flex items-center bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                                    <span className="mr-1">{getCompanyIcon(player)}</span>
                                    {player}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Psychographic Segmentation */}
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <div className="text-center mb-6">
                      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-yellow-100 mb-3">
                        <FaBrain className="text-2xl text-yellow-600" />
                      </div>
                      <h4 className="text-lg font-bold text-gray-900">Psychographic Segmentation</h4>
                      <div className="w-16 h-1 bg-yellow-500 mx-auto mt-2"></div>
                      <p className="text-xs text-gray-600 mt-2">Lifestyle, AIO (Activity/Interest/Opinion), Concerns, Personality, Values, Attitudes</p>
                    </div>
                    
                    <div className="space-y-4">
                      {analysis.visual_map.psychographic_segments && analysis.visual_map.psychographic_segments.map((segment, index) => (
                        <div key={index} className="bg-white p-4 rounded-lg border">
                          <div className="flex items-center mb-2">
                            <span className="text-xl mr-3">{segment.icon}</span>
                            <div className="flex-1">
                              <div className="font-semibold text-gray-900">{segment.name}</div>
                              <div className="text-sm text-gray-600">{segment.description}</div>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-xs mt-3">
                            <div className="flex justify-between">
                              <span className="font-medium">Market Size:</span>
                              <span className="text-yellow-600 font-semibold">{formatCurrency(segment.size)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="font-medium">Growth:</span>
                              <span className="text-green-600 font-semibold">{(segment.growth * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                          {segment.key_players && segment.key_players.length > 0 && (
                            <div className="mt-2">
                              <div className="text-xs font-medium text-gray-600 mb-1">Key Players:</div>
                              <div className="flex flex-wrap gap-1">
                                {segment.key_players.slice(0, 3).map((player, i) => (
                                  <span key={i} className="inline-flex items-center bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                                    <span className="mr-1">{getCompanyIcon(player)}</span>
                                    {player}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Behavioral Segmentation */}
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <div className="text-center mb-6">
                      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-100 mb-3">
                        <FaShoppingCart className="text-2xl text-purple-600" />
                      </div>
                      <h4 className="text-lg font-bold text-gray-900">Behavioral Segmentation</h4>
                      <div className="w-16 h-1 bg-purple-500 mx-auto mt-2"></div>
                      <p className="text-xs text-gray-600 mt-2">Purchase, Usage, Intent, Occasion, Buyer Stage, Life Cycle Stage, Engagement</p>
                    </div>
                    
                    <div className="space-y-4">
                      {analysis.visual_map.behavioral_segments && analysis.visual_map.behavioral_segments.map((segment, index) => (
                        <div key={index} className="bg-white p-4 rounded-lg border">
                          <div className="flex items-center mb-2">
                            <span className="text-xl mr-3">{segment.icon}</span>
                            <div className="flex-1">
                              <div className="font-semibold text-gray-900">{segment.name}</div>
                              <div className="text-sm text-gray-600">{segment.description}</div>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-xs mt-3">
                            <div className="flex justify-between">
                              <span className="font-medium">Market Size:</span>
                              <span className="text-purple-600 font-semibold">{formatCurrency(segment.size)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="font-medium">Growth:</span>
                              <span className="text-green-600 font-semibold">{(segment.growth * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                          {segment.key_players && segment.key_players.length > 0 && (
                            <div className="mt-2">
                              <div className="text-xs font-medium text-gray-600 mb-1">Key Players:</div>
                              <div className="flex flex-wrap gap-1">
                                {segment.key_players.slice(0, 3).map((player, i) => (
                                  <span key={i} className="inline-flex items-center bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                                    <span className="mr-1">{getCompanyIcon(player)}</span>
                                    {player}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Firmographic Segmentation - B2B Only */}
                {analysis.market_map.segmentation_by_firmographics && analysis.market_map.segmentation_by_firmographics.length > 0 && (
                  <div className="mt-8">
                    <h4 className="text-xl font-bold text-gray-900 mb-6 text-center">B2B Firmographic Segmentation</h4>
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <div className="text-center mb-6">
                        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-teal-100 mb-3">
                          <FaBuilding className="text-2xl text-teal-600" />
                        </div>
                        <h4 className="text-lg font-bold text-gray-900">Firmographic Segmentation</h4>
                        <div className="w-16 h-1 bg-teal-500 mx-auto mt-2"></div>
                        <p className="text-xs text-gray-600 mt-2">Industry, Company Size, Geographic Location, Job Titles/Roles, Company Revenue</p>
                      </div>
                      
                      <div className="space-y-4">
                        {analysis.market_map.segmentation_by_firmographics.map((segment, index) => (
                          <div key={index} className="bg-white p-4 rounded-lg border">
                            <div className="flex items-center mb-2">
                              <FaBuilding className="text-xl mr-3 text-teal-600" />
                              <div className="flex-1">
                                <div className="font-semibold text-gray-900">{segment.name}</div>
                                <div className="text-sm text-gray-600">{segment.description}</div>
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs mt-3">
                              <div className="flex justify-between">
                                <span className="font-medium">Market Size:</span>
                                <span className="text-teal-600 font-semibold">{formatCurrency(segment.size_estimate)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="font-medium">Growth:</span>
                                <span className="text-green-600 font-semibold">{(segment.growth_rate * 100).toFixed(1)}%</span>
                              </div>
                            </div>
                            {segment.key_players && segment.key_players.length > 0 && (
                              <div className="mt-2">
                                <div className="text-xs font-medium text-gray-600 mb-1">Key Players:</div>
                                <div className="flex flex-wrap gap-1">
                                  {segment.key_players.slice(0, 3).map((player, i) => (
                                    <span key={i} className="inline-flex items-center bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                                      <span className="mr-1">{getCompanyIcon(player)}</span>
                                      {player}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Resonate rAI Export Section */}
            {analysis && analysis.market_map && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900">Resonate rAI Integration</h3>
                  <button
                    onClick={() => exportPersonas(analysis.market_map.id)}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center"
                    disabled={isProcessing}
                  >
                    <FaBrain className="mr-2 text-blue-600" />
                    Export for Resonate rAI
                  </button>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
                    <div className="flex items-center mb-3">
                      <FaUsers className="text-blue-600 mr-2" />
                      <h4 className="font-bold text-gray-900">Demographics</h4>
                    </div>
                    <p className="text-sm text-gray-700">
                      Base-level demographic data including age ranges, gender, household income, education levels, and employment categories mapped to Resonate Elements taxonomy.
                    </p>
                    <div className="mt-3 text-xs text-blue-600 font-medium">
                      Age Group • Gender • Household Income • Education • Employment
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
                    <div className="flex items-center mb-3">
                      <FaGlobe className="text-green-600 mr-2" />
                      <h4 className="font-bold text-gray-900">Geographics</h4>
                    </div>
                    <p className="text-sm text-gray-700">
                      Geographic segmentation data including regional distribution, market size classification, and geography types for precise location targeting.
                    </p>
                    <div className="mt-3 text-xs text-green-600 font-medium">
                      Region • Market Size • Geography Type
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-6 rounded-lg border border-purple-200">
                    <div className="flex items-center mb-3">
                      <TvIcon className="w-5 h-5 text-purple-600 mr-2" />
                      <h4 className="font-bold text-gray-900">Media Usage</h4>
                    </div>
                    <p className="text-sm text-gray-700">
                      Media consumption patterns and digital engagement levels to optimize channel strategy and content preferences for each segment.
                    </p>
                    <div className="mt-3 text-xs text-purple-600 font-medium">
                      Primary Media • Digital Engagement • Content Preferences  
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-6 rounded-lg border border-orange-200">
                  <div className="flex items-center mb-4">
                    <FaUsers className="text-orange-600 mr-2" />
                    <h4 className="font-bold text-gray-900">Ready for Resonate rAI Platform</h4>
                  </div>
                  <p className="text-gray-700 mb-4">
                    Export generates JSON data with base-level demographics, geographics, and media usage mapped directly to Resonate Elements taxonomy. 
                    Each segment includes specific taxonomy paths for easy entry into the Resonate rAI platform to recreate audiences.
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Export Format:</span> Structured JSON with taxonomy paths
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Integration:</span> Direct Resonate Elements mapping
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Segments:</span> Demographics • Psychographics • Behavioral
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Confidence:</span> High/Medium/Low mapping accuracy
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Competitive Benchmarking */}
            {analysis.market_map.competitors && analysis.market_map.competitors.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Competitive Benchmarking</h3>
                
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b-2 border-gray-200">
                        <th className="text-left py-4 px-3 font-bold text-gray-900 bg-gray-50">Brand</th>
                        <th className="text-left py-4 px-3 font-bold text-gray-900 bg-gray-50">Market Share</th>
                        <th className="text-left py-4 px-3 font-bold text-gray-900 bg-gray-50">Core Strengths</th>
                        <th className="text-left py-4 px-3 font-bold text-gray-900 bg-gray-50">Weaknesses</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.market_map.competitors.map((competitor, index) => (
                        <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                          <td className="py-4 px-3">
                            <div className="flex items-center">
                              <div className="w-8 h-8 mr-3 flex items-center justify-center bg-gray-50 border border-gray-200 rounded">
                                <BrandLogo companyName={competitor.name} size={24} />
                              </div>
                              <div className="font-bold text-gray-900">{competitor.name}</div>
                            </div>
                          </td>
                          <td className="py-4 px-3">
                            {competitor.market_share ? (
                              <span className="inline-block bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                                {(competitor.market_share * 100).toFixed(0)}%
                              </span>
                            ) : (
                              <span className="text-gray-400 text-sm">N/A</span>
                            )}
                          </td>
                          <td className="py-4 px-3">
                            <div className="flex flex-wrap gap-1">
                              {competitor.strengths.map((strength, i) => (
                                <span key={i} className="inline-block bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                                  {strength}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="py-4 px-3">
                            <div className="flex flex-wrap gap-1">
                              {competitor.weaknesses.map((weakness, i) => (
                                <span key={i} className="inline-block bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
                                  {weakness}
                                </span>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Competitive Digital Marketing Assessment */}
            {analysis.market_map.competitive_digital_assessment && Object.keys(analysis.market_map.competitive_digital_assessment).length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaGlobe className="mr-3 text-blue-600" />
                  Competitive Digital Marketing Assessment
                </h3>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {Object.entries(analysis.market_map.competitive_digital_assessment).map(([companyName, digitalData], index) => (
                    <div key={index} className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                      {/* Company Header */}
                      <div className="flex items-center mb-4 pb-3 border-b border-blue-200">
                        <div className="w-10 h-10 mr-3 flex items-center justify-center bg-white border border-blue-300 rounded-lg shadow-sm">
                          <BrandLogo companyName={companyName} size={32} />
                        </div>
                        <h4 className="font-bold text-gray-900 text-lg">{companyName}</h4>
                      </div>
                      
                      {/* Digital Strategy Overview */}
                      <div className="space-y-4">
                        {/* Advertising Spend */}
                        {digitalData.advertising_spend_estimate && (
                          <div className="bg-white p-3 rounded border border-blue-100">
                            <div className="text-xs font-medium text-blue-700 mb-1 flex items-center">
                              <FaShoppingCart className="mr-1" />
                              AD SPEND ESTIMATE
                            </div>
                            <div className="text-sm font-semibold text-gray-800">{digitalData.advertising_spend_estimate}</div>
                          </div>
                        )}
                        
                        {/* Primary Channels */}
                        {digitalData.primary_channels && digitalData.primary_channels.length > 0 && (
                          <div className="bg-white p-3 rounded border border-blue-100">
                            <div className="text-xs font-medium text-blue-700 mb-2 flex items-center">
                              <TvIcon className="w-4 h-4 mr-1" />
                              PRIMARY CHANNELS
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {digitalData.primary_channels.slice(0, 4).map((channel, i) => (
                                <div key={i} className="flex items-center bg-blue-50 text-blue-800 px-2 py-1 rounded text-xs">
                                  <span className="mr-1">{getMediaIcon(channel)}</span>
                                  {channel}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Social Media Presence */}
                        {digitalData.social_media_presence && (
                          <div className="bg-white p-3 rounded border border-blue-100">
                            <div className="text-xs font-medium text-blue-700 mb-1 flex items-center">
                              <FaBuilding className="mr-1" />
                              SOCIAL MEDIA
                            </div>
                            <div className="text-xs text-gray-700">{digitalData.social_media_presence}</div>
                          </div>
                        )}
                        
                        {/* SEO Positioning */}
                        {digitalData.seo_positioning && (
                          <div className="bg-white p-3 rounded border border-blue-100">
                            <div className="text-xs font-medium text-blue-700 mb-1 flex items-center">
                              <MagnifyingGlassIcon className="w-4 h-4 mr-1" />
                              SEO STRENGTH
                            </div>
                            <div className="text-xs text-gray-700">{digitalData.seo_positioning}</div>
                          </div>
                        )}
                        
                        {/* Marketing Strengths & Gaps */}
                        <div className="grid grid-cols-2 gap-3">
                          {digitalData.marketing_strengths && digitalData.marketing_strengths.length > 0 && (
                            <div className="bg-green-50 p-3 rounded border border-green-200">
                              <div className="text-xs font-medium text-green-700 mb-2 flex items-center">
                                <CheckCircleIcon className="w-4 h-4 mr-1" />
                                STRENGTHS
                              </div>
                              <div className="space-y-1">
                                {digitalData.marketing_strengths.slice(0, 2).map((strength, i) => (
                                  <div key={i} className="text-xs text-green-800">{strength}</div>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {digitalData.marketing_gaps && digitalData.marketing_gaps.length > 0 && (
                            <div className="bg-red-50 p-3 rounded border border-red-200">
                              <div className="text-xs font-medium text-red-700 mb-2 flex items-center">
                                <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
                                GAPS
                              </div>
                              <div className="space-y-1">
                                {digitalData.marketing_gaps.slice(0, 2).map((gap, i) => (
                                  <div key={i} className="text-xs text-red-800">{gap}</div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-6 bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
                  <div className="flex items-center mb-2">
                    <FaBrain className="text-purple-600 mr-2" />
                    <span className="font-medium text-purple-900">Digital Marketing Intelligence</span>
                  </div>
                  <p className="text-sm text-purple-700">
                    This competitive assessment analyzes digital marketing strategies, advertising spend estimates, channel preferences, and marketing execution strengths/gaps to identify opportunities for differentiation and growth.
                  </p>
                </div>
              </div>
            )}

            {/* Debug PPC Data */}
            {analysis.market_map && (
              <div className="bg-yellow-100 border border-yellow-400 p-4 rounded-lg mb-4">
                <h4 className="font-bold text-yellow-800">Debug: PPC Intelligence Data</h4>
                <pre className="text-xs text-yellow-700 mt-2 overflow-auto">
                  {JSON.stringify(analysis.market_map.ppc_intelligence, null, 2)}
                </pre>
              </div>
            )}

            {/* PPC Competitive Intelligence */}
            {analysis.market_map.ppc_intelligence && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaGoogle className="mr-3 text-blue-600" />
                  PPC Competitive Intelligence
                  <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    Powered by SpyFu
                  </span>
                </h3>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                  {/* Overview Stats */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                    <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                      <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                      PPC Overview
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{analysis.market_map.ppc_intelligence.paid_keywords_count || 0}</div>
                        <div className="text-xs text-gray-600">Paid Keywords</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{analysis.market_map.ppc_intelligence.competitors_count || 0}</div>
                        <div className="text-xs text-gray-600">PPC Competitors</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">{analysis.market_map.ppc_intelligence.ad_history_count || 0}</div>
                        <div className="text-xs text-gray-600">Ad Variations</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-orange-600 font-medium">{analysis.market_map.ppc_intelligence.confidence_level}</div>
                        <div className="text-xs text-gray-600">Confidence</div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Domain Stats */}
                  {analysis.market_map.ppc_intelligence.domain_stats && (
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-lg border border-green-200">
                      <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                        <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                        Domain Performance
                      </h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Est. Monthly Ad Spend:</span>
                          <span className="font-semibold text-gray-900">
                            ${analysis.market_map.ppc_intelligence.domain_stats.estimated_monthly_ad_spend?.toLocaleString() || 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Organic Keywords:</span>
                          <span className="font-semibold text-gray-900">
                            {analysis.market_map.ppc_intelligence.domain_stats.organic_keywords?.toLocaleString() || 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Paid Traffic:</span>
                          <span className="font-semibold text-gray-900">
                            {analysis.market_map.ppc_intelligence.domain_stats.estimated_monthly_paid_traffic?.toLocaleString() || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Top Keywords */}
                {analysis.market_map.ppc_intelligence.top_keywords && analysis.market_map.ppc_intelligence.top_keywords.length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                      <ChartBarIcon className="w-5 h-5 mr-2 text-blue-600" />
                      Top Performing Keywords
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left font-medium text-gray-700">Keyword</th>
                            <th className="px-4 py-2 text-center font-medium text-gray-700">Monthly Searches</th>
                            <th className="px-4 py-2 text-center font-medium text-gray-700">CPC</th>
                            <th className="px-4 py-2 text-center font-medium text-gray-700">Competition</th>
                            <th className="px-4 py-2 text-center font-medium text-gray-700">Est. Monthly Cost</th>
                          </tr>
                        </thead>
                        <tbody>
                          {analysis.market_map.ppc_intelligence.top_keywords.slice(0, 8).map((keyword, index) => (
                            <tr key={index} className="border-t border-gray-100">
                              <td className="px-4 py-2 font-medium">{keyword.keyword}</td>
                              <td className="px-4 py-2 text-center">{keyword.monthly_searches?.toLocaleString() || 'N/A'}</td>
                              <td className="px-4 py-2 text-center">${keyword.cpc?.toFixed(2) || '0.00'}</td>
                              <td className="px-4 py-2 text-center">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  keyword.competition === 'High' ? 'bg-red-100 text-red-800' :
                                  keyword.competition === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-green-100 text-green-800'
                                }`}>
                                  {keyword.competition}
                                </span>
                              </td>
                              <td className="px-4 py-2 text-center">${keyword.estimated_monthly_cost?.toLocaleString() || '0'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                
                {/* Top PPC Competitors */}
                {analysis.market_map.ppc_intelligence.top_ppc_competitors && analysis.market_map.ppc_intelligence.top_ppc_competitors.length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                      <TrophyIcon className="w-5 h-5 mr-2 text-yellow-600" />
                      Top PPC Competitors
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {analysis.market_map.ppc_intelligence.top_ppc_competitors.slice(0, 6).map((competitor, index) => (
                        <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <div className="flex items-center mb-3">
                            <div className="w-8 h-8 mr-3 flex items-center justify-center bg-white border border-gray-300 rounded-lg">
                              <BrandLogo companyName={competitor.domain} size={20} />
                            </div>
                            <div className="font-medium text-gray-900 text-sm">{competitor.domain}</div>
                          </div>
                          <div className="space-y-2 text-xs">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Shared Keywords:</span>
                              <span className="font-semibold">{competitor.overlapping_keywords}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Est. Monthly Spend:</span>
                              <span className="font-semibold">${competitor.estimated_monthly_spend?.toLocaleString() || '0'}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Recent Ad Examples - Google Ad Format */}
                {analysis.market_map.ppc_intelligence.recent_ads && analysis.market_map.ppc_intelligence.recent_ads.length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                      <FaGoogle className="w-5 h-5 mr-2 text-blue-600" />
                      Recent Google Ads
                    </h4>
                    <div className="space-y-4">
                      {analysis.market_map.ppc_intelligence.recent_ads.slice(0, 4).map((ad, index) => (
                        <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                          {/* Ad Label */}
                          <div className="flex items-center mb-2">
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium mr-2">Ad</span>
                            <span className="text-xs text-gray-500">google.com</span>
                          </div>
                          
                          {/* Ad Content */}
                          <div className="mb-3">
                            {/* Ad Headline */}
                            <h5 className="text-blue-600 text-lg font-medium hover:underline cursor-pointer mb-1">
                              {ad.ad_text.split('.')[0] || ad.ad_text.substring(0, 50)}
                            </h5>
                            
                            {/* Ad URL */}
                            <div className="text-green-700 text-sm mb-2">
                              https://www.example.com/{ad.keyword.replace(/\s+/g, '-').toLowerCase()}
                            </div>
                            
                            {/* Ad Description */}
                            <p className="text-gray-700 text-sm leading-relaxed">
                              {ad.ad_text.length > 60 ? ad.ad_text : `${ad.ad_text} Professional services with competitive pricing and excellent customer support.`}
                            </p>
                          </div>
                          
                          {/* Ad Extensions (Sitelinks simulation) */}
                          <div className="flex flex-wrap gap-3 text-blue-600 text-sm mb-3">
                            <a href="#" className="hover:underline">Services</a>
                            <a href="#" className="hover:underline">Pricing</a>
                            <a href="#" className="hover:underline">Contact</a>
                            <a href="#" className="hover:underline">Reviews</a>
                          </div>
                          
                          {/* Ad Metadata */}
                          <div className="flex justify-between items-center text-xs text-gray-500 border-t border-gray-100 pt-2">
                            <span>Keyword: <strong className="text-gray-700">{ad.keyword}</strong></span>
                            <div className="flex items-center space-x-3">
                              {ad.position && (
                                <span className="bg-gray-100 px-2 py-1 rounded">Position #{ad.position}</span>
                              )}
                              <div className="flex items-center">
                                <StarIcon className="w-4 h-4 text-yellow-400 mr-1" />
                                <span>4.{Math.floor(Math.random() * 5) + 3} ({Math.floor(Math.random() * 900) + 100})</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {/* Google Ads Attribution */}
                    <div className="mt-4 text-center">
                      <div className="inline-flex items-center px-3 py-2 bg-gray-50 rounded-lg text-sm text-gray-600">
                        <FaGoogle className="w-4 h-4 mr-2 text-blue-500" />
                        Ads based on competitive intelligence data
                      </div>
                    </div>
                  </div>
                )}
                
                <div className="bg-gradient-to-r from-indigo-50 to-blue-50 p-4 rounded-lg border border-indigo-200">
                  <div className="flex items-center mb-2">
                    <MagnifyingGlassIcon className="w-5 h-5 text-indigo-600 mr-2" />
                    <span className="font-medium text-indigo-900">PPC Intelligence Insights</span>
                  </div>
                  <p className="text-sm text-indigo-700">
                    This competitive intelligence data is powered by SpyFu and provides real insights into competitor PPC strategies, 
                    keyword targeting, ad spend estimates, and advertising tactics to inform your digital marketing strategy.
                  </p>
                </div>
              </div>
            )}

            {/* Strategic Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Opportunities */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <FaUsers className="mr-2 text-orange-600" />
                  Market Opportunities
                </h3>
                <div className="space-y-3">
                  {analysis.market_map.opportunities.map((opportunity, index) => (
                    <div key={index} className="flex items-start">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span className="text-gray-700">{opportunity}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Threats */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <FaShoppingCart className="mr-2 text-red-600" />
                  Market Threats
                </h3>
                <div className="space-y-3">
                  {analysis.market_map.threats.map((threat, index) => (
                    <div key={index} className="flex items-start">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span className="text-gray-700">{threat}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Strategic Recommendations */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <FaBuilding className="mr-2 text-green-600" />
                Strategic Recommendations
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysis.market_map.strategic_recommendations.map((recommendation, index) => (
                  <div key={index} className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                    <span className="text-gray-800">{recommendation}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Export Options */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">📥 Export Market Analysis</h3>
              <p className="text-sm text-gray-600 mb-4">Download your comprehensive market analysis in multiple formats</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={exportPDF}
                  className="bg-red-500 text-white px-6 py-4 rounded-lg font-semibold hover:bg-red-600 flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
                >
                  <svg className="h-6 w-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                  </svg>
                  <div className="text-left">
                    <div className="text-sm font-bold">Download PDF Report</div>
                    <div className="text-xs opacity-90">Client-ready with BCM branding</div>
                  </div>
                </button>
                <button
                  onClick={exportMarketMap}
                  className="bg-green-600 text-white px-6 py-4 rounded-lg font-semibold hover:bg-green-700 flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
                >
                  <svg className="h-6 w-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <div className="text-left">
                    <div className="text-sm font-bold">Download Excel Data</div>
                    <div className="text-xs opacity-90">Raw data for analysis</div>
                  </div>
                </button>
              </div>
              
              {/* Alternative direct links if downloads don't work */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-600 mb-2 font-semibold">Alternative: Open in New Tab</p>
                <div className="flex flex-wrap gap-2">
                  <a
                    href={`${process.env.REACT_APP_BACKEND_URL}/api/export-pdf/${analysis.market_map.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                  >
                    📄 Open PDF in new tab
                  </a>
                  <a
                    href={`${process.env.REACT_APP_BACKEND_URL}/api/export-market-map/${analysis.market_map.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                  >
                    <FaBrain className="mr-2" />
                    Open Excel in new tab
                  </a>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-orange-50 rounded-lg border border-orange-200">
                <p className="text-xs text-orange-800">
                  <span className="font-semibold flex items-center">
                    <FaBrain className="mr-1" />
                    Tip:
                  </span> Use PDF for client presentations and Excel for detailed data analysis or integration with simulation platforms.
                </p>
              </div>
            </div>

          </div>
        )}

        {/* Data Sources & Methodology - Moved to Bottom */}
        {analysis && (
          <div className="bg-white rounded-lg shadow-md p-6 mt-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <FaBrain className="mr-2 text-blue-600" />
              Resources & Footnotes
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <FaBrain className="mr-2 text-blue-600" />
                  Data Sources
                </h4>
                <ul className="space-y-2">
                  {analysis.market_map.data_sources.map((source, index) => {
                    // Map source names to URLs
                    const sourceMapping = {
                      "Gartner Market Research": "https://www.gartner.com/en/research",
                      "McKinsey Industry Reports": "https://www.mckinsey.com/industries",
                      "IBISWorld Market Analysis": "https://www.ibisworld.com",
                      "Forrester Research": "https://www.forrester.com/research",
                      "PwC Industry Insights": "https://www.pwc.com/us/en/industries.html",
                      "Statista": "https://www.statista.com",
                      "CB Insights": "https://www.cbinsights.com",
                      "Crunchbase": "https://www.crunchbase.com"
                    };
                    
                    const sourceName = typeof source === 'string' ? source : source.name;
                    const sourceUrl = typeof source === 'object' && source.url ? source.url : sourceMapping[sourceName];
                    
                    return (
                      <li key={index} className="flex items-start text-sm text-gray-600">
                        <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mr-2 mt-1.5 flex-shrink-0"></div>
                        <span className="mr-2 text-xs text-gray-400">[{index + 1}]</span>
                        {sourceUrl ? (
                          <a 
                            href={sourceUrl} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 underline hover:no-underline transition-colors"
                            title={`Visit ${sourceName}`}
                          >
                            {sourceName} 🔗
                          </a>
                        ) : (
                          <span>{sourceName}</span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">🔬 Methodology</h4>
                <p className="text-sm text-gray-600">{analysis.market_map.methodology}</p>
                <div className="mt-4">
                  <span className="text-xs font-medium text-gray-500">Analysis Date: </span>
                  <span className="text-xs text-gray-600">
                    {new Date(analysis.market_map.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <div className="mt-2">
                  <span className="text-xs font-medium text-gray-500">Confidence Level: </span>
                  <span className="text-xs text-gray-600 capitalize">
                    {analysis.market_map.confidence_level}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Analysis History */}
        {history.length > 0 && currentStep !== 4 && (
          <div className="mt-8 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Market Maps</h3>
            <div className="space-y-3">
              {history.slice(0, 5).map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer group"
                     onClick={() => loadAnalysis(item.id)}>
                  <div>
                    <div className="text-sm font-medium text-gray-900 group-hover:text-orange-600 transition-colors">
                      {item.product_name}
                    </div>
                    <div className="text-xs text-gray-500">{item.geography}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-orange-600">
                      {formatCurrency(item.market_size)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Help text */}
            <div className="mt-4 pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-500 text-center">
                Click on any analysis to view results
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default MarketMapApp;
