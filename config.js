/**
 * HeatShield Global Configuration
 * 
 * To override the API base URL in production deployment (e.g. Vercel, Netlify, GitHub Pages),
 * you can set window.HEATSHIELD_API_BASE in a script tag prior to loading config.js,
 * or update the default fallback URL below.
 */
(function() {
  const defaultApiBase = "http://127.0.0.1:8000";
  
  // Clean up trailing slashes if present
  let rawUrl = (window.HEATSHIELD_API_BASE || defaultApiBase).trim();
  if (rawUrl.endsWith('/')) {
    rawUrl = rawUrl.slice(0, -1);
  }
  
  window.HEATSHIELD_CONFIG = {
    API_BASE: rawUrl, // e.g. "http://127.0.0.1:8000" or "https://heatshield-api.onrender.com"
    API_BASE_URL: rawUrl + "/api" // e.g. "http://127.0.0.1:8000/api" or "https://heatshield-api.onrender.com/api"
  };
})();
