// frontend/src/config/api.js

const LOCAL_API = "http://127.0.0.1:8000";
const PROD_API = process.env.API_BACKEND_URL;

export const API_BASE_URL = PROD_API || LOCAL_API;
