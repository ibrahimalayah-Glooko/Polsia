import { render, screen, act, fireEvent } from "@testing-library/react";
import { AgentTriggerButton } from "@/components/dashboard/AgentTriggerButton";

jest.mock("@/lib/api", () => ({
  api: {
    post: jest.fn(),
  },
}));

import { api } from "@/lib/api";
const mockApiPost = api.post as jest.MockedFunction<typeof api.post>;

describe("AgentTriggerButton", () => {
  beforeEach(() => {
    mockApiPost.mockReset();
  });

  it("renders the label", () => {
    render(<AgentTriggerButton agentType="social_media" label="Tweet" />);
    expect(screen.getByText("Tweet")).toBeInTheDocument();
  });

  it("shows the queued task id after a successful trigger", async () => {
    mockApiPost.mockResolvedValue({ status: "queued", task_id: 42 });
    render(<AgentTriggerButton agentType="social_media" label="Tweet" />);

    await act(async () => {
      fireEvent.click(screen.getByText("Tweet"));
    });

    expect(mockApiPost).toHaveBeenCalledWith("/agents/social_media/trigger", expect.any(Object));
    expect(screen.getByText("Queued task #42")).toBeInTheDocument();
  });

  it("shows an error message when the trigger fails", async () => {
    mockApiPost.mockRejectedValue(new Error("boom"));
    render(<AgentTriggerButton agentType="ads_management" label="Ads" />);

    await act(async () => {
      fireEvent.click(screen.getByText("Ads"));
    });

    expect(screen.getByText("Failed to queue")).toBeInTheDocument();
  });
});
