import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MarketMapApp = () => {
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
      { name: 'Analyzing Market Landscape with AI', duration: 25 },
      { name: 'Processing Competitive Intelligence', duration: 15 },
      { name: 'Generating Market Segmentation', duration: 10 },
      { name: 'Creating Executive Summary', duration: 20 },
      { name: 'Finalizing Visual Market Map', duration: 10 }
    ]
  });
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadAnalysis = async (analysisId) => {
    try {
      const response = await axios.get(`${API}/analysis/${analysisId}`);
      setAnalysis(response.data);
      setCurrentStep(4);
    } catch (error) {
      console.error('Error loading analysis:', error);
      alert('Error loading analysis. Please try again.');
    }
  };

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API}/analysis-history`);
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

    try {
      // Start progress simulation
      const progressPromise = simulateProgress();
      
      // Start actual API call
      const apiPromise = axios.post(`${API}/analyze-market`, formData, {
        timeout: 120000  // 120 seconds timeout (increased for executive summary generation)
      });

      // Wait for both to complete
      const [_, response] = await Promise.all([progressPromise, apiPromise]);
      
      console.log('Market analysis response:', response.data);
      setAnalysis(response.data);
      setCurrentStep(4);
      loadHistory();

      // Reset progress
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
        alert('Analysis is taking longer than expected. Please try again or contact support.');
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

  const exportMarketMap = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/export-market-map/${analysis.market_map.id}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `market-map-${analysis.market_input.product_name.replace(/\s+/g, '-').toLowerCase()}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Export failed:', error);
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
      'Apple': 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg',
      'Google': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
      'Microsoft': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg',
      'Samsung': 'https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg',
      'Fitbit': 'https://upload.wikimedia.org/wikipedia/commons/3/33/Fitbit_logo16.svg',
      'Garmin': 'https://upload.wikimedia.org/wikipedia/commons/5/53/Garmin_logo.svg',
      'Xiaomi': 'https://upload.wikimedia.org/wikipedia/commons/2/29/Xiaomi_logo.svg',
      'Amazon': 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
      'Salesforce': 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg',
      'PayPal': 'https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg',
      'Stripe': 'https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg',
      'Square': 'https://upload.wikimedia.org/wikipedia/commons/6/64/Square%2C_Inc._logo.svg',
      'Sierra Nevada': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23228B22"%3E%3Cpath d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/%3E%3C/svg%3E',
      'Stone Brewing': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="%23654321"%3E%3Cpath d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/%3E%3C/svg%3E'
    };

    // Return specific logo if mapped, otherwise return a default business icon
    return logoMap[companyName] || "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='%23374151'%3E%3Cpath d='M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z'/%3E%3C/svg%3E";
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

  return (
    <div className="min-h-screen bg-gray-50">
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
            {currentStep === 4 && (
              <button
                onClick={resetForm}
                className="bg-white text-orange-600 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                New Analysis
              </button>
            )}
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

                  {/* Progress Indicator - Full Width */}
                  {isAnalyzing && (
                    <div className="mt-6 w-full">
                      <div className="bg-white p-6 rounded-lg shadow-lg border max-w-2xl mx-auto">
                        <div className="text-center mb-4">
                          <h4 className="text-lg font-semibold text-gray-900 mb-2">Market Analysis in Progress</h4>
                          <p className="text-sm text-gray-600">
                            Step {analysisProgress.currentStep} of {analysisProgress.totalSteps}
                          </p>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                          <div
                            className="bg-gradient-to-r from-orange-500 to-orange-600 h-3 rounded-full transition-all duration-500 ease-out"
                            style={{ width: `${(analysisProgress.currentStep / analysisProgress.totalSteps) * 100}%` }}
                          ></div>
                        </div>

                        {/* Current Step */}
                        <div className="text-center mb-3">
                          <div className="text-sm font-medium text-gray-900 mb-1">
                            {analysisProgress.stepName || 'Initializing...'}
                          </div>
                          {analysisProgress.estimatedTimeLeft > 0 && (
                            <div className="text-xs text-gray-500">
                              Estimated time remaining: {analysisProgress.estimatedTimeLeft} seconds
                            </div>
                          )}
                        </div>

                        {/* Steps List */}
                        <div className="space-y-2">
                          {analysisProgress.steps.map((step, index) => (
                            <div key={index} className={`flex items-center text-xs ${
                              index < analysisProgress.currentStep ? 'text-green-600' :
                              index === analysisProgress.currentStep - 1 ? 'text-orange-600' :
                              'text-gray-400'
                            }`}>
                              <div className={`w-4 h-4 rounded-full mr-3 flex items-center justify-center ${
                                index < analysisProgress.currentStep ? 'bg-green-500' :
                                index === analysisProgress.currentStep - 1 ? 'bg-orange-500' :
                                'bg-gray-300'
                              }`}>
                                {index < analysisProgress.currentStep ? (
                                  <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                ) : index === analysisProgress.currentStep - 1 ? (
                                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
                                ) : (
                                  <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                                )}
                              </div>
                              <span>{step.name}</span>
                            </div>
                          ))}
                        </div>

                        {/* Cancel Button - Proper Button Style */}
                        <div className="mt-6 pt-4 border-t border-gray-100 text-center">
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

                        {/* Subtle help text */}
                        <div className="mt-4 pt-4 border-t border-gray-100">
                          <p className="text-xs text-gray-400 text-center">
                            Please wait while we generate your comprehensive market analysis...
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
                        <span className="text-2xl">🌍</span>
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
                                  <span key={i} className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
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
                        <span className="text-2xl">👥</span>
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
                                  <span key={i} className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
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
                        <span className="text-2xl">🧠</span>
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
                                  <span key={i} className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
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
                        <span className="text-2xl">🛒</span>
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
                                  <span key={i} className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
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
                                <img
                                  src={getCompanyLogo(competitor.name)}
                                  alt={`${competitor.name} logo`}
                                  className="w-6 h-6 object-contain"
                                  onError={(e) => {
                                    // Fallback to a generic business icon
                                    e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='%23374151'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E";
                                  }}
                                />
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

            {/* Strategic Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Opportunities */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">🎯 Market Opportunities</h3>
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
                <h3 className="text-xl font-bold text-gray-900 mb-4">⚠️ Market Threats</h3>
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
              <h3 className="text-xl font-bold text-gray-900 mb-4">✅ Strategic Recommendations</h3>
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
              <h3 className="text-xl font-bold text-gray-900 mb-4">Export Market Map</h3>
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={exportMarketMap}
                  className="bg-orange-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-orange-600 flex items-center"
                >
                  <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  Download Comprehensive Excel Report
                </button>
              </div>
            </div>

            {/* Data Sources & Methodology */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Data Sources & Methodology</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Data Sources</h4>
                  <ul className="space-y-2">
                    {analysis.market_map.data_sources.map((source, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mr-2"></div>
                        {source}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Methodology</h4>
                  <p className="text-sm text-gray-600">{analysis.market_map.methodology}</p>
                  <div className="mt-4">
                    <span className="text-xs font-medium text-gray-500">Analysis Date: </span>
                    <span className="text-xs text-gray-600">
                      {new Date(analysis.market_map.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* TAM → SAM → SOM Visual Chart */}
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
                        <strong>Total Addressable Market:</strong> Represents 100% of global revenue opportunity for {analysis.market_input.product_name} 
                        across all customer segments in {analysis.market_input.geography}. Based on {analysis.market_map.data_sources.join(', ')} data, 
                        growing at {(analysis.market_map.market_growth_rate * 100).toFixed(1)}% CAGR driven by {analysis.market_map.key_drivers.slice(0,2).join(' and ')}.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-4 h-4 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <h4 className="text-lg font-bold text-blue-600 mb-2">SAM - {formatCurrency(analysis.market_map.total_market_size * 0.3)}</h4>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        <strong>Serviceable Addressable Market:</strong> 30% of TAM ({formatCurrency(analysis.market_map.total_market_size * 0.3)}) 
                        representing segments we can realistically serve with our {analysis.market_input.transaction_type} business model. 
                        Focused on {analysis.market_input.target_user} who prioritize {analysis.market_input.key_metrics.split(',')[0]} 
                        and are motivated by {analysis.market_input.demand_driver}.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-4 h-4 bg-blue-300 rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <h4 className="text-lg font-bold text-blue-300 mb-2">SOM - {formatCurrency(analysis.market_map.total_market_size * 0.03)}</h4>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        <strong>Serviceable Obtainable Market:</strong> 10% of SAM ({formatCurrency(analysis.market_map.total_market_size * 0.03)}) 
                        based on realistic 3-5 year market penetration assuming competitive response from {analysis.market_map.competitors.slice(0,2).map(c => c.name).join(' and ')}. 
                        Achievable through {analysis.market_map.strategic_recommendations.slice(0,1)[0]?.toLowerCase() || 'focused market strategy'}.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Right side - Concentric Circles Visualization with Better Labels */}
                <div className="flex justify-center relative">
                  <div className="relative w-80 h-80">
                    {/* TAM - Outer Circle */}
                    <div className="absolute inset-0 w-80 h-80 bg-blue-900 rounded-full flex items-end justify-center pb-4">
                      {/* TAM Label positioned at bottom of outer ring */}
                      <div className="text-white text-center">
                        <div className="text-xl font-bold">{formatCurrency(analysis.market_map.total_market_size)}</div>
                        <div className="text-sm font-medium">TAM</div>
                      </div>
                    </div>
                      
                    {/* SAM - Middle Circle - Properly centered */}
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-56 h-56 bg-blue-600 rounded-full flex items-end justify-center pb-3">
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
                    
                    {/* Improved Labels with better positioning */}
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2">
                      <div className="flex flex-col items-center">
                        <div className="text-xs text-gray-600 mb-1 whitespace-nowrap">Total Market</div>
                        <div className="w-6 h-px bg-gray-400"></div>
                        <div className="w-0 h-0 border-l-2 border-r-2 border-t-4 border-transparent border-t-gray-400"></div>
                      </div>
                    </div>
                    
                    <div className="absolute top-8 -right-16">
                      <div className="flex items-center">
                        <div className="w-8 h-px bg-gray-400"></div>
                        <div className="w-0 h-0 border-t-2 border-b-2 border-l-4 border-transparent border-l-gray-400"></div>
                        <div className="text-xs text-gray-600 ml-2 whitespace-nowrap">Serviceable<br/>Market</div>
                      </div>
                    </div>
                    
                    <div className="absolute bottom-8 -left-20">
                      <div className="flex items-center">
                        <div className="text-xs text-gray-600 mr-2 whitespace-nowrap">Obtainable<br/>Market</div>
                        <div className="w-0 h-0 border-t-2 border-b-2 border-r-4 border-transparent border-r-gray-400"></div>
                        <div className="w-8 h-px bg-gray-400"></div>
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
