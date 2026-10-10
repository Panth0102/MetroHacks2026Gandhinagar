import { afterEach, describe, expect, it, vi } from "vitest";

import { downloadCsv } from "@/lib/csv";

describe("downloadCsv", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("serializes rows with headers and escapes special characters", () => {
    const parts: BlobPart[][] = [];
    class FakeBlob {
      constructor(p: BlobPart[]) {
        parts.push(p);
      }
    }
    vi.stubGlobal("Blob", FakeBlob);
    vi.stubGlobal("URL", { createObjectURL: () => "blob:mock", revokeObjectURL: () => {} });
    const clickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => {});

    downloadCsv(
      "test.csv",
      [
        { key: "a", header: "Col A" },
        { key: "b", header: "Col B" },
      ],
      [{ a: "plain", b: 'has,comma "quote"' }],
    );

    const text = String(parts[0]?.[0] ?? "");
    expect(text).toContain("Col A,Col B");
    expect(text).toContain('"has,comma ""quote"""');
    expect(clickSpy).toHaveBeenCalled();
  });
});
