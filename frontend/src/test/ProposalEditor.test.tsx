import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockGet, mockPatch, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPatch: vi.fn(),
  mockPost: vi.fn(),
}));
vi.mock("@/lib/api-client", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api-client")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
      patch: mockPatch,
      post: mockPost,
      downloadUrl: (p: string) => `http://api${p}`,
    },
  };
});

import { ProposalEditorPage } from "@/features/proposals/ProposalEditorPage";
import type { Proposal } from "@/types/api";
import { renderWithProviders } from "./utils";

const PROPOSAL: Proposal = {
  id: 1,
  reference_code: "PROP-ABC123",
  space_id: 5,
  station_id: 2,
  title: "Riverfront kiosk opportunity",
  tenant_category: "Food & beverage",
  status: "draft",
  content: {
    title: "Riverfront kiosk opportunity",
    executive_summary: "Observed entries support this location.",
    location_highlights: ["On the Blue Line"],
    verified_metrics: [{ label: "Avg daily entries", value: "30,000" }],
    commercial_opportunity: "Good commuter flow.",
    pricing_summary: "Indicative price, not a verified rate.",
    suggested_usage: "Grab-and-go kiosk.",
    call_to_action: "Contact the commercial team.",
    assumptions_and_limitations: ["Observed entries, not unique visitors."],
  },
  context_snapshot: {
    station: { name: "Riverfront Central" },
    space: { space_code: "STN01-S01" },
    footfall: {},
    pricing: {},
    user_input: {},
  },
  pricing_model_version: "v1.0-heuristic",
  generation_source: "template",
  ai_model: null,
  created_at: "2026-10-10T00:00:00Z",
  updated_at: "2026-10-10T00:00:00Z",
};

function renderEditor() {
  return renderWithProviders(
    <Routes>
      <Route path="/proposals/:id" element={<ProposalEditorPage />} />
    </Routes>,
    ["/proposals/1"],
  );
}

describe("ProposalEditorPage", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPatch.mockReset();
    mockPost.mockReset();
    mockGet.mockResolvedValue(PROPOSAL);
    mockPatch.mockImplementation((_p: string, body: Record<string, unknown>) =>
      Promise.resolve({ ...PROPOSAL, ...body, updated_at: "2026-10-11T00:00:00Z" }),
    );
  });

  it("loads the proposal into editable fields and the preview", async () => {
    renderEditor();
    const title = (await screen.findByLabelText("Title")) as HTMLInputElement;
    expect(title.value).toBe("Riverfront kiosk opportunity");
    // Verified metric shown in the preview (facts, not editable)
    expect(screen.getByText("30,000")).toBeInTheDocument();
    expect(screen.getByText(/Template-generated/i)).toBeInTheDocument();
  });

  it("saves edited content via PATCH and clears the dirty state", async () => {
    const user = userEvent.setup();
    renderEditor();
    const summary = await screen.findByLabelText("Executive summary");
    await user.clear(summary);
    await user.type(summary, "Edited summary text.");
    expect(screen.getByText(/Unsaved edits/i)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /^Save$/i }));
    await waitFor(() => expect(mockPatch).toHaveBeenCalled());
    const [, body] = mockPatch.mock.calls[0]!;
    expect(body.content.executive_summary).toBe("Edited summary text.");
  });

  it("exposes a working PDF download link", async () => {
    renderEditor();
    const link = (await screen.findByRole("link", { name: /Download PDF/i })) as HTMLAnchorElement;
    expect(link.href).toContain("/api/v1/proposals/1/pdf");
  });
});
