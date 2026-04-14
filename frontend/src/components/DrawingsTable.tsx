import { useMemo } from "react";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { motion } from "framer-motion";
import { ArrowUpDown, ArrowUp, ArrowDown, ExternalLink } from "lucide-react";
import type { Drawing } from "../lib/types";

interface Props {
  drawings: Drawing[];
  sorting: SortingState;
  onSortingChange: (s: SortingState) => void;
  onRowClick: (drawing: Drawing) => void;
}

const disciplineColors: Record<string, string> = {
  E: "bg-amber-500/10 text-amber-300 border-amber-500/30",
  M: "bg-sky-500/10 text-sky-300 border-sky-500/30",
  S: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
  O: "bg-fuchsia-500/10 text-fuchsia-300 border-fuchsia-500/30",
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
}

export function DrawingsTable({ drawings, sorting, onSortingChange, onRowClick }: Props) {
  const columns = useMemo<ColumnDef<Drawing>[]>(
    () => [
      {
        accessorKey: "id",
        header: "Drawing ID",
        cell: (info) => (
          <span className="font-mono text-amber-300/90 text-sm">
            {info.getValue() as string}
          </span>
        ),
      },
      {
        accessorKey: "title",
        header: "Title",
        cell: (info) => (
          <span className="text-slate-200">{info.getValue() as string}</span>
        ),
      },
      {
        accessorKey: "discipline",
        header: "Discipline",
        cell: (info) => {
          const code = info.getValue() as string;
          const name = (info.row.original as Drawing).discipline_name;
          return (
            <span
              className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium border ${
                disciplineColors[code] ?? "bg-slate-800 text-slate-300 border-slate-700"
              }`}
            >
              <span className="font-mono">{code}</span>
              <span className="opacity-70">{name.slice(0, 1) + name.slice(1).toLowerCase()}</span>
            </span>
          );
        },
      },
      {
        accessorKey: "revision",
        header: "Rev",
        cell: (info) => (
          <span className="font-mono text-sm text-slate-300">{info.getValue() as string}</span>
        ),
      },
      {
        accessorKey: "drawing_type",
        header: "Type",
        cell: (info) => (
          <span className="text-slate-400 text-sm">{info.getValue() as string}</span>
        ),
      },
      {
        accessorKey: "sequence",
        header: "Seq",
        cell: (info) => (
          <span className="font-mono text-xs text-slate-500">
            {String(info.getValue() as number).padStart(4, "0")}
          </span>
        ),
      },
      {
        accessorKey: "created_at",
        header: "Created",
        cell: (info) => (
          <span className="text-slate-400 text-sm font-mono">
            {formatDate(info.getValue() as string)}
          </span>
        ),
      },
      {
        id: "actions",
        header: "",
        cell: () => (
          <ExternalLink className="w-4 h-4 text-slate-600 group-hover:text-amber-400 transition-colors" />
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data: drawings,
    columns,
    state: { sorting },
    onSortingChange: (updater) => {
      const next = typeof updater === "function" ? updater(sorting) : updater;
      onSortingChange(next);
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/40 backdrop-blur-sm">
      <div className="overflow-x-auto scrollbar-thin">
        <table className="w-full">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id} className="border-b border-slate-800 bg-slate-950/60">
                {hg.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const sortDir = header.column.getIsSorted();
                  return (
                    <th
                      key={header.id}
                      onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                      className={`px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400 ${
                        canSort ? "cursor-pointer select-none hover:text-amber-300" : ""
                      }`}
                    >
                      <span className="inline-flex items-center gap-1">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {canSort &&
                          (sortDir === "asc" ? (
                            <ArrowUp className="w-3 h-3" />
                          ) : sortDir === "desc" ? (
                            <ArrowDown className="w-3 h-3" />
                          ) : (
                            <ArrowUpDown className="w-3 h-3 opacity-30" />
                          ))}
                      </span>
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row, idx) => (
              <motion.tr
                key={row.id}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.18, delay: idx * 0.012 }}
                onClick={() => onRowClick(row.original)}
                className="group border-b border-slate-800/50 hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3 text-sm">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
