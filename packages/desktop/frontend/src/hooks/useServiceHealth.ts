import axios from "axios";
import { useEffect, useState } from "react";
import { getBackendBaseUrl } from "../api";
import { HealthFetchState, ServiceHealth } from "../lib/productReadiness";

export function useServiceHealth() {
  const [health, setHealth] = useState<ServiceHealth | null>(null);
  const [healthState, setHealthState] = useState<HealthFetchState>("loading");

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    (async () => {
      try {
        const base = await getBackendBaseUrl();
        const res = await axios.get<ServiceHealth>(`${base}/health`, {
          signal: controller.signal,
          timeout: 5000,
        });
        if (!active) return;
        setHealth(res.data);
        setHealthState("online");
      } catch {
        if (!active) return;
        setHealth(null);
        setHealthState("offline");
      }
    })();

    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  return { health, healthState };
}
