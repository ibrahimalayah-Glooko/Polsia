import { render, screen } from "@testing-library/react";
import { PanelCard } from "@/components/dashboard/PanelCard";

describe("PanelCard", () => {
  it("renders title and children", () => {
    render(<PanelCard title="Tasks">Hello</PanelCard>);
    expect(screen.getByText("Tasks")).toBeInTheDocument();
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  it("renders a link when linkHref is provided", () => {
    render(
      <PanelCard title="Tasks" linkHref="/tasks" linkLabel="Manage Tasks">
        content
      </PanelCard>
    );
    const link = screen.getByText("Manage Tasks");
    expect(link).toHaveAttribute("href", "/tasks");
  });

  it("does not render a link when linkHref is omitted", () => {
    render(<PanelCard title="Tasks">content</PanelCard>);
    expect(screen.queryByText("View all")).not.toBeInTheDocument();
  });
});
