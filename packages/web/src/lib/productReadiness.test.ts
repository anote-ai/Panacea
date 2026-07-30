import { describe, expect, it } from "vitest";
import {
  getAuthStatusNotice,
  getEmptyStateSuggestions,
} from "./productReadiness";

describe("productReadiness helpers", () => {
  it("returns an offline auth notice when health checks fail", () => {
    expect(getAuthStatusNotice("offline", null)).toEqual({
      title: "Service unavailable",
      detail:
        "We couldn't reach the app service. If you're previewing locally, start the backend and refresh.",
      tone: "error",
    });
  });

  it("prefers a Google auth notice when Google sign-in is not configured", () => {
    expect(
      getAuthStatusNotice("online", {
        status: "ok",
        service: "anote-backend",
        readiness: "degraded",
        checks: { googleAuthConfigured: false },
      }),
    ).toEqual({
      title: "Google sign-in unavailable",
      detail:
        "Email and password sign-in still work. Add the Google OAuth environment variables to enable it.",
      tone: "warning",
    });
  });

  it("returns document-first prompts when documents are attached", () => {
    expect(getEmptyStateSuggestions(true)[0]).toContain("attached documents");
    expect(getEmptyStateSuggestions(false)[0]).toContain("project");
  });
});
