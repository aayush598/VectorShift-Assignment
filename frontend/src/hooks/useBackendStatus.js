import { useEffect, useState, useRef } from "react";
import { API_BASE_URL } from "../config/api";

const POLL_INTERVAL = 1000; // 1 seconds

export const useBackendStatus = () => {
  const [isConnected, setIsConnected] = useState(null); // null = checking
  const timerRef = useRef(null);

  const checkBackend = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
      });

      if (!res.ok) throw new Error("Health check failed");

      setIsConnected(true);
      stopPolling();
    } catch {
      setIsConnected(false);
      startPolling();
    }
  };

  const startPolling = () => {
    if (!timerRef.current) {
      timerRef.current = setInterval(checkBackend, POLL_INTERVAL);
    }
  };

  const stopPolling = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  useEffect(() => {
    checkBackend();

    return () => {
      stopPolling();
    };
  }, []);

  return { isConnected, retry: checkBackend };
};
