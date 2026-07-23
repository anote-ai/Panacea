import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    window.localStorage.clear();
    delete (window as any).electronAPI;
    window.history.pushState({}, "", "/");
  });

  it("redirects an unauthenticated user to the login page", async () => {
    render(<App />);
    expect(await screen.findByText(/welcome back/i)).toBeInTheDocument();
  });
});
