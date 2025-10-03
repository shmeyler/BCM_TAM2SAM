import React from 'react';

const Login = () => {
  const handleGoogleLogin = () => {
    // Redirect URL should be the main app root
    const redirectUrl = window.location.origin;
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
    console.log('Redirecting to:', authUrl);
    window.location.href = authUrl;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* BCM Logo and Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-orange-500 rounded-full mb-4">
            <span className="text-4xl text-white font-bold">BCM</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Map Generator</h1>
          <p className="text-gray-600">AI-Powered Market Intelligence</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-xl shadow-xl p-8 border border-gray-100">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome Back</h2>
            <p className="text-sm text-gray-600">
              Sign in with your @beebyclarkmeyler.com account
            </p>
          </div>

          {/* Google Sign In Button */}
          <button
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center space-x-3 bg-white border-2 border-gray-300 rounded-lg px-6 py-4 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 shadow-sm hover:shadow-md"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span className="text-gray-700 font-semibold">Sign in with Google</span>
          </button>

          {/* Info Text */}
          <div className="mt-6 p-4 bg-orange-50 rounded-lg border border-orange-100">
            <p className="text-xs text-gray-700 text-center">
              <span className="font-semibold">🔒 Secure Access:</span> Only @beebyclarkmeyler.com email addresses are authorized to access this platform.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-xs text-gray-500">
            Powered by Kimi K2 • BCM Market Intelligence Platform
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;