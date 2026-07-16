const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const runtimeConfig = {
  apiBase,
  wsBase: apiBase.replace(/^http/i, "ws"),
};
