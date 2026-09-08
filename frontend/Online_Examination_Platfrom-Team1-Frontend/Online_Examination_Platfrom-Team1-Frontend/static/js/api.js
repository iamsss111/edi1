/**
 * MMCOE Online Examination Platform
 * Shared API Client
 *
 * Handles:
 * - Backend API requests
 * - JWT token storage
 * - Authenticated requests
 * - Current user storage
 * - Login/logout
 * - Common API error handling
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

const AUTH_TOKEN_KEY = 'examportal_access_token';
const AUTH_USER_KEY = 'examportal_user';


/**
 * Store authentication data.
 *
 * Remember me:
 *   localStorage
 *
 * Session only:
 *   sessionStorage
 */
function storeAuth(accessToken, user, rememberMe = false) {
  clearAuth();

  const storage = rememberMe ? localStorage : sessionStorage;

  storage.setItem(AUTH_TOKEN_KEY, accessToken);
  storage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}


/**
 * Retrieve the stored JWT token.
 */
function getAccessToken() {
  return (
    localStorage.getItem(AUTH_TOKEN_KEY) ||
    sessionStorage.getItem(AUTH_TOKEN_KEY)
  );
}


/**
 * Retrieve the stored authenticated user.
 */
function getStoredUser() {
  const rawUser =
    localStorage.getItem(AUTH_USER_KEY) ||
    sessionStorage.getItem(AUTH_USER_KEY);

  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch (error) {
    console.error('Unable to parse stored user data:', error);
    return null;
  }
}


/**
 * Clear authentication data from both storage locations.
 */
function clearAuth() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);

  sessionStorage.removeItem(AUTH_TOKEN_KEY);
  sessionStorage.removeItem(AUTH_USER_KEY);
}


/**
 * Check whether a user is currently authenticated.
 */
function isAuthenticated() {
  return Boolean(getAccessToken());
}


/**
 * Make an API request.
 *
 * Automatically adds:
 * Authorization: Bearer <JWT>
 *
 * Returns parsed JSON.
 */
async function apiRequest(endpoint, options = {}) {
  const token = getAccessToken();

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  let responseData = null;

  try {
    responseData = await response.json();
  } catch (error) {
    responseData = null;
  }

  /*
   * A 401 means the JWT is missing, invalid, or expired.
   *
   * Clear local authentication state so the user does not
   * remain in a stale authenticated state.
   */
  if (response.status === 401) {
    clearAuth();
  }

  if (!response.ok) {
    const error = new Error(
      responseData?.message ||
      `Request failed with status ${response.status}.`
    );

    error.status = response.status;
    error.data = responseData;

    throw error;
  }

  return responseData;
}


/**
 * Authenticate a user with the backend.
 */
async function login(email, password, rememberMe = false) {
  const responseData = await apiRequest('/login', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password
    })
  });

  if (
    !responseData ||
    !responseData.success ||
    !responseData.data ||
    !responseData.data.access_token ||
    !responseData.data.user
  ) {
    throw new Error('The server returned an invalid login response.');
  }

  const {
    access_token: accessToken,
    user
  } = responseData.data;

  storeAuth(accessToken, user, rememberMe);

  return user;
}


/**
 * Retrieve the currently authenticated user from the backend.
 */
async function getCurrentUser() {
  return apiRequest('/me', {
    method: 'GET'
  });
}


/**
 * Log out the current user locally.
 */
function logout() {
  clearAuth();
  window.location.href = '/auth/login.html';
}


/**
 * Return the dashboard URL for a backend role.
 *
 * The role comes from the backend, not from the login UI.
 */
function getDashboardUrl(role) {
  switch (role) {
    case 'STUDENT':
      return '/student/dashboard.html';

    case 'FACULTY':
      return '/faculty/dashboard.html';

    case 'ADMIN':
      return '/admin/dashboard.html';

    default:
      return null;
  }
}


/**
 * Redirect an authenticated user to the appropriate portal.
 */
function redirectByRole(role) {
  const dashboardUrl = getDashboardUrl(role);

  if (!dashboardUrl) {
    clearAuth();
    throw new Error('Your account has an unsupported role.');
  }

  window.location.href = dashboardUrl;
}

