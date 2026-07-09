import React, { createContext, useState, useEffect } from 'react';
import { fetchIpLocation, reverseGeocode } from '../services/api';

export const LocationContext = createContext();

export const LocationProvider = ({ children }) => {
  // Try to load cached location on startup
  const [location, setLocation] = useState(() => {
    try {
      const sessionLoc = sessionStorage.getItem('agri_location');
      if (sessionLoc) return JSON.parse(sessionLoc);
      const localLoc = localStorage.getItem('agri_location');
      if (localLoc) return JSON.parse(localLoc);
    } catch (e) {
      console.error("Failed to parse cached location:", e);
    }
    return null;
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [gpsStatus, setGpsStatus] = useState(() => {
    const sessionStatus = sessionStorage.getItem('agri_gps_status');
    if (sessionStatus) return sessionStatus;
    const localStatus = localStorage.getItem('agri_gps_status');
    if (localStatus) return localStatus;
    return 'loading';
  });

  const saveLocationState = (locState, status) => {
    setLocation(locState);
    setGpsStatus(status);
    try {
      if (locState) {
        localStorage.setItem('agri_location', JSON.stringify(locState));
        sessionStorage.setItem('agri_location', JSON.stringify(locState));
      } else {
        localStorage.removeItem('agri_location');
        sessionStorage.removeItem('agri_location');
      }
      localStorage.setItem('agri_gps_status', status);
      sessionStorage.setItem('agri_gps_status', status);
    } catch (e) {
      console.error("Storage save failed:", e);
    }
  };

  const fetchWeatherDetails = async (lat, lon) => {
    try {
      const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,weather_code`);
      if (res.ok) {
        const data = await res.json();
        if (data.current) {
          return {
            temp: data.current.temperature_2m,
            code: data.current.weather_code
          };
        }
      }
    } catch (e) {
      console.error("Failed to fetch weather forecast:", e);
    }
    return null;
  };

  const handleIpFallback = async (gpsErrorMsg) => {
    try {
      console.log("GPS access denied/failed, falling back to IP Geolocation.");
      const ipData = await fetchIpLocation();
      const lat = parseFloat(ipData.latitude);
      const lon = parseFloat(ipData.longitude);
      const weather = await fetchWeatherDetails(lat, lon);
      
      const locationState = {
        latitude: lat,
        longitude: lon,
        accuracy: null,
        city: ipData.city || "",
        region: ipData.region || "",
        country: ipData.country_name || "",
        formatted_location: ipData.city && ipData.region
          ? `${ipData.city}, ${ipData.region}`
          : ipData.city || ipData.region || "IP Location",
        type: 'IP',
        weather
      };
      
      saveLocationState(locationState, 'ip');
      setError(null);
    } catch (ipErr) {
      console.error("IP Geolocation fallback failed as well:", ipErr);
      setError(`GPS error: ${gpsErrorMsg}. IP error: ${ipErr.message}`);
      saveLocationState(null, 'denied');
    }
  };

  const requestLocation = () => {
    setLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      const errStr = "Geolocation is not supported by this browser.";
      console.warn(errStr);
      handleIpFallback(errStr).finally(() => setLoading(false));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const coords = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          type: 'GPS'
        };

        try {
          // Reverse geocode via Flask endpoint using Location MCP
          const address = await reverseGeocode(coords.latitude, coords.longitude);
          const weather = await fetchWeatherDetails(coords.latitude, coords.longitude);
          const locationState = {
            ...coords,
            city: address.city || "",
            district: address.district || "",
            state: address.state || "",
            country: address.country || "",
            formatted_location: address.formatted_location || `${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)}`,
            weather
          };
          saveLocationState(locationState, 'connected');
        } catch (err) {
          console.warn("Backend reverse geocoding failed, falling back to basic formatting:", err);
          const weather = await fetchWeatherDetails(coords.latitude, coords.longitude);
          const locationState = {
            ...coords,
            formatted_location: `${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)}`,
            weather
          };
          saveLocationState(locationState, 'connected');
        } finally {
          setLoading(false);
        }
      },
      async (error) => {
        await handleIpFallback(error.message);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  // Auto initialize on startup
  useEffect(() => {
    requestLocation();
  }, []);

  return (
    <LocationContext.Provider value={{
      location,
      loading,
      error,
      gpsStatus,
      requestLocation
    }}>
      {children}
    </LocationContext.Provider>
  );
};
