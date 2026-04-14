import { useCallback, useEffect, useMemo, useState } from "react";
import { Toaster, toast } from "react-hot-toast";
import type { SortingState } from "@tanstack/react-table";
import { Header } from "./components/Header";
import { TopBar } from "./components/TopBar";
import { DrawingsTable } from "./components/DrawingsTable";
import { GenerateModal } from "./components/GenerateModal";
import { DrawingDrawer } from "./components/DrawingDrawer";
import { EmptyState } from "./components/EmptyState";
import {
  generateDrawing,
  listDisciplines,
  listDrawings,
  listDrawingTypes,
} from "./lib/api";
import type { Drawing, DisciplineOption, GenerateRequest } from "./lib/types";

export default function App() {
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [total, setTotal] = useState(0);
  const [disciplines, setDisciplines] = useState<DisciplineOption[]>([]);
  const [drawingTypes, setDrawingTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [discipline, setDiscipline] = useState("");
  const [sorting, setSorting] = useState<SortingState>([{ id: "created_at", desc: true }]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selected, setSelected] = useState<Drawing | null>(null);

  const loadMeta = useCallback(async () => {
    try {
      const [d, t] = await Promise.all([listDisciplines(), listDrawingTypes()]);
      setDisciplines(d);
      setDrawingTypes(t);
    } catch {
      // handled by load()
    }
  }, []);

  const sortParams = useMemo(() => {
    const s = sorting[0];
    if (!s) return { sort_by: "created_at", descending: true };
    return { sort_by: s.id, descending: s.desc };
  }, [sorting]);

  const load = useCallback(async () => {
    setLoading(true);
    setApiError(null);
    try {
      const res = await listDrawings({
        page: 1,
        size: 200,
        sort_by: sortParams.sort_by,
        descending: sortParams.descending,
        discipline: discipline || undefined,
        search: search || undefined,
      });
      setDrawings(res.items);
      setTotal(res.total);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Unable to reach the API.");
      setDrawings([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [sortParams, discipline, search]);

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  useEffect(() => {
    const t = setTimeout(load, 150);
    return () => clearTimeout(t);
  }, [load]);

  const handleGenerate = async (req: GenerateRequest) => {
    try {
      const drawing = await generateDrawing(req);
      toast.success(`Generated ${drawing.id}`);
      setModalOpen(false);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Generate failed");
    }
  };

  const showingEmpty = !loading && drawings.length === 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: "#0f172a",
            color: "#e2e8f0",
            border: "1px solid #1e293b",
            fontSize: "14px",
          },
        }}
      />
      <Header />

      <main className="max-w-[1400px] mx-auto px-8 py-8">
        {apiError && (
          <div className="mb-6 flex items-start gap-3 px-4 py-3 rounded-md bg-amber-500/5 border border-amber-500/30">
            <div className="text-amber-300 text-sm flex-1">
              <div className="font-medium">Backend unreachable.</div>
              <div className="text-amber-200/70 text-xs mt-0.5">
                Start the API locally with{" "}
                <code className="font-mono">uvicorn api.main:app --port 8003 --reload</code> or
                set <code className="font-mono">VITE_API_URL</code> at build time.
              </div>
            </div>
            <button
              onClick={load}
              className="px-3 py-1 text-xs rounded border border-amber-500/40 text-amber-300 hover:bg-amber-500/10"
            >
              Retry
            </button>
          </div>
        )}

        <TopBar
          search={search}
          onSearch={setSearch}
          discipline={discipline}
          onDiscipline={setDiscipline}
          disciplines={disciplines}
          onGenerate={() => setModalOpen(true)}
          total={total}
        />

        {loading && drawings.length === 0 ? (
          <div className="border border-slate-800 rounded-lg py-20 text-center text-slate-500 text-sm">
            Loading drawings...
          </div>
        ) : showingEmpty ? (
          <EmptyState
            title={apiError ? "Can't reach the backend" : "No drawings match"}
            message={
              apiError
                ? "The drawing registry API isn't responding."
                : "Try clearing the filters or generate a new drawing."
            }
            onRetry={apiError ? load : undefined}
            showBackendHint={!!apiError}
          />
        ) : (
          <DrawingsTable
            drawings={drawings}
            sorting={sorting}
            onSortingChange={setSorting}
            onRowClick={setSelected}
          />
        )}
      </main>

      <GenerateModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        disciplines={disciplines}
        drawingTypes={drawingTypes}
        onSubmit={handleGenerate}
      />

      <DrawingDrawer drawing={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
