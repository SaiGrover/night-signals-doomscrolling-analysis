import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import axe from "axe-core";
import RiskDemo from "./RiskDemo";

afterEach(() => vi.restoreAllMocks());

test("renders the validation warning before any prediction", () => {
  render(<RiskDemo />);
  expect(screen.getByText(/not medical advice/i)).toBeInTheDocument();
  expect(screen.getByText(/No prediction has been made/i)).toBeInTheDocument();
});

test("has no automatically detectable accessibility violations", async () => {
  const { container } = render(<RiskDemo />);
  // jsdom has no canvas implementation, so visual contrast is verified in browser QA.
  expect((await axe.run(container, { rules: { "color-contrast": { enabled: false } } })).violations).toHaveLength(0);
});

test("announces a successful prediction", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ probability: .62, risk_band: "higher", threshold: .32, model_version: "2.0.0" }) }));
  render(<RiskDemo />); fireEvent.click(screen.getByRole("button", { name: /estimate risk/i }));
  await waitFor(() => expect(screen.getByText("62%")).toBeInTheDocument());
  expect(screen.getByText(/higher estimated risk/i)).toBeInTheDocument();
});
