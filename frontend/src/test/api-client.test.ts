import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, api } from "@/lib/api-client";

describe("api-client", () => {
  afterEach(() => vi.restoreAllMocks());

  it("parses a successful JSON response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    );
    const data = await api.get<{ ok: boolean }>("/x");
    expect(data.ok).toBe(true);
  });

  it("builds query strings and omits empty params", async () => {
    const spy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response("[]", { status: 200 }));
    await api.get("/items", { station_id: 3, status: undefined, q: "" });
    expect(spy.mock.calls[0]?.[0]).toContain("/items?station_id=3");
    expect(spy.mock.calls[0]?.[0]).not.toContain("status");
  });

  it("throws ApiError with backend detail on 4xx", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Station not found" }), { status: 404 }),
    );
    await expect(api.get("/stations/999")).rejects.toMatchObject({
      status: 404,
      message: "Station not found",
    });
  });

  it("reports an unreachable backend as status 0", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));
    const err = (await api.get("/x").catch((e) => e)) as ApiError;
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(0);
  });
});
