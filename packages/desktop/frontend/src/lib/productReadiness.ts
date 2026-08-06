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
  providers?: {
    anthropic?: boolean;
    openai?: boolean;
    google?: boolean;
    ollama?: boolean;
  };
  warnings?: string[];
}

export interface StatusNotice {
  title: string;
  detail: string;
  tone: "warning" | "error";
}

export interface WorkspaceStatusItem {
  label: string;
  value: string;
  detail: string;
  tone: "good" | "warning" | "error" | "neutral";
}

export type ModelProvider = "anthropic" | "openai" | "google" | "ollama";

const REPORTING_SUGGESTIONS = [
  "Draft a concise product status update I can use in today's work report.",
  "List the biggest risks, blockers, and next steps for this project.",
  "Summarize the key changes in this codebase in plain English.",
  "Turn this work into stakeholder-ready talking points.",
] as const;

function getModelSetupDetail(model: string): string {
  const provider = getProviderForModel(model);
  if (provider === "ollama") {
    return `Start Ollama locally and make sure the ${model} model is installed, or switch to a cloud model with a configured provider key.`;
  }
  return "Switch to a configured model, add the matching provider key, or run Ollama locally before sending a message.";
}

export function getAuthStatusNotice(
  healthState: HealthFetchState,
  health: ServiceHealth | null,
): StatusNotice | null {
  if (healthState === "offline") {
    return {
      title: "Local service unavailable",
      detail: "Start the desktop backend and refresh. Sign-in and chat need the local service running.",
      tone: "error",
    };
  }

  if (healthState !== "online") return null;

  if (health?.checks?.aiProviderConfigured === false) {
    return {
      title: "Model provider still needs setup",
      detail:
        "Account access works locally, but responses will not stream until you add a provider key or run Ollama on this device.",
      tone: "warning",
    };
  }

  if (health?.readiness === "degraded") {
    return {
      title: "Workspace running with limited configuration",
      detail: "Core desktop flows are available, but some optional integrations still need setup.",
      tone: "warning",
    };
  }

  return null;
}

export function getChatStatusNotice(
  healthState: HealthFetchState,
  health: ServiceHealth | null,
  model: string,
): StatusNotice | null {
  const authNotice = getAuthStatusNotice(healthState, health);
  if (authNotice?.tone === "error") return authNotice;
  if (!isModelConfigured(health, model)) {
    return {
      title: `${getProviderLabel(getProviderForModel(model))} setup needed for the selected model`,
      detail: getModelSetupDetail(model),
      tone: "warning",
    };
  }
  return authNotice;
}

export function getEmptyStateSuggestions(): readonly string[] {
  return REPORTING_SUGGESTIONS;
}

export function getWorkspaceStatusItems(
  healthState: HealthFetchState,
  health: ServiceHealth | null,
  model: string,
): WorkspaceStatusItem[] {
  const backendItem: WorkspaceStatusItem =
    healthState === "online"
      ? {
          label: "Backend",
          value: "Online",
          detail: "The local API is responding and ready for sign-in, chat history, and streaming.",
          tone: "good",
        }
      : healthState === "loading"
        ? {
            label: "Backend",
            value: "Checking",
            detail: "Verifying the local service before you start a conversation.",
            tone: "neutral",
          }
        : {
            label: "Backend",
            value: "Offline",
            detail: "Start the local backend to enable sign-in and chat.",
            tone: "error",
          };

  const providerReady = isModelConfigured(health, model);
  const providerLabel = getProviderLabel(getProviderForModel(model));
  const providerItem: WorkspaceStatusItem = providerReady
    ? {
        label: "Selected model",
        value: "Ready",
        detail: `${providerLabel} is configured for the model currently selected in the desktop workspace.`,
        tone: "good",
      }
    : {
        label: "Selected model",
        value: "Setup needed",
        detail: getModelSetupDetail(model),
        tone: "warning",
      };

  return [
    backendItem,
    providerItem,
    {
      label: "Privacy",
      value: "On-device",
      detail: "This desktop flow keeps the interface and stored workspace data local to this machine.",
      tone: "neutral",
    },
  ];
}

export function getProviderForModel(model: string): ModelProvider {
  if (model.startsWith("claude")) return "anthropic";
  if (model.startsWith("gpt")) return "openai";
  if (model.startsWith("gemini")) return "google";
  return "ollama";
}

export function getProviderLabel(provider: ModelProvider): string {
  switch (provider) {
    case "anthropic":
      return "Anthropic";
    case "openai":
      return "OpenAI";
    case "google":
      return "Google";
    case "ollama":
      return "Ollama";
  }
}

export function isModelConfigured(health: ServiceHealth | null, model: string): boolean {
  const provider = getProviderForModel(model);
  return Boolean(health?.providers?.[provider]);
}
