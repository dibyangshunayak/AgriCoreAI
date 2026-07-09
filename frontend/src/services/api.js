export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

/**
 * Uploads a file attachment (image, pdf, document, spreadsheet) to the backend.
 * Returns the relative file_path, context, and file type.
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${BACKEND_URL}/api/upload`, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to upload file');
    }

    return await response.json();
  } catch (error) {
    console.error("API error uploading file:", error);
    throw error;
  }
};

/**
 * Fetches geolocation information from the user's IP.
 */
export const fetchIpLocation = async () => {
  try {
    const response = await fetch('https://ipapi.co/json/');
    if (!response.ok) {
      throw new Error('Failed to retrieve IP geolocation data');
    }
    return await response.json();
  } catch (error) {
    console.error("API error fetching IP geolocation:", error);
    throw error;
  }
};

/**
 * Sends coordinates to the backend to reverse geocode them into address details.
 */
export const reverseGeocode = async (latitude, longitude) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/geocode`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ latitude, longitude }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to reverse geocode coordinates');
    }

    return await response.json();
  } catch (error) {
    console.error("API error reverse geocoding coordinates:", error);
    throw error;
  }
};
