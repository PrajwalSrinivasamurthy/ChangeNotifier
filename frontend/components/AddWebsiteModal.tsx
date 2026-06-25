"use client";

import { useState } from "react";
import { api } from "@/lib/api";

type Row = { url: string; name: string };

export default function AddWebsiteModal({
  open,
  onClose,
  onAdded,
}: {
  open: boolean;
  onClose: () => void;
  onAdded: () => void;
}) {
  const [rows, setRows] = useState<Row[]>([{ url: "", name: "" }]);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  const updateRow = (i: number, field: keyof Row, value: string) => {
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, [field]: value } : r)));
  };

  const addRow = () => setRows((prev) => [...prev, { url: "", name: "" }]);
  const removeRow = (i: number) => setRows((prev) => prev.filter((_, idx) => idx !== i));

  const submit = async () => {
    setError(null);
    const valid = rows.filter((r) => r.url.trim());
    if (valid.length === 0) {
      setError("Enter at least one URL");
      return;
    }
    setSubmitting(true);
    try {
      for (const r of valid) {
        await api.addWebsite(r.url.trim(), r.name.trim() || undefined);
      }
      setRows([{ url: "", name: "" }]);
      onAdded();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to add website");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-surface text-foreground border border-border rounded-xl p-6 w-full max-w-lg space-y-4 shadow-xl">
        <h2 className="text-lg font-semibold">Add website(s) to monitor</h2>
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {rows.map((row, i) => (
            <div key={i} className="flex gap-2">
              <input
                className="border border-border bg-background text-foreground rounded-lg px-3 py-1.5 flex-1 placeholder:text-foreground/40 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com"
                value={row.url}
                onChange={(e) => updateRow(i, "url", e.target.value)}
              />
              <input
                className="border border-border bg-background text-foreground rounded-lg px-3 py-1.5 w-32 placeholder:text-foreground/40 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Name (optional)"
                value={row.name}
                onChange={(e) => updateRow(i, "name", e.target.value)}
              />
              {rows.length > 1 && (
                <button
                  className="text-red-500 px-2 hover:text-red-400"
                  onClick={() => removeRow(i)}
                  aria-label="Remove row"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </div>
        <button className="text-sm text-blue-500 hover:text-blue-400" onClick={addRow}>
          + Add another URL
        </button>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <button
            className="px-3 py-1.5 rounded-lg border border-border hover:bg-surface-muted"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
            onClick={submit}
            disabled={submitting}
          >
            {submitting ? "Adding..." : "Add"}
          </button>
        </div>
      </div>
    </div>
  );
}
