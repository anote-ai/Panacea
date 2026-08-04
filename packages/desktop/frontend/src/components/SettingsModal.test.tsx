import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SettingsModal from "./SettingsModal";
import * as api from "../api";

vi.mock("../api", () => ({
  getProviderKeys: vi.fn(),
  setProviderKey: vi.fn(),
  deleteProviderKey: vi.fn(),
}));

describe("SettingsModal", () => {
  beforeEach(() => {
    vi.mocked(api.getProviderKeys).mockResolvedValue({});
    vi.mocked(api.setProviderKey).mockResolvedValue("sk-a...23z9");
    vi.mocked(api.deleteProviderKey).mockResolvedValue(undefined);
  });

  it("renders nothing when closed", () => {
    render(<SettingsModal open={false} onClose={() => {}} />);
    expect(screen.queryByText("API keys")).not.toBeInTheDocument();
  });

  it("loads provider status and saves a new key", async () => {
    const user = userEvent.setup();
    render(<SettingsModal open onClose={() => {}} />);

    expect(await screen.findByText("Anthropic (Claude)")).toBeInTheDocument();

    await user.click(screen.getAllByText("Set")[0]);
    await user.type(screen.getByPlaceholderText("Enter API key…"), "sk-ant-test-key");
    await user.click(screen.getByText("Save"));

    await waitFor(() =>
      expect(api.setProviderKey).toHaveBeenCalledWith("anthropic", "sk-ant-test-key")
    );
    expect(await screen.findByText("sk-a...23z9")).toBeInTheDocument();
  });
});
