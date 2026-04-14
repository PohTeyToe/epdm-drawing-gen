import { Sun } from "lucide-react";

export function Header() {
  return (
    <header className="relative border-b border-slate-800 bg-slate-950">
      <div className="absolute inset-0 grid-paper opacity-60" aria-hidden="true" />
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-amber-500/40 to-transparent" />
      <div className="relative max-w-[1400px] mx-auto px-8 py-10 flex items-center gap-4">
        <div className="flex items-center justify-center w-12 h-12 rounded-md bg-amber-500/10 border border-amber-500/30 shadow-[0_0_30px_rgba(245,158,11,0.15)]">
          <Sun className="w-6 h-6 text-amber-400" strokeWidth={1.5} />
        </div>
        <div>
          <div className="text-[11px] uppercase tracking-[0.2em] text-amber-500/80 font-mono">
            Morgan Solar / EPDM Vault
          </div>
          <h1 className="text-3xl font-semibold text-slate-100 tracking-tight">
            Drawing Registry
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Engineering drawing numbers issued against the ProductionVault.
          </p>
        </div>
      </div>
    </header>
  );
}
