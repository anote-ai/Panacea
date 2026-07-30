export type HealthFetchState = "loading" | "online" | "offline";

export interface ServiceHealth {
  status: string;
  service: string;
  environment?: string;
  readiness?: "ready" | "degraded";
  checks?: {
    googleAuthConfigured?: boolean;
    billingConfigured?: boolean;
    aiProviderConfigured?: boolean;
    providerKeyEncryptionConfigured?: boolean;
    jwtSecretStrong?: boolean;
  };
  warnings?: string[];
}

export interface StatusNotice {
  title: string;
  detail: string;
  tone: "warning" | "error";
}

const GENERAL_SUGGESTIONS = [
  "Summarize the most important points from this project.",
  "Draft a status update I can send to my team.",
  "List the biggest risks and next steps.",
];

const DOCUMENT_SUGGESTIONS = [
  "Summarize the attached documents in plain English.",
  "Extract the key risks, dates, and owners.",
  "Turn these documents into a short action plan.",
];

export function getAuthStatusNotice(
  healthState: HealthFetchState,
  health: ServiceHealth | null,
): StatusNotice | null {
  if (healthState === "offline") {
    return {
      title: "Service unavailable",
      detail:
        "We couldn't reach the app service. If you're previewing locally, start the backend and refresh.",
      tone: "error",
    };
  }

  if (healthState !== "online") return null;

  if (health?.checks?.googleAuthConfigured === false) {
    return {
      title: "Google sign-in unavailable",
      detail:
        "Email and password sign-in still work. Add the Google OAuth environment variables to enable it.",
      tone: "warning",
    };
  }

  if (health?.readiness === "degraded") {
    return {
      title: "Service running with limited configuration",
      detail:
        "Core chat and sign-in should still work, but some optional integrations still need setup.",
      tone: "warning",
    };
  }

  return null;
}

export function getEmptyStateSuggestions(hasDocuments: boolean): readonly string[] {
  return hasDocuments ? DOCUMENT_SUGGESTIONS : GENERAL_SUGGESTIONS;
}
