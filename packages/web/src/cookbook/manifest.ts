export interface CookbookRecipe {
  slug: string;
  name: string;
  group: "platform";
  runnable: boolean;
}

// Mirrors Cookbook/README.md's recipe table. Content lives in ./recipes/<slug>.md,
// copied verbatim from the Cookbook repo.
export const COOKBOOK_RECIPES: CookbookRecipe[] = [
  { slug: "03-panacea-document-qa-rag", name: "Document Q&A + RAG", group: "platform", runnable: false },
  { slug: "04-panacea-multi-agent-orchestration", name: "Multi-Agent Orchestration", group: "platform", runnable: false },
  { slug: "05-panacea-ai-coding-toolchain", name: "AI Coding Toolchain", group: "platform", runnable: false },
  { slug: "06-panacea-multimodal-ingestion", name: "Multi-Modal Ingestion", group: "platform", runnable: false },
  { slug: "07-panacea-openai-compatible-gateway", name: "OpenAI-Compatible Gateway", group: "platform", runnable: false },
  { slug: "08-panacea-billing-and-api-keys", name: "Billing & API Keys", group: "platform", runnable: false },
  { slug: "09-panacea-mcp-tool-server", name: "MCP Tool Server", group: "platform", runnable: false },
  { slug: "10-panacea-messaging-bots", name: "Multi-Channel Messaging Bots", group: "platform", runnable: false },
];

const recipeSources = import.meta.glob("./recipes/*.md", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

export function getRecipeContent(slug: string): string {
  return recipeSources[`./recipes/${slug}.md`] ?? "";
}
