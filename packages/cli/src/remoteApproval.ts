/**
 * Remote approval — lets a risky tool call pause and be approved or denied from a
 * different surface (Slack, mobile, web) via the backend's /api/approvals primitive,
 * instead of blocking on someone being at this terminal.
 *
 * Fails closed: any error reaching the backend, or a timeout, denies the tool call
 * rather than silently allowing it.
 */

export interface RemoteApprovalConfig {
  enabled?: boolean;
  backendUrl?: string;
  /** Tool names that must be remotely approved before running, e.g. ["Bash"]. */
  requireFor?: string[];
  pollIntervalMs?: number;
  timeoutMs?: number;
}

export interface ApprovalDecision {
  approved: boolean;
  reason: string;
}

const DEFAULT_BACKEND_URL = "http://localhost:5000";
const DEFAULT_POLL_INTERVAL_MS = 3000;
const DEFAULT_TIMEOUT_MS = 10 * 60 * 1000;

export class RemoteApprovalClient {
  constructor(
    private readonly config: RemoteApprovalConfig,
    private readonly sessionId: string
  ) {}

  requiresApproval(toolName: string): boolean {
    return Boolean(this.config.enabled) && (this.config.requireFor ?? []).includes(toolName);
  }

  async requestApproval(toolName: string, input: unknown): Promise<ApprovalDecision> {
    const backendUrl = this.config.backendUrl ?? DEFAULT_BACKEND_URL;
    const timeoutMs = this.config.timeoutMs ?? DEFAULT_TIMEOUT_MS;
    const pollIntervalMs = this.config.pollIntervalMs ?? DEFAULT_POLL_INTERVAL_MS;

    let approvalId: string;
    try {
      const createResp = await fetch(`${backendUrl}/api/approvals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          action: toolName,
          detail: safeStringify(input),
          ttl_seconds: Math.ceil(timeoutMs / 1000),
        }),
      });
      if (!createResp.ok) {
        return {
          approved: false,
          reason: `Approvals backend returned ${createResp.status}; denying by default`,
        };
      }
      approvalId = ((await createResp.json()) as { id: string }).id;
    } catch (err) {
      return {
        approved: false,
        reason: `Could not reach approvals backend (${(err as Error).message}); denying by default`,
      };
    }

    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      await sleep(pollIntervalMs);
      try {
        const resp = await fetch(`${backendUrl}/api/approvals/${approvalId}`);
        if (!resp.ok) continue;
        const body = (await resp.json()) as { status: string; responder?: string | null };
        if (body.status === "approved") {
          return { approved: true, reason: `Approved by ${body.responder ?? "remote"}` };
        }
        if (body.status === "denied") {
          return { approved: false, reason: `Denied by ${body.responder ?? "remote"}` };
        }
        if (body.status === "expired") {
          return { approved: false, reason: "Approval request expired before anyone responded" };
        }
        // status === "pending" — keep polling
      } catch {
        // transient network error while polling; keep trying until the deadline
      }
    }
    return { approved: false, reason: "Timed out waiting for remote approval" };
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function safeStringify(input: unknown): string {
  try {
    return JSON.stringify(input).slice(0, 2000);
  } catch {
    return String(input);
  }
}
