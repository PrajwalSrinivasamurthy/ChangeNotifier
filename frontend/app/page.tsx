"use client";

import { useCallback, useEffect, useState } from "react";
import { Website, api } from "@/lib/api";
import AddWebsiteModal from "@/components/AddWebsiteModal";
import WebsiteTable from "@/components/WebsiteTable";
import SettingsPanel from "@/components/SettingsPanel";
import ThemeToggle from "@/components/ThemeToggle";

export default function Home() {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const w = await api.listWebsites();
    setWebsites(w);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="max-w-5xl mx-auto p-8 space-y-8">
      <ThemeToggle />
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Webpage Change Notifier</h1>
          <p className="text-sm text-foreground/60 mt-1">
            Get an SMS the moment a monitored page changes.
          </p>
        </div>
        <button
          className="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
          onClick={() => setModalOpen(true)}
        >
          + Add website
        </button>
      </div>

      <section className="bg-surface border border-border rounded-xl p-5">
        <h2 className="text-lg font-semibold mb-3">Monitored websites</h2>
        {loading ? (
          <p className="text-foreground/60">Loading...</p>
        ) : (
          <WebsiteTable websites={websites} onChange={refresh} />
        )}
      </section>

      <section className="bg-surface border border-border rounded-xl p-5">
        <SettingsPanel />
      </section>

      <AddWebsiteModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onAdded={refresh}
      />
    </div>
  );
}
