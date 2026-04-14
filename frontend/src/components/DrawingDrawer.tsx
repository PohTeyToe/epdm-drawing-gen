import { AnimatePresence, motion } from "framer-motion";
import { X, FileText, HardDrive, Calendar, Hash } from "lucide-react";
import type { Drawing } from "../lib/types";

interface Props {
  drawing: Drawing | null;
  onClose: () => void;
}

export function DrawingDrawer({ drawing, onClose }: Props) {
  return (
    <AnimatePresence>
      {drawing && (
        <>
          <motion.div
            key="drawer-backdrop"
            className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            key="drawer"
            className="fixed top-0 right-0 h-full w-full max-w-xl z-50 bg-slate-900 border-l border-slate-800 shadow-2xl overflow-y-auto scrollbar-thin"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 260 }}
          >
            <div className="flex items-start justify-between px-6 py-5 border-b border-slate-800">
              <div>
                <div className="text-[11px] uppercase tracking-[0.2em] text-amber-500/80 font-mono">
                  Drawing Detail
                </div>
                <div className="mt-1 font-mono text-xl text-amber-300">{drawing.id}</div>
                <div className="mt-0.5 text-slate-300">{drawing.title}</div>
              </div>
              <button
                onClick={onClose}
                className="text-slate-500 hover:text-slate-200 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="px-6 py-5 space-y-6">
              <Section title="Preview">
                <SvgPreview drawing={drawing} />
              </Section>

              <Section title="Metadata">
                <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
                  <Meta icon={<Hash className="w-3.5 h-3.5" />} label="Prefix" value={drawing.prefix} />
                  <Meta
                    icon={<Hash className="w-3.5 h-3.5" />}
                    label="Discipline"
                    value={`${drawing.discipline_name} (${drawing.discipline})`}
                  />
                  <Meta
                    icon={<Hash className="w-3.5 h-3.5" />}
                    label="Sequence"
                    value={String(drawing.sequence).padStart(4, "0")}
                    mono
                  />
                  <Meta
                    icon={<Hash className="w-3.5 h-3.5" />}
                    label="Revision"
                    value={drawing.revision}
                    mono
                  />
                  <Meta
                    icon={<FileText className="w-3.5 h-3.5" />}
                    label="Type"
                    value={drawing.drawing_type}
                  />
                  <Meta
                    icon={<Calendar className="w-3.5 h-3.5" />}
                    label="Created"
                    value={new Date(drawing.created_at).toLocaleString()}
                    mono
                  />
                </dl>
              </Section>

              <Section title="Vault Path">
                <div className="flex items-start gap-2 bg-slate-950/70 border border-slate-800 rounded-md px-3 py-2.5 font-mono text-xs text-slate-300 break-all">
                  <HardDrive className="w-3.5 h-3.5 text-slate-500 mt-0.5 shrink-0" />
                  {drawing.vault_path}
                </div>
              </Section>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h3 className="text-[11px] uppercase tracking-wider font-semibold text-slate-500 mb-2">
        {title}
      </h3>
      {children}
    </section>
  );
}

function Meta({
  icon,
  label,
  value,
  mono,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="flex items-center gap-1 text-[11px] uppercase tracking-wider text-slate-500 mb-0.5">
        {icon}
        {label}
      </dt>
      <dd className={mono ? "font-mono text-slate-200" : "text-slate-200"}>{value}</dd>
    </div>
  );
}

function SvgPreview({ drawing }: { drawing: Drawing }) {
  return (
    <div className="relative aspect-[4/3] bg-slate-950 border border-slate-800 rounded-md overflow-hidden">
      <svg
        viewBox="0 0 400 300"
        className="absolute inset-0 w-full h-full"
        preserveAspectRatio="none"
      >
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" strokeWidth="0.5" />
          </pattern>
          <pattern id="gridmajor" width="100" height="100" patternUnits="userSpaceOnUse">
            <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#334155" strokeWidth="0.8" />
          </pattern>
        </defs>
        <rect width="400" height="300" fill="url(#grid)" />
        <rect width="400" height="300" fill="url(#gridmajor)" />
        <rect
          x="40"
          y="30"
          width="320"
          height="210"
          fill="none"
          stroke="#475569"
          strokeWidth="1"
        />
        <g opacity="0.6">
          <circle cx="200" cy="130" r="40" fill="none" stroke="#f59e0b" strokeWidth="1.2" />
          <circle cx="200" cy="130" r="20" fill="none" stroke="#f59e0b" strokeWidth="1" />
          <line x1="150" y1="130" x2="250" y2="130" stroke="#f59e0b" strokeWidth="0.8" />
          <line x1="200" y1="80" x2="200" y2="180" stroke="#f59e0b" strokeWidth="0.8" />
        </g>
        <text
          x="200"
          y="220"
          textAnchor="middle"
          fill="#64748b"
          fontSize="9"
          fontFamily="monospace"
        >
          PLACEHOLDER VIEW / NOT TO SCALE
        </text>
      </svg>

      {/* Stamp box bottom-right */}
      <div className="absolute bottom-3 right-3 bg-slate-950/95 border border-amber-500/40 rounded-sm">
        <div className="px-3 py-1.5 border-b border-amber-500/20">
          <div className="text-[8px] uppercase tracking-wider text-amber-500/80 font-mono">
            Drawing No.
          </div>
          <div className="font-mono text-sm text-amber-300">{drawing.id}</div>
        </div>
        <div className="px-3 py-1 flex items-center gap-3 text-[9px] font-mono text-slate-400">
          <span>
            REV <span className="text-slate-200">{drawing.revision}</span>
          </span>
          <span>{drawing.drawing_type.toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
}
