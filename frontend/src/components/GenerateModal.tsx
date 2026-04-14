import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Zap } from "lucide-react";
import type { DisciplineOption, GenerateRequest } from "../lib/types";

interface Props {
  open: boolean;
  onClose: () => void;
  disciplines: DisciplineOption[];
  drawingTypes: string[];
  onSubmit: (req: GenerateRequest) => Promise<void>;
}

const REVISIONS = ["A", "B", "C", "D", "E", "F"];

export function GenerateModal({ open, onClose, disciplines, drawingTypes, onSubmit }: Props) {
  const [projectCode, setProjectCode] = useState("MS");
  const [discipline, setDiscipline] = useState<string>("E");
  const [revision, setRevision] = useState("A");
  const [drawingType, setDrawingType] = useState<string>("Assembly");
  const [title, setTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        project_code: projectCode.toUpperCase(),
        discipline: discipline as GenerateRequest["discipline"],
        revision,
        drawing_type: drawingType,
        title: title || undefined,
      });
      setTitle("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            key="backdrop"
            className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            key="modal"
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <motion.div
              className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-lg shadow-2xl pointer-events-auto"
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
            >
              <div className="flex items-start justify-between px-6 pt-5 pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-400" />
                  <h2 className="text-base font-semibold text-slate-100">
                    Generate Drawing Number
                  </h2>
                </div>
                <button
                  onClick={onClose}
                  className="text-slate-500 hover:text-slate-200 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
                <Field label="Project Code">
                  <input
                    value={projectCode}
                    onChange={(e) => setProjectCode(e.target.value.slice(0, 4))}
                    minLength={2}
                    maxLength={4}
                    required
                    pattern="[A-Za-z0-9]{2,4}"
                    className="input"
                  />
                </Field>

                <div className="grid grid-cols-2 gap-4">
                  <Field label="Discipline">
                    <select
                      value={discipline}
                      onChange={(e) => setDiscipline(e.target.value)}
                      className="input"
                    >
                      {disciplines.map((d) => (
                        <option key={d.code} value={d.code}>
                          {d.name}
                        </option>
                      ))}
                    </select>
                  </Field>

                  <Field label="Revision">
                    <select
                      value={revision}
                      onChange={(e) => setRevision(e.target.value)}
                      className="input"
                    >
                      {REVISIONS.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                  </Field>
                </div>

                <Field label="Drawing Type">
                  <select
                    value={drawingType}
                    onChange={(e) => setDrawingType(e.target.value)}
                    className="input"
                  >
                    {drawingTypes.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </Field>

                <Field label="Title (optional)">
                  <input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Combiner Box Wiring"
                    className="input"
                  />
                </Field>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-3 py-2 text-sm text-slate-400 hover:text-slate-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-amber-500 text-slate-950 text-sm font-medium hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submitting ? "Generating..." : "Generate"}
                  </button>
                </div>
              </form>

              <style>{`
                .input {
                  width: 100%;
                  background: #0f172a;
                  border: 1px solid #1e293b;
                  border-radius: 6px;
                  padding: 0.5rem 0.75rem;
                  color: #e2e8f0;
                  font-size: 0.875rem;
                  outline: none;
                  transition: border-color 0.12s;
                }
                .input:focus {
                  border-color: rgba(245, 158, 11, 0.5);
                  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.3);
                }
              `}</style>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-[11px] uppercase tracking-wider font-medium text-slate-400 mb-1.5">
        {label}
      </span>
      {children}
    </label>
  );
}
