"use client";

import { useState } from "react";
import { Website, api } from "@/lib/api";

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return (
    new Date(iso).toLocaleString("en-US", {
      timeZone: "America/Chicago",
      dateStyle: "medium",
      timeStyle: "short",
    }) + " CT"
  );
}

export default function WebsiteTable({
  websites,
  onChange,
}: {
  websites: Website[];
  onChange: () => void;
}) {
  const [busyId, setBusyId] = useState<number | null>(null);

  const handleCheck = async (id: number) => {
    setBusyId(id);
    try {
      await api.checkWebsite(id);
      onChange();
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Remove this website from monitoring?")) return;
    setBusyId(id);
    try {
      await api.deleteWebsite(id);
      onChange();
    } finally {
      setBusyId(null);
    }
  };

  if (websites.length === 0) {
    return <p className="text-foreground/60">No websites yet. Add one to get started.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-left border-b border-border text-foreground/60">
            <th className="py-2 pr-4 font-medium">Name</th>
            <th className="py-2 pr-4 font-medium">URL</th>
            <th className="py-2 pr-4 font-medium">Last modified (detected)</th>
            <th className="py-2 pr-4 font-medium">Last checked</th>
            <th className="py-2 pr-4 font-medium">Last changed</th>
            <th className="py-2 pr-4"></th>
          </tr>
        </thead>
        <tbody>
          {websites.map((w) => (
            <tr key={w.id} className="border-b border-border hover:bg-surface-muted/60">
              <td className="py-2 pr-4 font-medium">{w.name}</td>
              <td className="py-2 pr-4">
                <a
                  href={w.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-500 hover:text-blue-400 underline"
                >
                  {w.url}
                </a>
              </td>
              <td className="py-2 pr-4">{w.last_modified_text || "—"}</td>
              <td className="py-2 pr-4">{formatDate(w.last_checked_at)}</td>
              <td className="py-2 pr-4">{formatDate(w.last_changed_at)}</td>
              <td className="py-2 pr-4">
                <div className="flex gap-3">
                  <button
                    className="text-blue-500 hover:text-blue-400 disabled:opacity-50"
                    disabled={busyId === w.id}
                    onClick={() => handleCheck(w.id)}
                  >
                    Check now
                  </button>
                  <button
                    className="text-red-500 hover:text-red-400 disabled:opacity-50"
                    disabled={busyId === w.id}
                    onClick={() => handleDelete(w.id)}
                  >
                    Remove
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
