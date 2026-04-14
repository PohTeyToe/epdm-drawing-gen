import { Search, Plus, Filter } from "lucide-react";
import type { DisciplineOption } from "../lib/types";

interface TopBarProps {
  search: string;
  onSearch: (value: string) => void;
  discipline: string;
  onDiscipline: (value: string) => void;
  disciplines: DisciplineOption[];
  onGenerate: () => void;
  total: number;
}

export function TopBar({
  search,
  onSearch,
  discipline,
  onDiscipline,
  disciplines,
  onGenerate,
  total,
}: TopBarProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center gap-3 justify-between mb-6">
      <div className="flex items-center gap-3 flex-1">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearch(e.target.value)}
            placeholder="Search drawings, IDs, titles..."
            className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/30"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
          <select
            value={discipline}
            onChange={(e) => onDiscipline(e.target.value)}
            className="pl-9 pr-8 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-slate-200 appearance-none focus:outline-none focus:border-amber-500/50"
          >
            <option value="">All disciplines</option>
            {disciplines.map((d) => (
              <option key={d.code} value={d.code}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
        <div className="text-xs text-slate-500 font-mono hidden md:block">
          {total} drawing{total === 1 ? "" : "s"}
        </div>
      </div>
      <button
        onClick={onGenerate}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-amber-500 text-slate-950 font-medium text-sm hover:bg-amber-400 transition-colors shadow-[0_0_20px_rgba(245,158,11,0.2)]"
      >
        <Plus className="w-4 h-4" strokeWidth={2.5} />
        Generate New
      </button>
    </div>
  );
}
