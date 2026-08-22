import { render, screen, act, fireEvent } from "@testing-library/react";
import { ChatPanel } from "@/components/dashboard/ChatPanel";

jest.mock("@/lib/api", () => ({
  api: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

import { api } from "@/lib/api";
const mockApiPost = api.post as jest.MockedFunction<typeof api.post>;
const mockApiGet = api.get as jest.MockedFunction<typeof api.get>;

describe("ChatPanel", () => {
  beforeEach(() => {
    mockApiPost.mockReset();
    mockApiGet.mockReset();
  });

  it("renders the initial assistant greeting", () => {
    render(<ChatPanel />);
    expect(screen.getByText(/tell me to build you a website/i)).toBeInTheDocument();
  });

  it("sends a message and displays the orchestrator's completed reply", async () => {
    mockApiPost.mockResolvedValue({ status: "queued", task_id: 7 });
    mockApiGet.mockResolvedValue({ status: "completed", result_summary: "Here is your plan.", error_message: null });

    render(<ChatPanel />);
    const input = screen.getByPlaceholderText("Ask Polsia anything…");

    fireEvent.change(input, { target: { value: "What should I focus on?" } });
    await act(async () => {
      fireEvent.click(screen.getByText("Send"));
      await new Promise((r) => setTimeout(r, 3100));
    });

    expect(mockApiPost).toHaveBeenCalledWith(
      "/agents/orchestrator/trigger",
      expect.objectContaining({ task_description: "What should I focus on?" })
    );
    expect(screen.getByText("What should I focus on?")).toBeInTheDocument();
    expect(screen.getByText("Here is your plan.")).toBeInTheDocument();
  });

  it("routes website-building requests to the code_generation agent", async () => {
    mockApiPost.mockResolvedValue({ status: "queued", task_id: 8 });
    mockApiGet.mockResolvedValue({
      status: "completed",
      result_summary: "Built and published a website at http://localhost/sites/acme/",
      error_message: null,
    });

    render(<ChatPanel />);
    const input = screen.getByPlaceholderText("Ask Polsia anything…");

    fireEvent.change(input, { target: { value: "Build me a website for my coffee shop" } });
    await act(async () => {
      fireEvent.click(screen.getByText("Send"));
      await new Promise((r) => setTimeout(r, 3100));
    });

    expect(mockApiPost).toHaveBeenCalledWith(
      "/agents/code_generation/trigger",
      expect.objectContaining({ task_description: "Build me a website for my coffee shop" })
    );
  });

  it("shows an error message when the trigger call fails", async () => {
    mockApiPost.mockRejectedValue(new Error("network down"));

    render(<ChatPanel />);
    const input = screen.getByPlaceholderText("Ask Polsia anything…");
    fireEvent.change(input, { target: { value: "hello" } });

    await act(async () => {
      fireEvent.click(screen.getByText("Send"));
    });

    expect(screen.getByText(/Error: Error: network down/)).toBeInTheDocument();
  });
});
