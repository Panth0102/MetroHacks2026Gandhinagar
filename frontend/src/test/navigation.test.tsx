import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SidebarContent } from "@/components/layout/sidebar";
import { NAV_ITEMS } from "@/components/layout/nav";
import { renderWithProviders } from "./utils";

describe("navigation", () => {
  it("renders a link for every primary nav item", () => {
    renderWithProviders(<SidebarContent />);
    for (const item of NAV_ITEMS) {
      const link = screen.getByRole("link", { name: new RegExp(item.label, "i") });
      expect(link).toHaveAttribute("href", item.to);
    }
  });
});
