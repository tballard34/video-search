import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HelloWorld from "../HelloWorld";

describe("HelloWorld", () => {
  it("renders video search title", () => {
    render(<HelloWorld />);

    expect(screen.getByText("Video Search")).toBeInTheDocument();
    expect(screen.getByText("Search and explore video content with semantic embeddings.")).toBeInTheDocument();
  });

  it("displays technology stack badges", () => {
    render(<HelloWorld />);

    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
    expect(screen.getByText("Vite")).toBeInTheDocument();
    expect(screen.getByText("Tailwind CSS")).toBeInTheDocument();
    expect(screen.getByText("shadcn/ui")).toBeInTheDocument();
  });

  it("renders a search icon", () => {
    render(<HelloWorld />);

    const searchIcon = document.querySelector("svg");
    expect(searchIcon).toBeInTheDocument();
  });
});
