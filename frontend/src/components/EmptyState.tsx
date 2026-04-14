import { AlertCircle, RefreshCw } from "lucide-react";

interface Props {
  title: string;
  message: string;
  onRetry?: () => void;
  showBackendHint?: boolean;
}

export function EmptyState({ title, message, onRetry, showBackendHint }: Props) {
  return (
    <div className="border border-dashed border-slate-800 rounded-lg py-16 px-6 text-center">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/30 mb-4">
        <AlertCircle className="w-5 h-5 text-amber-400" />
      </div>
      <h3 className="text-slate-200 font-medium mb-1">{title}</h3>
      <p className="text-slate-400 text-sm max-w-md mx-auto">{message}</p>
      {showBackendHint && (
        <p className="text-slate-500 text-xs mt-3 font-mono">
          uvicorn api.main:app --port 8003 --reload
        </p>
      )}
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 mt-5 px-3 py-1.5 rounded-md border border-slate-700 text-sm text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry
        </button>
      )}
    </div>
  );
}
