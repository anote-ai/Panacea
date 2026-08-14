import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../App";
import { API_BASE_URL } from "../constants/constants";

interface SessionInfo {
  status: string | null;
  amountTotal: number | null;
  currency: string | null;
  kind: string | null;
  plan: string | null;
  credits: number | null;
}

// The Stripe webhook that actually credits the account arrives async, on
// Stripe's own schedule, and can land after this page has already rendered
// — so a single refreshUser() call often reads stale plan/credits. Poll
// briefly until the profile reflects the purchase (or give up).
const PROFILE_POLL_ATTEMPTS = 8;
const PROFILE_POLL_INTERVAL_MS = 1500;

function formatAmount(amountTotal: number | null, currency: string | null): string {
  if (amountTotal == null) return "";
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: (currency || "usd").toUpperCase(),
  });
  return formatter.format(amountTotal / 100);
}

export default function CheckoutResultPage() {
  const { token, user, refreshUser } = useAuth();
  const [searchParams] = useSearchParams();
  const status = searchParams.get("checkout");
  const sessionId = searchParams.get("session_id");

  const [session, setSession] = useState<SessionInfo | null>(null);
  const [loading, setLoading] = useState(status === "success" && !!sessionId);
  const [error, setError] = useState("");
  const baselineRef = useRef<{ plan: string; credits: number } | null>(null);

  useEffect(() => {
    if (status !== "success" || !sessionId || !token) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await axios.get(
          `${API_BASE_URL}/api/payments/checkout/session/${sessionId}`,
          { headers: { Authorization: `Bearer ${token}` } },
        );
        if (!cancelled) setSession(res.data);
      } catch (err: any) {
        if (!cancelled) {
          setError(err?.response?.data?.error || "Unable to load purchase details.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, sessionId, token]);

  // Snapshot the pre-purchase plan/credits once, then poll until they move.
  useEffect(() => {
    if (!session || baselineRef.current || !user) return;
    baselineRef.current = { plan: user.plan, credits: user.credits };
  }, [session, user]);

  useEffect(() => {
    if (!session) return;
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts += 1;
      refreshUser();
      const baseline = baselineRef.current;
      const reflected =
        !baseline ||
        (session.kind === "credit_pack"
          ? baseline.credits !== user?.credits
          : session.kind === "subscription"
          ? baseline.plan !== user?.plan
          : true);
      if (reflected || attempts >= PROFILE_POLL_ATTEMPTS) clearInterval(interval);
    }, PROFILE_POLL_INTERVAL_MS);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session]);

  const isSuccess = status === "success";

  return (
    <div className="min-h-screen flex items-center justify-center bg-white dark:bg-[#212121] px-4">
      <div className="w-full max-w-md rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#2F2F2F] p-8 text-center shadow-sm">
        {isSuccess ? (
          <>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/40 text-green-600 dark:text-green-400 text-2xl">
              ✓
            </div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Payment successful
            </h1>
            {loading && (
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Loading purchase details...
              </p>
            )}
            {!loading && error && (
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Your payment went through, but we couldn't load the details.
              </p>
            )}
            {!loading && !error && session && (
              <div className="mt-3 text-sm text-gray-600 dark:text-gray-300">
                {session.amountTotal != null && (
                  <p>
                    You were charged{" "}
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatAmount(session.amountTotal, session.currency)}
                    </span>
                    .
                  </p>
                )}
                {session.kind === "credit_pack" && session.credits && (
                  <p className="mt-1">
                    {session.credits.toLocaleString()} credits have been added to your account.
                  </p>
                )}
                {session.kind === "subscription" && session.plan && (
                  <p className="mt-1">
                    Your account has been upgraded to the{" "}
                    <span className="font-medium capitalize">{session.plan}</span> plan.
                  </p>
                )}
              </div>
            )}
            <Link
              to="/app"
              className="mt-6 inline-block rounded-lg bg-black dark:bg-white text-white dark:text-black px-4 py-2 text-sm font-medium hover:opacity-90"
            >
              Back to Chat
            </Link>
          </>
        ) : (
          <>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-2xl">
              ✕
            </div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Checkout cancelled
            </h1>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              No charge was made. You can restart checkout anytime from Settings.
            </p>
            <Link
              to="/app"
              className="mt-6 inline-block rounded-lg bg-black dark:bg-white text-white dark:text-black px-4 py-2 text-sm font-medium hover:opacity-90"
            >
              Back to Chat
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
