import { useContext } from 'react';
import { LocationContext } from '../context/LocationContext';

/**
 * Custom hook to access the AgriCore AI Geolocation state and controls.
 * Must be used inside a LocationProvider wrapper.
 */
export const useLocation = () => {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocation must be used within a LocationProvider');
  }
  return context;
};

export default useLocation;
