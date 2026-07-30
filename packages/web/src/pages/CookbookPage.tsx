import { Link, useNavigate, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import RocketLogo from "../components/RocketLogo";
import { useTheme } from "../App";
import { COOKBOOK_RECIPES, getRecipeContent } from "../cookbook/manifest";

const GROUPS: { id: "platform"; label: string }[] = [
  { id: "platform", label: "Panacea platform" },
];

export default function CookbookPage() {
  const { slug } = useParams<{ slug: string }>();
  const nav = useNavigate();
  const { dark, toggle } = useTheme();

  const active = COOKBOOK_RECIPES.find((r) => r.slug === slug) || COOKBOOK_RECIPES[0];
  const content = getRecipeContent(active.slug);

  return (
    <div className="flex h-screen bg-white dark:bg-[#212121] text-gray-900 dark:text-white">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 bg-[#F7F7F8] dark:bg-[#171717] flex flex-col">
        <Link to="/" className="p-3 flex items-center gap-2 hover:bg-gray-200 dark:hover:bg-[#2F2F2F] rounded-lg m-1">
          <RocketLogo className="w-7 h-7 flex-shrink-0" />
          <span className="font-semibold text-sm truncate">Cookbook</span>
        </Link>

        <div className="flex-1 overflow-y-auto px-2 pb-3 space-y-4">
          {GROUPS.map((group) => (
            <div key={group.id}>
              <p className="px-3 pt-3 pb-1 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                {group.label}
              </p>
              <div className="space-y-0.5">
                {COOKBOOK_RECIPES.filter((r) => r.group === group.id).map((r) => (
                  <button
                    key={r.slug}
                    onClick={() => nav(`/cookbook/${r.slug}`)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center justify-between gap-2 transition-colors ${
                      r.slug === active.slug
                        ? "bg-gray-200 dark:bg-[#2F2F2F]"
                        : "hover:bg-gray-200 dark:hover:bg-[#2F2F2F]"
                    }`}
                  >
                    <span className="truncate">{r.name}</span>
                    <span
                      className={`flex-shrink-0 text-[10px] font-medium px-1.5 py-0.5 rounded-full border ${
                        r.runnable
                          ? "border-gray-400 dark:border-gray-500 text-gray-600 dark:text-gray-300"
                          : "border-gray-300 dark:border-gray-600 text-gray-400 dark:text-gray-500"
                      }`}
                    >
                      {r.runnable ? "Run" : "Guide"}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="p-3 border-t border-gray-200 dark:border-gray-700">
          <Link
            to="/"
            className="block px-3 py-2 rounded-lg text-sm text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-[#2F2F2F]"
          >
            &larr; Back to Panacea
          </Link>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Cookbook / {active.name}
          </span>
          <button
            onClick={toggle}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-[#2F2F2F] text-gray-500 dark:text-gray-400"
            aria-label="Toggle dark mode"
          >
            {dark ? "☀️" : "🌙"}
          </button>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-8">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
