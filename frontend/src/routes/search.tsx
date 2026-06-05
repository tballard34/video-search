import { createFileRoute } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { TbArrowRight, TbSearch } from "react-icons/tb";

export const Route = createFileRoute("/search")({
  component: SearchPage,
});

function SearchPage() {
  const [query, setQuery] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
  }

  return (
    <div className="flex h-full flex-col bg-background">
      <header className="border-b border-border bg-surface px-8 py-5">
        <h1 className="text-2xl font-bold text-foreground">Search</h1>
      </header>

      <div className="flex min-h-0 flex-1 items-center justify-center px-6">
        <form onSubmit={handleSubmit} className="w-full max-w-3xl">
          <div className="flex items-center gap-4 rounded-2xl border border-border bg-surface px-5 py-4 shadow-sm shadow-gray-950/5 transition focus-within:border-gray-300 focus-within:shadow-lg focus-within:shadow-gray-950/10">
            <TbSearch size={24} className="flex-shrink-0 text-gray-400" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="min-w-0 flex-1 bg-transparent text-lg text-foreground outline-none placeholder:text-gray-400"
              placeholder="Search anything in your videos"
            />
            <button
              type="submit"
              disabled={!query.trim()}
              className="inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gray-950 text-white transition hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400"
              aria-label="Search"
            >
              <TbArrowRight size={22} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
