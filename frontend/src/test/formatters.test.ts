import { describe, expect, it } from "vitest";

import {
  formatCurrency,
  formatHour,
  formatNumber,
  formatPercent,
  labelSpaceType,
} from "@/lib/formatters";

describe("formatters", () => {
  it("formats INR currency without decimals", () => {
    expect(formatCurrency("58952")).toContain("58,952");
    expect(formatCurrency(45000)).toContain("45,000");
  });

  it("returns an em dash for missing values", () => {
    expect(formatCurrency(null)).toBe("—");
    expect(formatNumber(null)).toBe("—");
    expect(formatPercent(null)).toBe("—");
    expect(formatHour(null)).toBe("—");
  });

  it("formats percentages from a fraction", () => {
    expect(formatPercent(0.2857)).toBe("28.6%");
  });

  it("formats hours in 12-hour clock", () => {
    expect(formatHour(0)).toBe("12:00 AM");
    expect(formatHour(13)).toBe("1:00 PM");
    expect(formatHour(18)).toBe("6:00 PM");
  });

  it("labels space types for humans", () => {
    expect(labelSpaceType("advertising_panel")).toBe("Advertising panel");
    expect(labelSpaceType("unknown_type")).toBe("unknown_type");
  });
});
