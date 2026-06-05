import { createFileRoute } from "@tanstack/react-router";
import { useState, type ComponentType, type FormEvent } from "react";
import { TbArrowRight, TbChevronDown } from "react-icons/tb";

import { ClaudeIcon, GeminiIcon, OpenAIIcon } from "@/components/ModelIcons";

type AgentModel = {
  id: string;
  label: string;
  Icon: ComponentType<{ className?: string }>;
  iconClassName: string;
};

const models: AgentModel[] = [
  {
    id: "gpt-5-5",
    label: "GPT-5.5",
    Icon: OpenAIIcon,
    iconClassName: "h-4 w-4 text-gray-950",
  },
  {
    id: "claude-4-8",
    label: "Claude 4.8",
    Icon: ClaudeIcon,
    iconClassName: "h-4 w-4",
  },
  {
    id: "gemini-3-1-pro",
    label: "Gemini 3.1 Pro",
    Icon: GeminiIcon,
    iconClassName: "h-4 w-4",
  },
];

export const Route = createFileRoute("/agent")({
  component: AgentPage,
});

function AgentPage() {
  const [prompt, setPrompt] = useState("");
  const [selectedModel, setSelectedModel] = useState<AgentModel>(models[0]!);
  const [isModelMenuOpen, setIsModelMenuOpen] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPrompt("");
  }

  const SelectedIcon = selectedModel.Icon;

  return (
    <div className="flex h-full flex-col bg-background">
      <header className="border-b border-border bg-surface px-8 py-5">
        <h1 className="text-2xl font-bold text-foreground">Agent</h1>
      </header>

      <div className="flex min-h-0 flex-1 flex-col px-5 py-8 sm:px-8">
        <div className="flex min-h-0 flex-1 items-center justify-center pb-44">
          <p className="text-center text-base font-medium text-gray-400">Send a message to start the conversation.</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="mx-auto w-full max-w-4xl rounded-2xl border border-border bg-surface p-4 shadow-sm shadow-gray-950/5 transition focus-within:border-gray-300 focus-within:shadow-lg focus-within:shadow-gray-950/10"
        >
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            className="h-28 w-full resize-none bg-transparent px-1 text-lg text-foreground outline-none placeholder:text-gray-400"
            placeholder="Ask about your videos"
          />

          <div className="mt-4 flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsModelMenuOpen((isOpen) => !isOpen)}
                  className="inline-flex h-10 items-center gap-2 rounded-xl px-3 text-sm font-medium text-gray-700 transition hover:bg-gray-100 hover:text-gray-950"
                >
                  <SelectedIcon className={selectedModel.iconClassName} />
                  <span className="max-w-36 truncate">{selectedModel.label}</span>
                  <TbChevronDown size={16} className="text-gray-400" />
                </button>

                {isModelMenuOpen && (
                  <div className="absolute bottom-full left-0 z-10 mb-2 w-56 overflow-hidden rounded-2xl border border-border bg-surface p-1 shadow-xl shadow-gray-950/10">
                    {models.map((model) => {
                      const ModelIcon = model.Icon;

                      return (
                        <button
                          key={model.id}
                          type="button"
                          onClick={() => {
                            setSelectedModel(model);
                            setIsModelMenuOpen(false);
                          }}
                          className={`flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm transition ${
                            selectedModel.id === model.id ? "bg-gray-100 text-gray-950" : "text-gray-600 hover:bg-gray-50 hover:text-gray-950"
                          }`}
                        >
                          <ModelIcon className={model.iconClassName} />
                          <span className="truncate">{model.label}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={!prompt.trim()}
              className="inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gray-950 text-white transition hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400"
              aria-label="Send message"
            >
              <TbArrowRight size={22} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
